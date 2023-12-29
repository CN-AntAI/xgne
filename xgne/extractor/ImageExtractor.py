import logging
import urllib.parse
from copy import copy
import re
from typing import List, Optional
from PIL import Image, ImageFile
import requests
from lxml.html import Element

from ..defaults import META_IMAGE_TAGS, TOP_IMAGE_SETTINGS
from ..parsers import Parser
from ..utils import urljoin_if_valid, url_to_filetype, get_requests_params

log = logging.getLogger(__name__)


class ImageExtractor:
    """文章中的图片提取器，用于获取顶部图片、图片列表、网站图标等。"""

    def __init__(self):
        self.parser = Parser()
        self.top_image: Optional[str] = None
        self.meta_image: Optional[str] = None
        self.images: List[str] = []
        self.favicon: Optional[str] = None
        self._chunksize = 1024

    def extractor(
            self, doc: Element, top_node: Element, article_url: str
    ) -> None:
        """从文档中提取图片的主要方法。

        Args:
            doc (Element): 文档元素
            top_node (Element): 顶部节点
            article_url (str): 文章链接
        """
        self.favicon = self._get_favicon(doc)

        self.meta_image = self._get_meta_image(doc)
        if self.meta_image:
            self.meta_image = urljoin_if_valid(article_url, self.meta_image)
        self.images = [
            urljoin_if_valid(article_url, u)
            for u in self._get_images(doc)
            if u and u.strip()
        ]
        self.top_image = self._get_top_image(doc, top_node, article_url)

    def _get_favicon(self, doc: Element) -> str:
        """从网站中提取图标，参考 http://en.wikipedia.org/wiki/Favicon
        <link rel="shortcut icon" type="image/png" href="favicon.png" />
        <link rel="icon" type="image/png" href="favicon.png" />
        """
        kwargs = {"tag": "link", "attr": "rel", "value": "icon"}
        meta = self.parser.getElementsByTag(doc, **kwargs)
        if meta:
            favicon = self.parser.getAttribute(meta[0], "href")
            return favicon
        return ""

    def _get_meta_field(self, doc: Element, field: str) -> str:
        """从文档中提取给定的 meta 字段。"""
        metafield = self.parser.css_select(doc, field)
        if metafield:
            return metafield[0].get("content", "").strip()
        return ""

    def _get_meta_image(self, doc: Element) -> str:
        """从文档中获取可能的图片标签。"""
        candidates = []
        for elem in META_IMAGE_TAGS:
            if elem["tag"] == "meta":
                candidates.append(
                    (self._get_meta_field(doc, elem["field"]), elem["score"])
                )
            else:
                img = self.parser.getElementsByTag(
                    doc,
                    attr=elem["attr"],
                    value=elem["value"],
                    use_regex=("|" in elem["value"]),
                )
                if img:
                    candidates.append((img[0].get("href"), elem["score"]))
        candidates = [c for c in candidates if c[0]]

        candidates.sort(key=lambda x: x[1], reverse=True)

        return candidates[0][0] if candidates else ""

    def _get_images(self, doc: Element) -> List[str]:
        """从文档中获取所有图片的链接。"""
        images = [
            x.get("src")
            for x in self.parser.getElementsByTag(doc, tag="img")
            if x.get("src")
        ]

        return images

    def _get_top_image(
            self, doc: Element, top_node: Element, article_url: str
    ) -> str:
        """获取顶部图片链接。"""

        def node_distance(node1, node2):
            path1 = node1.getroottree().getpath(node1).split("/")
            path2 = node2.getroottree().getpath(node2).split("/")
            for i, (step1, step2) in enumerate(zip(path1, path2)):
                if step1 != step2:
                    return len(path1[i:]) + len(path2[i:])

            return abs(len(path1) - len(path2))

        if self.meta_image:
            if self._check_image_size(
                    self.meta_image, article_url
            ):
                return self.meta_image

        img_cand = []
        for img in self.parser.getElementsByTag(doc, tag="img"):
            if not img.get("src"):
                continue
            if img.get("src").startswith("data:"):
                continue

            if top_node is not None:
                distance = node_distance(top_node, img)
                img_cand.append((img, distance))
            else:
                if self._check_image_size(img.get("src"), article_url):
                    return img.get("src")

        img_cand.sort(key=lambda x: x[1])

        for img in img_cand:
            if self._check_image_size(img[0].get("src"), article_url):
                return img[0].get("src")

        return ""

    def _check_image_size(self, url: str, referer: Optional[str]) -> bool:
        """检查图片的尺寸是否符合设定的要求。"""
        img = self._fetch_image(
            url,
            referer,
        )
        if not img:
            return False

        width, height = img.size

        if TOP_IMAGE_SETTINGS["min_width"] > width:
            return False
        if TOP_IMAGE_SETTINGS["min_height"] > height:
            return False
        if TOP_IMAGE_SETTINGS["min_area"] > width * height:
            return False

        if (
                re.search(r"(logo|sprite)", url, re.IGNORECASE)
                and TOP_IMAGE_SETTINGS["min_area"] > width * height / 10
        ):
            return False

        return True

    def _fetch_image(self, url: str, referer: Optional[str]) -> Optional[Image.Image]:
        """从给定的 URL 获取图片，并检查是否符合要求。"""

        def clean_url(url):
            """将 URL 中的 Unicode 数据进行编码"""
            if not isinstance(url, str):
                return url

            url = url.encode("utf8")
            url = "".join(
                [
                    urllib.parse.quote(c) if ord(c) >= 127 else c
                    for c in url.decode("utf-8")
                ]
            )
            return url

        requests_params = copy(get_requests_params())
        requests_params["headers"]["Referer"] = referer
        max_retries = TOP_IMAGE_SETTINGS["max_retries"]

        cur_try = 0
        url = clean_url(url)
        if not url or not url.startswith(("http://", "https://")):
            return None

        response = None
        while True:
            try:
                response = requests.get(
                    url,
                    stream=True,
                    **requests_params,
                )

                content_type = response.headers.get("Content-Type")

                if not content_type or "image" not in content_type.lower():
                    return None

                p = ImageFile.Parser()
                new_data = response.raw.read(self._chunksize)
                while not p.image and new_data:
                    try:
                        p.feed(new_data)
                    except (IOError, ValueError) as e:
                        log.warning(
                            "在获取图片时发生错误 %s: %s 来源: %s",
                            str(e),
                            url,
                            requests_params["headers"].get("Referer"),
                        )
                        return None
                    except Exception as e:
                        # 对于一些 favicon.ico 图片，图片很小，
                        # 导致我们的 PIL feed() 方法无法通过长度测试。
                        is_favicon = url_to_filetype(url) == "ico"
                        if not is_favicon:
                            raise e
                        return None
                    new_data = response.raw.read(self._chunksize)
                return p.image
            except requests.exceptions.RequestException:
                cur_try += 1
                if cur_try >= max_retries:
                    log.warning(
                        "在获取图片时发生错误: %s 来源: %s",
                        url,
                        requests_params["headers"].get("Referer"),
                    )
                    return None
            finally:
                if response is not None:
                    response.raw.close()
                    if response.raw._connection:
                        response.raw._connection.close()

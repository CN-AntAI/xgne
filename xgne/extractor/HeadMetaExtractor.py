import re

from lxml.html import HtmlElement, Element
from collections import Counter

from ..defaults import META_IMAGE_TAGS
from ..parsers import Parser


class HeadMetaExtractor:
    def __init__(self):
        # 定义用于匹配 URL 的正则表达式
        # self.url_pattern = re.compile(r'https?://\S+')
        self.url_pattern = re.compile(r'https?://[^\s/]+')
        self.parser = Parser()

    def extract_host(self, head_meta):
        # 提取所有可能的 host
        potential_hosts = []
        for key, value in head_meta.items():
            # 使用正则表达式检查值是否是有效的 URL
            matches = self.url_pattern.findall(value)
            for match in matches:
                potential_hosts.append(match)

        # 如果有有效的 host，选择出现次数最多的作为最终的 host
        if potential_hosts:
            most_common_host = Counter(potential_hosts).most_common(1)[0][0]
            return most_common_host
        else:
            return None

    def extractor(self, element: HtmlElement):
        # 选择包含 meta 元素的标签
        meta_tags = element.xpath('//head/meta')

        # 遍历每个 meta 元素
        head_meta = {}
        for tag in meta_tags:
            # 获取 meta 元素的属性
            property_value = tag.get('property')
            name_value = tag.get('name')
            content_value = tag.get('content')

            # 构建字典
            if property_value and content_value:
                head_meta[property_value] = content_value
            elif name_value and content_value:
                head_meta[name_value] = content_value
        # 提取 host
        host = self.extract_host(head_meta)

        # 将 host 添加到 head_meta 中
        head_meta['host'] = host
        head_meta['top_image'] = self._get_meta_image(element)

        return head_meta

    def _get_meta_image(self, element: Element) -> str:
        """从文档中获取可能的图片标签。"""
        candidates = []
        for elem in META_IMAGE_TAGS:
            if elem["tag"] == "meta":
                candidates.append(
                    (self._get_meta_field(element, elem["field"]), elem["score"])
                )
            else:
                img = self.parser.getElementsByTag(
                    element,
                    attr=elem["attr"],
                    value=elem["value"],
                    use_regex=("|" in elem["value"]),
                )
                if img:
                    candidates.append((img[0].get("href"), elem["score"]))
        candidates = [c for c in candidates if c[0]]

        candidates.sort(key=lambda x: x[1], reverse=True)

        return candidates[0][0] if candidates else ""

    def _get_meta_field(self, element: Element, field: str) -> str:
        """从文档中提取给定的 meta 字段。"""
        metafield = self.parser.css_select(element, field)
        if metafield:
            return metafield[0].get("content", "").strip()
        return ""

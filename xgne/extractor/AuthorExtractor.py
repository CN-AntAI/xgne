import re
from copy import deepcopy
from typing import List, Union
from collections import OrderedDict

from lxml.html import HtmlElement

from ..utils import config
from ..parsers import Parser
from ..defaults import AUTHOR_PATTERN, AUTHOR_ATTRS, AUTHOR_STOP_WORDS, AUTHOR_VALS


class AuthorExtractor:
    def __init__(self):
        self.author_pattern = AUTHOR_PATTERN
        self.parser = Parser()
        self.authors: List[str] = []

    def extractor(self, element: HtmlElement, author_xpath='') -> List[str]:
        # 如果提供了自定义的作者 XPath，则直接使用该 XPath 进行提取
        author_xpath = author_xpath or config.get('author', {}).get('xpath')
        if author_xpath:
            self.authors = element.xpath(author_xpath)
        # 否则，从文本中提取作者信息
        text = ''.join(element.xpath('.//text()'))
        for pattern in self.author_pattern:
            author_obj = re.search(pattern, text)
            if author_obj:
                self.authors = self.authors + [author_obj.group(0)]
        self.authors = [i.strip() for i in self.authors if i.strip()]
        # 如果未成功提取作者信息，则尝试从 JSON-LD 数据和其他元素中提取
        if not self.authors:
            _digits = re.compile(r"\d")
            author_stopwords_patt = [re.escape(x) for x in AUTHOR_STOP_WORDS]
            author_stopwords = re.compile(
                r"\b(" + "|".join(author_stopwords_patt) + r")\b", flags=re.IGNORECASE
            )

            def contains_digits(d):
                return bool(_digits.search(d))

            def uniqify_list(lst: List[str]) -> List[str]:
                """
                从提供的字符串列表中去除重复项但保持原始顺序。
                忽略末尾空格和大小写。

                Args:
                    lst (List[str]): 输入的字符串列表，可能包含重复项

                Returns:
                    List[str]: 输出的字符串列表，已删除重复项
                """
                seen = OrderedDict()
                for item in lst:
                    seen[item.lower().strip()] = item.strip()
                return [seen[item] for item in seen.keys() if item]

            def parse_byline(search_str):
                """
                解析候选行的 HTML 或文本，并以列表形式提取出名字
                """
                # 移除 HTML 标签
                search_str = re.sub("<[^<]+?>", "", search_str)
                search_str = re.sub("[\n\t\r\xa0]", " ", search_str)

                # 移除原始的 "By" 语句
                m = re.search(r"\b(by|from)[:\s](.*)", search_str, flags=re.IGNORECASE)
                if m:
                    search_str = m.group(2)

                search_str = search_str.strip()

                # 使用非字母数字字符分割行
                name_tokens = re.split(r"[·,\|]|\sand\s|\set\s|\sund\s|/", search_str)
                # 一些合理性检查
                name_tokens = [s.strip() for s in name_tokens if not contains_digits(s)]
                name_tokens = [s for s in name_tokens if 5 > len(re.findall(r"\w+", s)) > 1]

                return name_tokens

            # Try 1: Search popular author tags for authors

            matches = []
            authors = []

            json_ld_scripts = self.parser.get_ld_json_object(element)

            def get_authors(vals):
                if isinstance(vals, dict):
                    if isinstance(vals.get("name"), str):
                        authors.append(vals.get("name"))
                    elif isinstance(vals.get("name"), list):
                        authors.extend(vals.get("name"))
                elif isinstance(vals, list):
                    for val in vals:
                        if isinstance(val, dict):
                            authors.append(val.get("name"))
                        elif isinstance(val, str):
                            authors.append(val)
                elif isinstance(vals, str):
                    authors.append(vals)

            for script_tag in json_ld_scripts:
                if "@graph" in script_tag:
                    g = script_tag.get("@graph", [])
                    for item in g:
                        if not isinstance(item, dict):
                            continue
                        if item.get("@type") == "Person":
                            authors.append(item.get("name"))
                        if "author" in item:
                            get_authors(item["author"])
                else:
                    if "author" in script_tag:
                        get_authors(script_tag["author"])

            def get_text_from_element(node: HtmlElement) -> str:
                """
                从元素中提取文本，包括其子元素的文本
                """
                if node is None:
                    return ""
                if node.tag in ["script", "style", "time"]:
                    return ""

                node = deepcopy(node)
                for tag in ["script", "style", "time"]:
                    for el in node.xpath(f".//{tag}"):
                        el.getparent().remove(el)
                text = list(node.itertext())
                text = " ".join(text)
                return text

            authors = [re.sub("[\n\t\r\xa0]", " ", x) for x in authors if x]
            doc_root = element.getroottree()

            def getpath(node):
                if doc_root is not None:
                    return doc_root.getpath(node)

            # TODO: be more specific, not a combination of all attributes and values
            for attr in AUTHOR_ATTRS:
                for val in AUTHOR_VALS:
                    found = self.parser.get_element_by_attribs(element, attribs={attr: val})
                    matches.extend([(found, getpath(found)) for found in found])

            matches.sort(
                key=lambda x: x[1], reverse=True
            )  # 按 XPath 排序，以获取最特定的匹配项
            matches_reduced = []
            for m in matches:
                if len(matches_reduced) == 0:
                    matches_reduced.append(m)
                elif not matches_reduced[-1][1].startswith(
                        m[1]
                ):  # 移除前一个节点的父节点
                    matches_reduced.append(m)
            matches_reduced.sort(
                key=lambda x: x[1]
            )  # 保留一些作者的排序

            for match, _ in matches_reduced:
                content: Union[str, List] = ""
                if match.tag == "meta":
                    mm = match.xpath("@content")
                    if len(mm) > 0:
                        content = mm[0]
                else:
                    # 忽略 <time> 标签或带有 "on ..." 的标签
                    # 移除 <style> 标签 https://washingtonindependent.com/how-to-apply-for-reseller-permit-in-washington-state/
                    content = get_text_from_element(match)
                if len(content) > 0:
                    authors.extend(parse_byline(content))

            # 输出的字符串列表，已删除重复项
            authors = [re.sub(author_stopwords, "", x).strip(" .,-/") for x in authors]
            self.authors = uniqify_list(authors)
        return self.authors

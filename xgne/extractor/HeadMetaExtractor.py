import re

from lxml.html import HtmlElement
from collections import Counter


class HeadMetaExtractor:
    def __init__(self):
        # 定义用于匹配 URL 的正则表达式
        # self.url_pattern = re.compile(r'https?://\S+')
        self.url_pattern = re.compile(r'https?://[^\s/]+')

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

        return head_meta

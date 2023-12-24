from lxml.html import HtmlElement


class HeadMetaExtractor:

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

        return head_meta
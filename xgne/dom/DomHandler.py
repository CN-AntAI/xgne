# -*- coding: utf-8 -*-

import re
from copy import deepcopy

import lxml.html
from lxml.html import HtmlElement
from lxml.html import etree

from ..defaults import USELESS_TAG, TAGS_CAN_BE_REMOVE_IF_EMPTY, USELESS_ATTR, MAYBEIS, INLINE_TAG
from ..defaults import USELESS_TAG_TO_TIME


class DomHandle:

    # 移除 br 和 /*...*/ 注释
    def remove_annotation(self, html):
        html = re.sub('</?br.*?>', '', html, flags=re.S)
        html = re.sub('<!--.*?-->', '', html, flags=re.S)
        html = re.sub(r'/\*.*?\*/', '', html, flags=re.S)
        return html

    # 构建dom树
    def build_html_element(self, html):
        # element = fromstring(html)
        utf8_parser = lxml.html.HTMLParser(encoding='utf-8')
        element = lxml.html.document_fromstring(html.encode('utf-8', 'replace'), parser=utf8_parser)
        return element

    # 移除无用标签
    def remove_useless_tag(self, element: HtmlElement):
        etree.strip_elements(element, *USELESS_TAG, with_tail=False)
        return element

    # 移除无用标签 保留script
    def remove_useless_tag_time(self, element: HtmlElement):
        etree.strip_elements(element, *USELESS_TAG_TO_TIME, with_tail=False)
        return element

    def iter_node(self, element: HtmlElement):
        yield element
        for sub_element in element:
            if isinstance(sub_element, HtmlElement):
                yield from self.iter_node(sub_element)

    # 删除节点
    def remove_node(self, node: HtmlElement):
        parent = node.getparent()
        if parent is not None:
            # print('删除的标签2----', bytes.decode(tostring(node, encoding='utf-8', pretty_print=False, method='html')))
            parent.remove(node)

    # 仅删除标签
    def drop_tag(self, node: HtmlElement):
        parent = node.getparent()
        if parent is not None:
            # print('删除的标签----', bytes.decode(tostring(node, encoding='utf-8', pretty_print=False, method='html')))
            node.drop_tag()

    # 判断节点是否为空
    def is_empty_element(self, node: HtmlElement):
        return not node.getchildren() and not node.text

    # 标准化节点
    def normalize_node(self, element: HtmlElement, tag):
        for node in self.iter_node(element):
            # ['section', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span']  移除为空的标签
            if node.tag.lower() in TAGS_CAN_BE_REMOVE_IF_EMPTY and self.is_empty_element(node):
                self.remove_node(node)
            # 删除标签(不删文本)
            if node.tag.lower() == 'p':
                etree.strip_tags(node, 'span')
                etree.strip_tags(node, 'strong')
                etree.strip_tags(node, 'font')
            # 不包含子节点的div 改成tagdiv标签 疑似正文标签
            # if node.tag.lower() == 'div' and not node.getchildren():
            #     node.tag = 'tagdiv'

            # 不包含子节点的span 改成p标签
            if tag == 'p' and node.tag.lower() == 'span' and not node.getchildren():
                node.tag = 'p'

            # 删除为空的p标签
            if node.tag.lower() == 'p' and not node.xpath('.//*'):
                if not (node.text and node.text.strip()):
                    self.drop_tag(node)
        return element

    def remove_unlikely_content_tag(self, element: HtmlElement):
        for node in self.iter_node(element):
            id_and_class = '{}{}'.format(node.get('class', ''), node.get('id', ''))
            if id_and_class.strip():
                unlike = '|'.join(USELESS_ATTR)
                maybe = '|'.join(MAYBEIS)
                if re.compile(unlike, re.I).search(id_and_class) and (
                        not re.compile(maybe, re.I).search(id_and_class)) and node.tag not in ['html', 'body']:
                    self.remove_node(node)
        return element

    def remove_noise_node(self, element: HtmlElement, noise_xpath_list):
        if not noise_xpath_list:
            return
        for noise_xpath in noise_xpath_list:
            nodes = element.xpath(noise_xpath)
            for node in nodes:
                self.remove_node(node)
        return element

    def get_text(self, html='', element=None, seg=' ', remove_noise=False, body=False):
        if isinstance(element, HtmlElement):
            selector = deepcopy(element)
        elif html and isinstance(html, str):
            selector = self.build_html_element(html)
            if remove_noise:
                etree.strip_elements(selector, *USELESS_TAG)
        if body:
            text_list = selector.xpath('//body//text()')
        else:
            text_list = selector.xpath('.//text()')
        return seg.join([i.strip() for i in text_list]).strip()

    def remove_inline_tag(self, element):
        elem = deepcopy(element)
        for node in self.iter_node(elem):
            tag_name = node.tag.lower()
            if tag_name in INLINE_TAG:
                # etree.strip_tags(parent, tag_name)
                node.drop_tag()
        return elem

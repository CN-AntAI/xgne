# -*- coding: utf-8 -*-
import re

from lxml.html import HtmlElement, tostring, HTMLParser, document_fromstring

from ..defaults import DATETIME_PATTERN, TIME_TOKEN, DATETIME_PATTERN_COMPARE, RE_SUB_MAP
from ..dom.DomHandler import DomHandle
from ..extractor.ContentExtractor import ContentExtractor
from ..extractor.TitleExtractor import TitleExtractor
from ..utils import normalize_text, html2element, pre_parse


class TimeExtractorFeature:

    def __init__(self):
        self.time_pattern = DATETIME_PATTERN
        self.dom_handler = DomHandle()

    def check_time(self, time_list, text):
        text = '        ' + text
        if time_list and isinstance(time_list, list):
            if len(time_list) > 0:
                for matched_time in time_list:
                    res = re.search(f'(........){matched_time}', text, flags=re.I)
                    if res:
                        time_prefix = res.group(1)
                        if [i for i in TIME_TOKEN if i.lower() in time_prefix.lower()]:
                            return matched_time
                        text = text.replace(matched_time, '', 1)
        return None

    def extract_from_text(self, element, text=None, content=None) -> str:
        if text is None:
            text = self.dom_handler.get_text(element=element, seg=' ', remove_noise=True, body=True)
        # 处理时间
        text = re.sub(r'下午|上午|星期.?', ' ', text)
        text = re.sub(r'\s+', ' ', text)

        for pattern, repl_value in RE_SUB_MAP.items():
            text = re.sub(pattern, repl_value, text, flags=re.I)

        time_list_collect = []
        for dt in DATETIME_PATTERN_COMPARE:
            time_list = re.findall(dt, text, flags=re.S)
            check_result = self.check_time(time_list, text)
            if check_result is None:
                continue
            else:
                return check_result
        if time_list_collect:
            return time_list_collect[0]
        else:
            for dt in self.time_pattern:
                dt_obj = re.search(dt, text, flags=re.I)
                if dt_obj:
                    return dt_obj.group(1)
        return ''

    def extract_time_area(self, title, element, content) -> str:
        if isinstance(element, HtmlElement) and content:
            content_text = self.dom_handler.get_text(content)
            if title in content_text:
                return ''
            else:
                body_text = self.dom_handler.get_text(element=element, remove_noise=True, body=True)
                news_start = content_text[:10] if len(content_text) > 9 else content_text
                if news_start not in body_text:
                    new_html = bytes.decode(tostring(element, encoding='utf-8', pretty_print=False, method='html'))
                    utf8_parser = HTMLParser(encoding='utf-8')
                    element = document_fromstring(new_html.encode('utf-8', 'replace'), parser=utf8_parser)
                    body_text = self.dom_handler.get_text(element=element, remove_noise=True, body=True)
                news_start = news_start.replace('\xa0', ' ')
                body_text.replace('\xa0', ' ')
                try:
                    begin = body_text.index(title) + len(title)
                    if news_start in body_text:
                        end = body_text[begin:].rindex(news_start) + begin
                        if end - begin > 300:
                            end = begin + 300
                    else:
                        end = begin + 300
                    if begin >= end:
                        time_area = ''
                    else:
                        time_area = body_text[begin:end + 1]
                except:
                    time_area = ''
                if not time_area:
                    try:
                        end = body_text.rindex(news_start)
                        time_area = body_text[:end + 1]
                    except:
                        return ''
                # find_zh = re.findall(r'[\u4e00-\u9fa5]', time_area)
                # if len(find_zh) > 30:
                #     return ''
                else:
                    return self.extract_from_text(None, text=time_area)
        return ''


class Tes:
    def test1(self):
        file_path = '/Users/king/Library/Application Support/JetBrains/PyCharm2023.2/scratches/gne/tmp/data.html'
        html = open(file_path, encoding='gbk').read()
        normal_html = normalize_text(html)
        element = html2element(normal_html)
        title = TitleExtractor().extract(element)
        element = pre_parse(element)
        content = ContentExtractor().extract(element)
        pub_time = TimeExtractorFeature().extract_time_area(title, element, content[0][1]['text'])
        print(pub_time)

    def test2(self):
        file_path = '/Users/king/Library/Application Support/JetBrains/PyCharm2023.2/scratches/gne/tmp/data2.html'
        html = open(file_path).read()
        normal_html = normalize_text(html)
        element = html2element(normal_html)
        title = TitleExtractor().extract(element)
        element = pre_parse(element)
        content = ContentExtractor().extract(element)
        pub_time = TimeExtractorFeature().extract_time_area(title, element, content[0][1]['text'])
        pub_time = TimeExtractorFeature().extract_from_text(element, None, content[0][1]['text'])
        print(pub_time)

    def test3(self):
        text = """'Toggle navigation     亚太地区地图  专题报告  岛屿追踪器  Search for:  CH English 正體中文 Tiếng Việt Melayu NOTE: Some content may not be available in all languages.          Published: 4月 30, 2018   中'"""
        text = """ D e & Time   Mar. 13, 2023 9:00  – 10:30  ET Loc i   line  ly  is event will be webca   re  will begin in approxim ely —&col ;—&col ;— Refresh your browser wi ow if  re  does not  art autom ically. Submit a que i  Se  ano er message in —&col ;— Your n e a  title: Submi"""
        print(TimeExtractorFeature().extract_from_text(element=None, text=text))


if __name__ == '__main__':
    Tes().test3()

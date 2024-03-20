import re

from lxml.html import HtmlElement
from lxml.html import fromstring

from ..defaults import PUBLISH_TIME_META, PUBLISH_TIME_TAG, SCRIPT_TIME_RE, JW_DATETIME_PATTERN, DATETIME_PATTERN, RE_SUB_MAP


class TimeExtractor:
    def __init__(self):
        self.time_pattern = JW_DATETIME_PATTERN + DATETIME_PATTERN

    def extractor(self, element: HtmlElement, publish_time_xpath: str = '') -> str:
        publish_time = (self.extract_from_user_xpath(publish_time_xpath, element)  # 用户指定的 Xpath 是第一优先级
                        or self.extract_from_meta(element))
        return publish_time

    def extract_from_user_xpath(self, publish_time_xpath: str, element: HtmlElement) -> str:
        if publish_time_xpath:
            publish_time = ''.join(element.xpath(publish_time_xpath))
            return publish_time
        return ''

    def extract_from_text(self, element: HtmlElement) -> str:
        text = ''.join(element.xpath('.//text()'))
        for dt in self.time_pattern:
            dt_obj = re.search(dt, text)
            if dt_obj:
                return dt_obj.group(1)
        else:
            return ''

    def is_have_at_least_one_digit(self, string: str) -> bool:
        lst = []
        for char in string:
            lst.append(str(char).isdigit())
        return any(lst)

    def extract_from_meta(self, element: HtmlElement) -> str:
        """
        一些很规范的新闻网站，会把新闻的发布时间放在 META 中，因此应该优先检查 META 数据
        :param element: 网页源代码对应的Dom 树
        :return: str
        """
        for xpath in PUBLISH_TIME_META:
            publish_time = element.xpath(xpath)
            if publish_time and self.is_have_at_least_one_digit(publish_time[0]):
                return '|'.join([i for i in publish_time if i])
            else:
                continue
        return ''

    def extract_from_target_xpath(self, html_str) -> str:
        """
        从自定义的xpath 中获取
        Parameters
        ----------
        html_str :

        Returns
        -------

        """
        element = fromstring(html_str)

        for xpath in PUBLISH_TIME_TAG:
            # if str(xpath).startswith('//time'):
            #     time_element_num = element.xpath('//time')
            #     if len(time_element_num):
            #         continue
            publish_time = element.xpath(xpath)
            if publish_time:
                if len(publish_time) > 1:
                    new_xpath = xpath + '[1]'
                    publish_time = element.xpath(new_xpath)
                    return str(publish_time[0]).strip()

                else:
                    return str(publish_time[0]).strip()

        return ''

    def extract_from_full_text(self, html: str):
        dt_obj = ''
        root_element = fromstring(html)
        for element in root_element.iter():
            # 检查属性
            for key, value in element.attrib.items():
                if 5 < len(value.strip()) < 30:
                    for pattern in SCRIPT_TIME_RE:
                        result = re.search(pattern=pattern, string=value)
                        if result:
                            return result.group(1)

            # 检查文本内容
            text = element.text
            if text:
                try:
                    if 5 < len(text.strip()) < 30:
                        for dt in self.time_pattern:
                            dt_obj = re.search(dt, text, flags=re.I)
                            if dt_obj:
                                return dt_obj.group(1)

                except Exception as e:
                    return ''

        if not dt_obj:
            html = fromstring(html)

            text = ''

            for element in root_element.iter():
                text += ''.join(element.xpath('.//text()'))

            for pattern, repl_value in RE_SUB_MAP.items():
                text = re.sub(pattern, repl_value, text, flags=re.I)

            for dt in self.time_pattern:
                dt_obj = re.search(dt, text, flags=re.I)
                if dt_obj:
                    if '1970' not in dt_obj.group():
                        return dt_obj.group()
                    else:
                        continue
        return ''


class Test():

    def test_1(self):

        t = JW_DATETIME_PATTERN + DATETIME_PATTERN
        for dt in t:
            dt_obj = re.search(dt, 'November 25, 2010 9:54 a.m. EST | Filed under: '
                               , flags=re.I | re.S)
            if dt_obj:
                # (dt_obj, dt)
                if '1970' not in dt_obj.group(1):
                    return dt_obj
                else:
                    continue


if __name__ == '__main__':
    Test().test_1()

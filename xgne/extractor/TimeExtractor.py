import re
import time

from ..utils import config
from lxml.html import HtmlElement
from dateutil.parser import parse
from ..defaults import DATETIME_PATTERN, PUBLISH_TIME_META


class TimeExtractor:
    def __init__(self):
        self.time_pattern = DATETIME_PATTERN

    def extractor(self, element: HtmlElement, publish_time_xpath: str = '') -> dict:
        publish_time_xpath = publish_time_xpath or config.get('publish_time', {}).get('xpath')
        publish_time = (self.extract_from_user_xpath(publish_time_xpath, element)  # 用户指定的 Xpath 是第一优先级
                        or self.extract_from_meta(element)  # 第二优先级从 Meta 中提取
                        or self.extract_from_text(element))  # 最坏的情况从正文中提取

        return self.deal_publish_time(publish_time)

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

    def extract_from_meta(self, element: HtmlElement) -> str:
        """
        一些很规范的新闻网站，会把新闻的发布时间放在 META 中，因此应该优先检查 META 数据
        :param element: 网页源代码对应的Dom 树
        :return: str
        """
        for xpath in PUBLISH_TIME_META:
            publish_time = element.xpath(xpath)
            if publish_time:
                return ''.join(publish_time)
        # 从Meta标签中提取时间
        try:
            meta_tags = element.xpath("//meta")
            for meta_tag in meta_tags:
                name = meta_tag.get("name", "").lower()
                content = meta_tag.get("content", "").strip()
                if 'date' in name or 'time' in name or 'create' in name:
                    return content
        except Exception as e:
            pass
        return ''

    def deal_publish_time(self, publish_time_temp) -> dict:
        try:
            publish_time = parse(publish_time_temp)
            if publish_time:
                formatted_time = {
                    'publish_time_src': publish_time_temp,
                    'publish_time_ts': int(publish_time.timestamp()),
                    'publish_time_zone': publish_time.strftime('%Z'),
                    'publish_time_format': publish_time.strftime('%Y-%m-%d %H:%M:%S')
                }
                return formatted_time
            else:
                return self._set_default_pt()
        except Exception as e:
            return self._set_default_pt()

    def _set_default_pt(self):
        '''
        设置默认的发布时间
        :return:
        '''
        cts = int(time.time())
        ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cts))
        publish_time = parse(ctime)
        return {
            'publish_time_src': ctime,
            'publish_time_ts': cts,
            'publish_time_zone': publish_time.strftime('%Z'),
            'publish_time_format': ctime
        }

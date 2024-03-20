# -*- coding: utf-8 -*-

# 从script 标签中匹配时间特征
import json
import re

from parsel import Selector

from ..defaults import SCRIPT_TIME_RE, BASE_SCRIPT_TIME_RE, SCRIPT_TIME_RE_TOKEN


class TimeExtractorFeature2:
    def __init__(self):
        self.SCRIPT_TIME_RE = SCRIPT_TIME_RE

    def extract_from_target_re(self, html, class_name, ):
        sel = Selector(text=html)
        scripts = sel.xpath('//script').getall()
        new_re_pattern = BASE_SCRIPT_TIME_RE % class_name
        return self.find_date(scripts, [new_re_pattern])

    def find_date(self, scripts, patterns):
        for script_source_code in scripts:
            for re_pattern in patterns:
                result = re.search(pattern=re_pattern, string=script_source_code)
                if result:
                    return result.group(1)
        return ''

    def find_data_in_all_html_text(self, text):
        for re_pattern in self.SCRIPT_TIME_RE:
            result = re.search(pattern=re_pattern, string=text)
            if result:
                return result.group(1)

    def extract_data_from_ld_script(self, html_text):

        sel = Selector(text=html_text)

        datas = sel.xpath('//script[@type="application/ld+json"]/text()').getall()

        for data in datas:
            try:
                data = json.loads(data)
                for key in SCRIPT_TIME_RE_TOKEN:
                    try:
                        published = data[key]
                        if published:
                            return published
                    except Exception as e:
                        pass
            except Exception as e:
                pass

        return ''

    def extract_data_from_script_re(self, html_text):
        sel = Selector(text=html_text)
        scripts = sel.xpath('//script').getall()
        res = self.find_date(scripts, self.SCRIPT_TIME_RE)

        return res

    def extract_from_script(self, html: str):

        res = self.extract_data_from_ld_script(html_text=html) or self.extract_data_from_script_re(
            html_text=html) or self.find_data_in_all_html_text(html)

        return res

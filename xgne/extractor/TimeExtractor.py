import json
import re
from datetime import datetime

from parsel import Selector

from ..dom.DomHandler import DomHandle
from ..utils import config
from lxml.html import HtmlElement, fromstring, tostring, HTMLParser, document_fromstring
from dateutil.parser import parse
from ..defaults import DATETIME_PATTERN, PUBLISH_TIME_META, RE_SUB_MAP, SCRIPT_TIME_RE, JW_DATETIME_PATTERN, \
    PUBLISH_TIME_TAG, DATETIME_PATTERN_COMPARE, TIME_TOKEN, SCRIPT_TIME_RE_TOKEN, BASE_SCRIPT_TIME_RE


class TimeExtractor:
    def __init__(self):
        self.time_pattern = JW_DATETIME_PATTERN + DATETIME_PATTERN
        self.dom_handler = DomHandle()
        self.SCRIPT_TIME_RE = SCRIPT_TIME_RE

    def extractor(self, element: HtmlElement, publish_time_xpath: str = '', normal_html=None, title=None,
                  content=None, html=None, npp_pt=None) -> dict:
        '''
        时间解析器
        :param element: 网页对象
        :param publish_time_xpath: 发布时间xpath
        :param normal_html: 使用 NFKC 对网页源代码进行归一化，把特殊符号转换为普通符号
        :param title: 标题
        :param content: 内容
        :param html: 原始html源码
        :param text: 暂无定义使用
        :return:
        /*
                发布时间会整理以下四种格式以字典的形式返回
                {
                    'publish_time_src': '2012-12-10T09:24:01+00:00', # 发布时间原始数据
                    'publish_time_ts': 1355131441, # 发布时间时间戳格式
                    'publish_time_zone': UTC, # 发布时间的时区
                    'publish_time_format': '2012-12-10 09:24:01' # 发布时间格式化后的数据
                }
        */
        '''

        # normal_html = normal_html,
        # title = title,
        # content = content[0][1]['text'],
        # html = html,
        # text = None
        publish_time_xpath = publish_time_xpath or config.get('publish_time', {}).get('xpath')
        publish_time = (self.extract_from_user_xpath(publish_time_xpath, element)  # 用户指定的 Xpath 是第一优先级
                        or self.extract_from_meta(element)  # 第二优先级从 Meta 中提取
                        or npp_pt  # 引入3k的发布时间判断
                        or self.extract_data_from_ld_script(html_text=normal_html)  # 第三优先级从javascript中有Json的情况
                        or self.extract_data_from_script_re(html_text=normal_html)  # 第三优先级从javascript中与正则情况
                        or self.find_data_in_all_html_text(normal_html)  # 第三优先级从全文正则情况
                        or self.extract_time_area(title=title, element=element,
                                                  content=content)  # 第四优先级从标题字符串和内容元素定位时间区域，提取出其文本信息并返回
                        or self.extract_from_target_xpath(html)  # 第五优先级函数根据预定义的 XPath 规则提取发布时间信息
                        or self.extract_from_text(element)  # 第六优先级首先对文本进行预处理，然后尝试使用预定义的时间匹配模式进行提取
                        or self.extract_from_full_text(html=normal_html)  # 最后全文检索
                        )

        return self.deal_publish_time(publish_time)

    def extract_from_user_xpath(self, publish_time_xpath: str, element: HtmlElement) -> str:
        if publish_time_xpath:
            publish_time = ''.join(element.xpath(publish_time_xpath))
            return publish_time
        return ''

    def is_have_at_least_one_digit(self, string: str) -> bool:
        lst = []
        for char in string:
            lst.append(str(char).isdigit())
        return any(lst)

    def extract_from_meta(self, element: HtmlElement) -> str:
        """
        从 META 数据中提取时间信息。

        参数：
        - element：网页源代码对应的 DOM 树。

        返回值：
        - str：提取到的时间信息。

        注意：
        函数首先检查预定义的 XPath 表达式列表 PUBLISH_TIME_META，尝试从网页的 META 标签中提取时间信息。
        如果找到符合条件的时间信息，立即返回。
        如果未找到符合条件的时间信息，则继续检查所有 META 标签，尝试从中提取包含时间相关信息的标签内容。
        """

        # 遍历预定义的 XPath 表达式列表 PUBLISH_TIME_META
        for xpath in PUBLISH_TIME_META:
            # 使用 XPath 表达式从 DOM 树中提取元素
            publish_time = element.xpath(xpath)
            # 如果找到发布时间并且至少包含一个数字，则返回时间信息
            if publish_time and self.is_have_at_least_one_digit(publish_time[0]):
                return '|'.join([i for i in publish_time if i])  # 返回找到的时间信息
            # 如果找到发布时间，则返回时间信息
            if publish_time:
                return ''.join(publish_time)  # 返回找到的时间信息

        # 如果未在 META 数据中找到时间信息，则继续检查所有 META 标签
        try:
            meta_tags = element.xpath("//meta")
            for meta_tag in meta_tags:
                name = meta_tag.get("name", "").lower()
                content = meta_tag.get("content", "").strip()
                # 如果 META 标签的 name 属性包含 'date'、'time' 或 'create'，则返回标签内容作为时间信息
                if 'date' in name or 'time' in name or 'create' in name:
                    return content  # 返回找到的时间信息
        except Exception as e:
            pass

        return ''  # 如果未找到时间信息，则返回空字符串

    def extract_from_target_xpath(self, html_str) -> str:
        """
        从给定的 HTML 字符串中提取发布时间信息。

        参数：
        - html_str：包含目标信息的 HTML 字符串。

        返回值：
        - str：提取到的发布时间信息。

        注意：
        函数根据预定义的 XPath 规则提取发布时间信息。
        """

        # 使用 lxml 解析 HTML 字符串并构建元素树
        element = fromstring(html_str)

        # 遍历预定义的 XPath 规则列表
        for xpath in PUBLISH_TIME_TAG:
            publish_time = element.xpath(xpath)
            # 如果找到发布时间信息，返回第一个匹配的结果（去除首尾空白）
            if publish_time:
                if len(publish_time) > 1:
                    new_xpath = xpath + '[1]'
                    publish_time = element.xpath(new_xpath)
                    return str(publish_time[0]).strip()
                else:
                    return str(publish_time[0]).strip()

        # 如果未找到发布时间信息，返回空字符串
        return ''

    def extract_from_full_text(self, html: str):
        """
        从给定的 HTML 文本中提取时间信息。

        参数：
        - html：要提取时间的 HTML 文本。

        返回值：
        - str：提取到的时间信息。

        注意：
        函数首先遍历 HTML 元素，检查元素的属性值和文本内容是否包含可能的时间信息。
        如果找到符合条件的时间信息，立即返回。
        如果未找到符合条件的时间信息，则重新遍历 HTML 元素的文本内容，并使用预定义的时间匹配模式进行提取。
        """

        dt_obj = ''  # 用于存储找到的时间对象

        root_element = fromstring(html)

        # 遍历 HTML 元素
        for element in root_element.iter():
            # 检查元素的属性值
            for key, value in element.attrib.items():
                # 如果属性值长度在5到30之间，可能包含时间信息
                if 5 < len(value.strip()) < 30:
                    # 尝试匹配预定义的时间正则表达式
                    for pattern in SCRIPT_TIME_RE:
                        result = re.search(pattern=pattern, string=value)
                        if result:
                            return result.group(1)  # 返回匹配到的时间信息

            # 检查元素的文本内容
            text = element.text
            if text:
                try:
                    if 5 < len(text.strip()) < 30:
                        # 尝试匹配预定义的时间正则表达式
                        for dt in self.time_pattern:
                            dt_obj = re.search(dt, text, flags=re.I)
                            if dt_obj:
                                return dt_obj.group(1)  # 返回匹配到的时间信息
                except Exception as e:
                    return ''

        # 如果未找到符合条件的时间信息，则重新遍历 HTML 元素的文本内容
        if not dt_obj:
            text = ''
            for element in root_element.iter():
                text += ''.join(element.xpath('.//text()'))  # 获取 HTML 元素的文本内容

            # 根据预定义的替换映射表对文本内容进行处理
            for pattern, repl_value in RE_SUB_MAP.items():
                text = re.sub(pattern, repl_value, text, flags=re.I)

            # 尝试匹配预定义的时间正则表达式
            for dt in self.time_pattern:
                dt_obj = re.search(dt, text, flags=re.I)
                if dt_obj:
                    if '1970' not in dt_obj.group():
                        return dt_obj.group()  # 返回匹配到的时间信息
                    else:
                        continue

        return ''  # 如果未找到时间信息，则返回空字符串

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

    def extract_from_text(self, element: HtmlElement = None, text=None) -> str:
        """
        从给定的文本中提取时间信息。

        参数：
        - element：要提取时间的 HTML 元素对象（可选）。
        - text：要提取时间的文本内容（可选）。

        返回值：
        - str：提取到的时间信息。

        注意：
        函数首先对文本进行预处理，然后尝试使用预定义的时间匹配模式进行提取。
        如果提取成功，返回匹配到的第一个时间信息；否则返回空字符串。
        """

        # 如果未提供文本，则从给定元素中获取文本内容
        if text is None:
            text = self.dom_handler.get_text(element=element, seg=' ', remove_noise=True, body=True)

        # 预处理文本，替换一些常见的时间相关词语
        text = re.sub(r'下午|上午|星期.?', ' ', text)
        text = re.sub(r'\s+', ' ', text)

        # 尝试使用预定义的时间匹配模式进行提取
        for dt in self.time_pattern:
            dt_obj = re.search(dt, text)
            if dt_obj:
                return dt_obj.group(1)

        # 根据预定义的替换映射表对文本进行进一步处理
        for pattern, repl_value in RE_SUB_MAP.items():
            text = re.sub(pattern, repl_value, text, flags=re.I)

        # 尝试使用更复杂的时间匹配模式进行提取
        for dt in DATETIME_PATTERN_COMPARE:
            time_list = re.findall(dt, text, flags=re.S)
            check_result = self.check_time(time_list, text)
            if check_result is not None:
                return check_result

        # 如果未找到时间信息，尝试提取第一个匹配的时间信息
        for dt in self.time_pattern:
            dt_obj = re.search(dt, text, flags=re.I)
            if dt_obj:
                return dt_obj.group(1)

        # 如果仍未找到时间信息，返回空字符串
        return ''

    def extract_time_area(self, title, element, content) -> str:
        """
        从给定的元素中提取时间区域文本。

        参数：
        - title：标题字符串，用于定位时间区域。
        - element：HtmlElement 对象，包含了需要提取时间区域的元素。
        - content：HtmlElement 对象，表示整个文档的内容。

        返回值：
        - str：提取到的时间区域文本。

        注意：
        函数将根据标题字符串和内容元素定位时间区域，提取出其文本信息并返回。
        """

        # 确保 element 是 HtmlElement 类型且 content 不为空
        if isinstance(element, HtmlElement) and content:
            # 获取内容元素的文本信息
            content_text = self.dom_handler.get_text(content)
            # 如果标题字符串出现在内容文本中，返回空字符串
            if title in content_text:
                return ''
            else:
                # 从内容元素中提取纯文本信息
                body_text = self.dom_handler.get_text(element=element, remove_noise=True, body=True)
                # 获取内容文本的前 10 个字符作为检测标记
                news_start = content_text[:10] if len(content_text) > 9 else content_text
                # 如果标记不在提取的文本中，重新解析元素并提取文本信息
                if news_start not in body_text:
                    new_html = bytes.decode(tostring(element, encoding='utf-8', pretty_print=False, method='html'))
                    utf8_parser = HTMLParser(encoding='utf-8')
                    element = document_fromstring(new_html.encode('utf-8', 'replace'), parser=utf8_parser)
                    body_text = self.dom_handler.get_text(element=element, remove_noise=True, body=True)
                # 替换特殊字符
                news_start = news_start.replace('\xa0', ' ')
                body_text.replace('\xa0', ' ')
                try:
                    # 查找标题字符串在文本中的位置
                    begin = body_text.index(title) + len(title)
                    # 如果标记在文本中，确定时间区域的结束位置
                    if news_start in body_text:
                        end = body_text[begin:].rindex(news_start) + begin
                        if end - begin > 300:
                            end = begin + 300
                    else:
                        end = begin + 300
                    # 如果开始位置大于等于结束位置，返回空字符串
                    if begin >= end:
                        time_area = ''
                    else:
                        # 提取时间区域文本
                        time_area = body_text[begin:end + 1]
                except:
                    time_area = ''
                # 如果无法提取时间区域，尝试提取标题之前的文本作为时间区域
                if not time_area:
                    try:
                        end = body_text.rindex(news_start)
                        time_area = body_text[:end + 1]
                    except:
                        return ''
                # 如果提取到时间区域文本，继续提取其中的信息并返回
                else:
                    return self.extract_from_text(None, text=time_area)
        return ''

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
        """
        在 HTML 文本中查找时间信息。

        参数：
        - text：HTML 文本字符串。

        返回值：
        - str：找到的时间信息。

        注意：
        函数依次使用预定义的正则表达式列表 SCRIPT_TIME_RE 在文本中查找时间信息。
        如果找到符合条件的时间信息，则立即返回。
        """

        # 依次使用预定义的正则表达式列表在文本中查找时间信息
        for re_pattern in self.SCRIPT_TIME_RE:
            result = re.search(pattern=re_pattern, string=text)
            if result:
                return result.group(1)  # 如果找到符合条件的时间信息，则立即返回

        # 如果未找到时间信息，则返回空字符串
        return ''

    def extract_data_from_ld_script(self, html_text):
        """
        从包含在 <script type="application/ld+json"> 标签中的 JSON 数据中提取时间信息。

        参数：
        - html_text：HTML 文本字符串。

        返回值：
        - str：提取到的时间信息。

        注意：
        函数首先使用 XPath 表达式 '//script[@type="application/ld+json"]/text()' 提取 HTML 文本中的所有 JSON 数据。
        然后，遍历每个 JSON 数据，尝试从中提取时间信息。
        如果找到符合条件的时间信息，则立即返回。
        """

        # 使用 Scrapy 的 Selector 对象从 HTML 文本中提取 JSON 数据
        sel = Selector(text=html_text)
        datas = sel.xpath('//script[@type="application/ld+json"]/text()').getall()

        # 遍历所有提取到的 JSON 数据
        for data in datas:
            try:
                data = json.loads(data)
                # 遍历预定义的时间字段列表 SCRIPT_TIME_RE_TOKEN
                for key in SCRIPT_TIME_RE_TOKEN:
                    try:
                        published = data[key]
                        # 如果找到时间信息，则返回该信息
                        if published:
                            return published  # 返回找到的时间信息
                    except Exception as e:
                        pass
            except Exception as e:
                pass

        return ''  # 如果未找到时间信息，则返回空字符串

    def extract_data_from_script_re(self, html_text):
        """
        从 HTML 文本中的 <script> 标签中提取时间信息。

        参数：
        - html_text：HTML 文本字符串。

        返回值：
        - str：提取到的时间信息。

        注意：
        函数首先使用 Scrapy 的 Selector 对象从 HTML 文本中提取所有的 <script> 标签。
        然后，调用 find_date 函数，使用预定义的正则表达式列表 SCRIPT_TIME_RE 在每个 <script> 标签中查找时间信息。
        如果找到符合条件的时间信息，则立即返回。
        """

        # 使用 Scrapy 的 Selector 对象从 HTML 文本中提取所有的 <script> 标签
        sel = Selector(text=html_text)
        scripts = sel.xpath('//script').getall()

        # 调用 find_date 函数，在每个 <script> 标签中查找时间信息
        res = self.find_date(scripts, self.SCRIPT_TIME_RE)

        return res  # 返回找到的时间信息

    def extract_from_script(self, html: str):

        res = self.extract_data_from_ld_script(html_text=html) or self.extract_data_from_script_re(
            html_text=html) or self.find_data_in_all_html_text(html)

        return res

    def deal_publish_time(self, publish_time_temp) -> dict:
        try:
            publish_time = parse(publish_time_temp)
            # 将字符串转换为 datetime 对象
            input_time = datetime.fromisoformat(publish_time.isoformat())
            # 获取时区信息
            timezone_info = input_time.tzname()
            if publish_time:
                formatted_time = {
                    'publish_time_src': publish_time_temp,
                    'publish_time_ts': int(publish_time.timestamp()),
                    'publish_time_zone': timezone_info,
                    'publish_time_format': publish_time.strftime('%Y-%m-%d %H:%M:%S')
                }
                return formatted_time
            else:
                return self._set_default_pt()
        except Exception as e:
            return self._set_default_pt()

    def deal_publish_time_dtt(self, publish_time_temp) -> dict:
        '''
        处理时间格式为日期时间型
        '''
        try:
            # 将字符串转换为 datetime 对象
            input_time = datetime.fromisoformat(publish_time_temp.isoformat())
            publish_time_temp2 = publish_time_temp.strftime('%Y-%m-%d %H:%M:%S')
            publish_time = parse(publish_time_temp2)
            # 获取时区信息
            timezone_info = input_time.tzname()
            if publish_time:
                formatted_time = {
                    'publish_time_src': publish_time_temp2,
                    'publish_time_ts': int(input_time.timestamp()),
                    'publish_time_zone': timezone_info,
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
        # cts = int(time.time())
        # ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cts))
        # publish_time = parse(ctime)
        return {
            'publish_time_src': '',
            'publish_time_ts': '',
            'publish_time_zone': '',
            'publish_time_format': ''
        }

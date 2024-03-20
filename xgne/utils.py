import codecs
import logging
import os
import re
import yaml
import unicodedata
from lxml.html import fromstring, HtmlElement
from lxml.html import etree
from urllib.parse import urlparse, urljoin
from http.cookiejar import CookieJar as cj

from .version import __version__

from .defaults import USELESS_TAG, TAGS_CAN_BE_REMOVE_IF_EMPTY, USELESS_ATTR, HIGH_WEIGHT_ARRT_KEYWORD, ALLOWED_TYPES

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def normalize_node(element: HtmlElement):
    etree.strip_elements(element, *USELESS_TAG)
    for node in iter_node(element):
        # inspired by readability.
        if node.tag.lower() in TAGS_CAN_BE_REMOVE_IF_EMPTY and is_empty_element(node):
            remove_node(node)

        # merge text in span or strong to parent p tag
        if node.tag.lower() == 'p':
            etree.strip_tags(node, 'span')
            etree.strip_tags(node, 'strong')

        # if a div tag does not contain any sub node, it could be converted to p node.
        if node.tag.lower() == 'div' and not node.getchildren():
            node.tag = 'p'

        if node.tag.lower() == 'span' and not node.getchildren():
            node.tag = 'p'

        # remove empty p tag
        if node.tag.lower() == 'p' and not node.xpath('.//img'):
            if not (node.text and node.text.strip()):
                drop_tag(node)

        class_name = node.get('class')
        if class_name:
            if class_name in USELESS_ATTR:
                remove_node(node)
                break


def html2element(html):
    html = re.sub('</?br.*?>', '', html)
    element = fromstring(html)
    return element


def pre_parse(element):
    normalize_node(element)

    return element


def remove_noise_node(element, noise_xpath_list):
    noise_xpath_list = noise_xpath_list or config.get('noise_node_list')
    if not noise_xpath_list:
        return
    for noise_xpath in noise_xpath_list:
        nodes = element.xpath(noise_xpath)
        for node in nodes:
            remove_node(node)
    return element


def iter_node(element: HtmlElement):
    yield element
    for sub_element in element:
        if isinstance(sub_element, HtmlElement):
            yield from iter_node(sub_element)


def remove_node(node: HtmlElement):
    """
    this is a in-place operation, not necessary to return
    :param node:
    :return:
    """
    parent = node.getparent()
    if parent is not None:
        parent.remove(node)


def drop_tag(node: HtmlElement):
    """
    only delete the tag, but merge its text to parent.
    :param node:
    :return:
    """
    parent = node.getparent()
    if parent is not None:
        node.drop_tag()


def is_empty_element(node: HtmlElement):
    return not node.getchildren() and not node.text


def pad_host_for_images(host, url):
    """
    网站上的图片可能有如下几种格式：

    完整的绝对路径：https://xxx.com/1.jpg
    完全不含 host 的相对路径： /1.jpg
    含 host 但是不含 scheme:  xxx.com/1.jpg 或者  ://xxx.com/1.jpg

    :param host:
    :param url:
    :return:
    """
    if url.startswith('http'):
        return url
    parsed_uri = urlparse(host)
    scheme = parsed_uri.scheme
    if url.startswith(':'):
        return f'{scheme}{url}'
    if url.startswith('//'):
        return f'{scheme}:{url}'
    return urljoin(host, url)


def read_config():
    if os.path.exists('.xgne'):
        with open('.xgne', encoding='utf-8') as f:
            config_text = f.read()
        config = yaml.safe_load(config_text)
        return config
    return {}


def get_high_weight_keyword_pattern():
    return re.compile('|'.join(HIGH_WEIGHT_ARRT_KEYWORD), flags=re.I)


def get_longest_common_sub_string(str1: str, str2: str) -> str:
    """
    获取两个字符串的最长公共子串。

    构造一个矩阵，横向是字符串1，纵向是字符串2，例如：

      BL是天才！？
    听0 0 0 0 00 0
    说0 0 0 0 00 0
    B1 0 0 0 00 0
    L0 1 0 0 00 0
    是0 0 1 0 00 0
    天0 0 0 1 00 0
    才0 0 0 0 10 0
    ！0 0 0 0 01 0

    显然，只要斜对角线最长的就是最长公共子串

    :param str1: 第一个字符串
    :param str2: 第二个字符串
    :return: 最长公共子串
    """
    if not all([str1, str2]):
        return ''

    # 构造一个矩阵，横向是字符串1，纵向是字符串2
    matrix = [[0] * (len(str2) + 1) for _ in range(len(str1) + 1)]
    max_length = 0
    start_position = 0

    for index_of_str1 in range(1, len(str1) + 1):
        for index_of_str2 in range(1, len(str2) + 1):
            if str1[index_of_str1 - 1] == str2[index_of_str2 - 1]:
                matrix[index_of_str1][index_of_str2] = matrix[index_of_str1 - 1][index_of_str2 - 1] + 1
                if matrix[index_of_str1][index_of_str2] > max_length:
                    max_length = matrix[index_of_str1][index_of_str2]
                    start_position = index_of_str1 - max_length
            else:
                matrix[index_of_str1][index_of_str2] = 0

    return str1[start_position: start_position + max_length]


def normalize_text(html):
    """
    使用 NFKC 对网页源代码进行归一化，把特殊符号转换为普通符号
    :param html:
    :return:
    """
    return unicodedata.normalize('NFKC', html)


def urljoin_if_valid(base_url: str, url: str) -> str:
    """拼接基本URL和可能是相对URL的地址，防止由于解析导致的无效URL。

    Args:
        base_url (str): 基本URL（即文章的URL）
        url (str): 相对或绝对URL

    Returns:
        str: 如果有效则返回拼接的URL，否则返回空字符串
    """

    try:
        res = urljoin(base_url, url)
        return res
    except ValueError:
        return ""


def url_to_filetype(abs_url: str) -> None:
    """
    输入一个URL，输出由URL指定的文件的文件类型。对于没有文件类型的情况，返回None。
    'http://blahblah/images/car.jpg' -> 'jpg'
    'http://yahoo.com'               -> None
    """
    path = urlparse(abs_url).path.rstrip('/')
    path_chunks = [x for x in path.split("/") if x]
    last_chunk = path_chunks[-1].split('.')  # 最后一块通常是文件
    if len(last_chunk) < 2:
        return None
    file_type = last_chunk[-1]
    # 假设文件扩展名最多为5个字符长
    return file_type.lower() if len(file_type) <= 5 or file_type.lower() in ALLOWED_TYPES else None


def get_requests_params():
    '''
    获取请求头的参数
    :return:
    '''
    return {
        "timeout": 7,
        "proxies": {},
        "headers": {
            "User-Agent": f"xgne/{__version__}",
        },
        "cookies": cj(),
    }


# 通用文本过滤
def universal_filter(text):
    if text:
        # \u1234
        text = text.replace(u'\u200b', '')
        text = text.replace(u'\u2002', '')
        text = text.replace(u'\u3000', '')
        text = text.replace(u'\ufeff', '')
        # \x??
        text = text.replace(u'\xa0', '')
        text = text.replace(u'\x7f', '')
        # &??
        text = text.replace('&nbsp', ' ')
        text = text.replace('&ldquo;', '"')
        text = text.replace('&rdquo;', '"')
        text = text.replace('&bull;', '•')
        text = text.replace('&mdash;', '—')
        text = text.replace('&lsquo;', "'")
        text = text.replace('&rsquo;', "'")
        text = text.replace('&hellip;', '…')
        text = text.replace('&middot;', '·')
        text = text.replace('&quot;', '"')
        text = text.replace('&amp;', '&')
        text = text.replace('&#39;', "'")
        text = text.replace('&deg;', "°")
        text = text.replace('&times;', "×")
        text = text.replace('&beta;', "β")
        text = text.replace('&ndash;', "–")
        # \n, \r, \t
        text = text.replace('\n', '')
        text = text.replace('\r', '')
        text = text.replace('\t', '')
        # '  ?  '
        text = text.strip()
    return text


class FileHelper(object):
    @staticmethod
    def loadResourceFile(filename):
        if not os.path.isabs(filename):
            dirpath = os.path.abspath(os.path.dirname(__file__))
            path = os.path.join(dirpath, 'resources', filename)
        else:
            path = filename
        try:
            f = codecs.open(path, 'r', 'utf-8')
            content = f.read()
            f.close()
            return content
        except IOError:
            raise IOError("Couldn't open file %s" % path)


config = read_config()

# #!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2023-12-24 15:21
# @Author : BruceLong
# @FileName: x_test.py
# @Email   : 18656170559@163.com
# @Software: PyCharm
# @Blog ：http://www.cnblogs.com/yunlongaimeng/
from pprint import pprint

from xgne import GeneralNewsExtractor

# html = '''经过渲染的网页 HTML 代码'''
import requests

# url = 'https://washingtonindependent.com/how-to-apply-for-reseller-permit-in-washington-state/'
# url = 'https://nationalinterest.org/blog/buzz/china-offered-taiwanese-pilot-15-million-steal-us-made-ch-47-helicopter-207917'
# url = 'https://tulapressa.ru/2023/12/jetour-x70-plus-eshhe-bolshe-vozmozhnostej-dlya-semejnyx-puteshestvij/'
# url = 'https://www.thepaper.cn/newsDetail_forward_25397910'
url = 'https://www.autodeal.com.ph/articles/car-news-philippines/jetour-auto-alabang-launches-new-premium-dealership'

# url = 'https://abreview.ru/ab/news/hongqi_uvelichil_set_do_15_dilerov/'
# url = 'http://www.bbc.co.uk/zhongwen/simp/chinese_news/2012/12/121210_hongkong_politics.shtml'
# url = 'https://tulapressa.ru/2023/12/jetour-x70-plus-eshhe-bolshe-vozmozhnostej-dlya-semejnyx-puteshestvij/'
# url = 'https://vk.com/jetour_keyauto_krasnodar?from=quick_search'
# url = 'https://m.vk.com/wall-220824670_826'
# url = 'https://m.vk.com/wall-220824670_803'
# url = 'https://club.autohome.com.cn/bbs/thread/51d14cddbcd9673f/107158122-1.html'
# url = 'https://www.ruiwen.com/xindetihui/6404315.html'

proxies = {
    'http': 'http://192.168.1.112:1205',
    'https': 'http://192.168.1.112:1205'
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.62'
}


if __name__ == '__main__':
    # response = requests.get(url=url, proxies=proxies, headers=headers)
    response = requests.get(url=url)
    if response.status_code in [200, 302]:
        html = response.text
        extractor = GeneralNewsExtractor()
        result = extractor.extract(html)
        pprint(result)

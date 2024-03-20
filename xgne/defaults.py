# *********************************作者配置信息********************************
import re

AUTHOR_PATTERN = [
    "责编[：|:| |丨|/]\s*([\u4E00-\u9FA5a-zA-Z]{2,20})[^\u4E00-\u9FA5|:|：]",
    "责任编辑[：|:| |丨|/]\s*([\u4E00-\u9FA5a-zA-Z]{2,20})[^\u4E00-\u9FA5|:|：]",
    "作者[：|:| |丨|/]\s*([\u4E00-\u9FA5a-zA-Z]{2,20})[^\u4E00-\u9FA5|:|：]",
    "编辑[：|:| |丨|/]\s*([\u4E00-\u9FA5a-zA-Z]{2,20})[^\u4E00-\u9FA5|:|：]",
    "文[：|:| |丨|/]\s*([\u4E00-\u9FA5a-zA-Z]{2,20})[^\u4E00-\u9FA5|:|：]",
    "原创[：|:| |丨|/]\s*([\u4E00-\u9FA5a-zA-Z]{2,20})[^\u4E00-\u9FA5|:|：]",
    "撰文[：|:| |丨|/]\s*([\u4E00-\u9FA5a-zA-Z]{2,20})[^\u4E00-\u9FA5|:|：]",
    "来源[：|:| |丨|/]\s*([\u4E00-\u9FA5a-zA-Z]{2,20})[^\u4E00-\u9FA5|:|：|<]",
    # 以下正则表达式需要进一步测试
    # '(作者[：|:| |丨|/]\s*[\u4E00-\u9FA5a-zA-Z、 ]{2,20})[）】)]]?[^\u4E00-\u9FA5|:|：]',
    # '(记者[：|:| |丨|/]\s*[\u4E00-\u9FA5a-zA-Z、 ]{2,20})[）】)]]?[^\u4E00-\u9FA5|:|：]',
    # '(原创[：|:| |丨|/]\s*[\u4E00-\u9FA5a-zA-Z、 ]{2,20})[）】)]]?[^\u4E00-\u9FA5|:|：]',
    # '(撰文[：|:| |丨|/]\s*[\u4E00-\u9FA5a-zA-Z、 ]{2,20})[）】)]]?[^\u4E00-\u9FA5|:|：]',
    # '(文/图[：|:| |丨|/]?\s*[\u4E00-\u9FA5a-zA-Z、 ]{2,20})[）】)]]?[^\u4E00-\u9FA5|:|：]',
]

AUTHOR_ATTRS = ["name", "rel", "itemprop", "class", "id", "property"]
AUTHOR_VALS = [
    "author",
    "byline",
    "dc.creator",
    "byl",
    "article:author",
    "story-byline",
    "article-author",
]
AUTHOR_STOP_WORDS = [
    "By",
    "Reuters",
    "IANS",
    "AP",
    "AFP",
    "PTI",
    "IANS",
    "ANI",
    "DPA",
    "Senior Reporter",
    "Reporter",
    "Writer",
    "Opinion Writer",
]
# *********************************时间相关配置信息********************************
DATETIME_PATTERN = [
    "(\d{4}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[0-1]?[0-9]:[0-5]?[0-9]:[0-5]?[0-9])",
    "(\d{4}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[2][0-3]:[0-5]?[0-9]:[0-5]?[0-9])",
    "(\d{4}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[0-1]?[0-9]:[0-5]?[0-9])",
    "(\d{4}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[2][0-3]:[0-5]?[0-9])",
    "(\d{4}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[1-24]\d时[0-60]\d分)([1-24]\d时)",
    "(\d{2}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[0-1]?[0-9]:[0-5]?[0-9]:[0-5]?[0-9])",
    "(\d{2}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[2][0-3]:[0-5]?[0-9]:[0-5]?[0-9])",
    "(\d{2}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[0-1]?[0-9]:[0-5]?[0-9])",
    "(\d{2}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[2][0-3]:[0-5]?[0-9])",
    "(\d{2}[-|/|.]\d{1,2}[-|/|.]\d{1,2}\s*?[1-24]\d时[0-60]\d分)([1-24]\d时)",
    "(\d{4}年\d{1,2}月\d{1,2}日\s*?[0-1]?[0-9]:[0-5]?[0-9]:[0-5]?[0-9])",
    "(\d{4}年\d{1,2}月\d{1,2}日\s*?[2][0-3]:[0-5]?[0-9]:[0-5]?[0-9])",
    "(\d{4}年\d{1,2}月\d{1,2}日\s*?[0-1]?[0-9]:[0-5]?[0-9])",
    "(\d{4}年\d{1,2}月\d{1,2}日\s*?[2][0-3]:[0-5]?[0-9])",
    "(\d{4}年\d{1,2}月\d{1,2}日\s*?[1-24]\d时[0-60]\d分)([1-24]\d时)",
    "(\d{2}年\d{1,2}月\d{1,2}日\s*?[0-1]?[0-9]:[0-5]?[0-9]:[0-5]?[0-9])",
    "(\d{2}年\d{1,2}月\d{1,2}日\s*?[2][0-3]:[0-5]?[0-9]:[0-5]?[0-9])",
    "(\d{2}年\d{1,2}月\d{1,2}日\s*?[0-1]?[0-9]:[0-5]?[0-9])",
    "(\d{2}年\d{1,2}月\d{1,2}日\s*?[2][0-3]:[0-5]?[0-9])",
    "(\d{2}年\d{1,2}月\d{1,2}日\s*?[1-24]\d时[0-60]\d分)([1-24]\d时)",
    "(\d{1,2}月\d{1,2}日\s*?[0-1]?[0-9]:[0-5]?[0-9]:[0-5]?[0-9])",
    "(\d{1,2}月\d{1,2}日\s*?[2][0-3]:[0-5]?[0-9]:[0-5]?[0-9])",
    "(\d{1,2}月\d{1,2}日\s*?[0-1]?[0-9]:[0-5]?[0-9])",
    "(\d{1,2}月\d{1,2}日\s*?[2][0-3]:[0-5]?[0-9])",
    "(\d{1,2}月\d{1,2}日\s*?[1-24]\d时[0-60]\d分)([1-24]\d时)",
    "(\d{4}[-|/|.]\d{1,2}[-|/|.]\d{1,2})",
    "(\d{2}[-|/|.]\d{1,2}[-|/|.]\d{4})",
    "(\d{2}[-|/|.]\d{1,2}[-|/|.]\d{1,2})",
    "(\d{4}年\d{1,2}月\d{1,2}日)",
    "(\d{1,2}月(\.| |-|,)*\d{1,2}(\.| |-|,)*\d{4})",  # 4月 30, 2018
    "((\d{4})(\.|,| |\|)*年(\.|,| |\|)*\d{1,2}(\.|,| |\|)*月(\.|,| |\|)*\d{1,2}日)",  # 年月日中间带有空格.和,
    "(\d{2}年\d{1,2}月\d{1,2}日)",
    "(\d{1,2}月\d{1,2}日)"
]

PUBLISH_TIME_META = [  # 部分特别规范的新闻网站，可以直接从 HTML 的 meta 数据中获得发布时间
    '//meta[starts-with(@property, "rnews:datePublished")]/@content',
    '//meta[starts-with(@property, "article:published_time")]/@content',
    '//meta[starts-with(@property, "og:published_time")]/@content',
    '//meta[starts-with(@property, "og:release_date")]/@content',
    '//meta[starts-with(@itemprop, "datePublished")]/@content',
    '//meta[starts-with(@itemprop, "dateUpdate")]/@content',
    '//meta[starts-with(@name, "OriginalPublicationDate")]/@content',
    '//meta[starts-with(@name, "article_date_original")]/@content',
    '//meta[starts-with(@name, "og:time")]/@content',
    '//meta[starts-with(@name, "apub:time")]/@content',
    '//meta[starts-with(@name, "publication_date")]/@content',
    '//meta[starts-with(@name, "sailthru.date")]/@content',
    '//meta[starts-with(@name, "PublishDate")]/@content',
    '//meta[starts-with(@name, "publishdate")]/@content',
    '//meta[starts-with(@name, "PubDate")]/@content',
    '//meta[starts-with(@name, "pubtime")]/@content',
    '//meta[starts-with(@name, "_pubtime")]/@content',
    '//meta[starts-with(@name, "weibo: article:create_at")]/@content',
    '//meta[starts-with(@pubdate, "pubdate")]/@content',
]
JW_DATETIME_PATTERN = [
    "(((\d{1,2}:\d{1,2}:\d{1,2})(\.|,| |\||/|-|—|\[|\])*(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\.|,| |\||/|-|—|\[|\])*\d{1,4}(\.|,| |\||/|-|—|\[|\])*(\d{2,4})))",
    "((\d{1,2}:\d{1,2})(\.|,| |\||/|-|—|\[|\])*(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\.|,| |\||/|-|—|\[|\])*\d{1,4}(\.|,| |\||/|-|—|\[|\])*(\d{2,4}))",
    "(\d{1,4}(\.|,| |\||/|-|—|\[|\])*(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Aug|Sept|Oct|Nov|Dec)(\.|,| |\||/|-|—|\[|\])*(\d{2,4})(\.|,| |\||/|-|—|\[|\])*(\d{1,2}:\d{1,2}((:\d{1,2})?))?)",
    "((January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Aug|Sept|Oct|Nov|Dec)(\.|,| |\||/|-|—|\[|\])*\d{1,4}(\.|,| |\||/|-|—|\[|\])*(\d{2,4})(\.|,| |\||/|-|—|\[|\])*(\d{1,2}:\d{1,2}((:\d{1,2})?))?)",
    "(\d{1,4}(\.|,| |\||/|-|—|\[|\])*(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)(\.|,| |\||/|-|—|\[|\])*(\d{2,4})(\.|,| |\||/|-|—|\[|\])*(\d{1,2}:\d{1,2}((:\d{1,2})?))?)",
    "((Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)(\.|,| |\||/|-|—|\[|\])*\d{1,4}(\.|,| |\||/|-|—|\[|\])*(\d{2,4})(\.|,| |\||/|-|—|\[|\])*(\d{1,2}:\d{1,2}((:\d{1,2})?))?)",
    # 印度尼西亚月份

    "(\d{1,2}) ?(minutes|hours|day|days) ?(ago)",  # 3 days ago
    "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",  # 标准utc 时间
    '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z$'  # 带毫秒的utc 时间 2023-03-27T10:00:22.260993Z
    "(\d{4}(\.| |\|)*\d{1,2}(\.| |\|)*\d{1,2}(\.| |\|)*\d{2}:\d{2}:\d{2})",  # 2016. 9. 20. 15:01:01
    "(\d{4}(\.| |\|)*\d{1,2}(\.| |\|)*\d{1,2}(\.| |\|)*\d{2}:\d{2})",  # 2016. 9. 20. 15:01

]
DATETIME_PATTERN.extend(JW_DATETIME_PATTERN)
# *********************************标题配置信息********************************
TITLE_HTAG_XPATH = '//h1//text() | //h2//text() | //h3//text() | //h4//text()'

TITLE_SPLIT_CHAR_PATTERN = '[-_|]'

USELESS_TAG = ['style', 'script', 'link', 'video', 'iframe', 'source', 'picture', 'header', 'blockquote',
               'footer']

# if one tag in the follow list does not contain any child node nor content, it could be removed
TAGS_CAN_BE_REMOVE_IF_EMPTY = ['section', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span']

USELESS_ATTR = {
    'share',
    'contribution',
    'copyright',
    'copy-right',
    'disclaimer',
    'recommend',
    'related',
    'footer',
    'comment',
    'social',
    'submeta',
    'report-infor'
}

# *********************************正文配置信息********************************
HIGH_WEIGHT_ARRT_KEYWORD = ['content',
                            'article',
                            'news_txt',
                            'post_text']

# *********************************Meta配置信息********************************
META_IMAGE_TAGS = [
    {"tag": "meta", "field": 'meta[property="og:image"]', "score": 10},
    {"tag": "link", "attr": "rel", "value": "image_src|img_src", "score": 8},
    {"tag": "meta", "field": 'meta[name="og:image"]', "score": 8},
    {"tag": "link", "attr": "rel", "value": "icon", "score": 5},
]

ARTICLE_BODY_TAGS = [
    {"tag": "article", "role": "article"},
    {"itemprop": "articleBody"},
    {"itemtype": "https://schema.org/Article"},
    {"itemtype": "https://schema.org/NewsArticle"},
    {"itemtype": "https://schema.org/BlogPosting"},
    {"itemtype": "https://schema.org/ScholarlyArticle"},
    {"itemtype": "https://schema.org/SocialMediaPosting"},
    {"itemtype": "https://schema.org/TechArticle"},
]

ALLOWED_TYPES = [
    "html",
    "htm",
    "md",
    "rst",
    "aspx",
    "jsp",
    "rhtml",
    "cgi",
    "xhtml",
    "jhtml",
    "asp",
    "shtml",
]
TOP_IMAGE_SETTINGS = {
    "min_width": 300,
    "min_height": 200,
    "min_area": 10000,
    "max_retries": 2,
}
TIME_TOKEN = ['发布时间', '发表时间', '发布日期', '时间:', '时间：', '日期：', '更新時間：',
              'Updated:', 'Published:', 'published about', 'issue', 'issued', '當前報紙', '發表於', 'Updated', 'Published on ',
              'Published: '
              ]

INLINE_TAG = ['span', 'a', 'em', 'b', 'i', 'small', 'strong']
MAYBEIS = ['and', 'article', 'body', 'column', 'main', 'shadow']

DATETIME_PATTERN_COMPARE = [
    # "((((\.|,| |\||/|-|—)*)?)(\d{1,2}:\d{1,2}((:\d{1,2})?))?(((\.|,| |\||/|-|—)*)?)(\d{1,4})?(((\.|,| |\||/|-|—)*)?)(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Aug|Sept|Oct|Nov|Dec)(((\.|,| |\||/|-|—)*)?)((\d{2,4})?)(((\.|,| |\||/|-|—)*)?)((\d{2,4})?)(((\.|,| |\||/|-|—)*)?)(\d{1,2}:\d{1,2}((:\d{1,2})?))?(((\.|,| |\||/|-|—)*)?)\w+(([\+-]\d)?))",
    "([1-2]\d{3}[-|/|.]\d{1,2}[-|/|.]\d{1,2}/?\s*?[0-2]?[0-9]:[0-5]?[0-9]:[0-5]?[0-9])",  # 2020-04-05 12:23:23
    "([1-2]\d{3}[-|/|.]\d{1,2}[-|/|.]\d{1,2}/?\s*?[0-2]?[0-9]:[0-5]?[0-9])",  # 2020-04-05 12:23
    "([1-2]\d{3}[-|/|.]\d{1,2}[-|/|.]\d{1,2}/?\s*?[0-2]?[0-9][时|点][0-5]?[0-9]分[0-5]?[0-9]秒)",  # 2020-04-05 12时23分05秒
    "([1-2]\d{3}[-|/|.]\d{1,2}[-|/|.]\d{1,2}/?\s*?[0-2]?[0-9][时|点][0-5]?[0-9]分)",  # 2020-04-05 12时23分
    "([1-2]\d{1}[-|/|.]\d{1,2}[-|/|.]\d{1,2}/?\s*?[0-2]?[0-9]:[0-5]?[0-9]:[0-5]?[0-9])",  # 20-04-05 12:23:23
    "([1-2]\d{1}[-|/|.]\d{1,2}[-|/|.]\d{1,2}/?\s*?[0-2]?[0-9]:[0-5]?[0-9])",  # 20-04-05 12:23
    "([1-2]\d{3}年\s*\d{1,2}月\s*\d{1,2}日?\s*?[0-2]?[0-9]:[0-5]?[0-9]:[0-5]?[0-9])",  # 2020年3月12日  12:23:23
    "([1-2]\d{3}年\s*\d{1,2}月\s*\d{1,2}日?\s*?[0-2]?[0-9]:[0-5]?[0-9])",  # 2020年3月12日  12:23
    "([1-2]\d{3}年\d{1,2}月\d{1,2}日?\s*?[0-2]?[0-9][时|点][0-5]?[0-9]分[0-5]?[0-9]秒)",  # 2020年3月12日  12时23分45秒
    "([1-2]\d{3}年\d{1,2}月\d{1,2}日?\s*?[0-2]?[0-9][时|点][0-5]?[0-9]分)",  # 2020年3月12日  12时23分
    "([1-2]\d{1}年\d{1,2}月\d{1,2}日?\s*?[0-2]?[0-9]:[0-5]?[0-9]:[0-5]?[0-9])",  # 20年3月12日  12:23:23
    "([1-2]\d{1}年\d{1,2}月\d{1,2}日?\s*?星期.\s*?[0-2]?[0-9]:[0-5]?[0-9])",  # 20年3月12日  12:23
    "([1-2]\d{1}年\d{1,2}月\d{1,2}日?\s*?[0-2]?[0-9][时|点][0-5]?[0-9]分[0-5]?[0-9]秒)",  # 20年3月12日  12时23分45秒
    "([1-2]\d{1}年\d{1,2}月\d{1,2}日?\s*?[[0-2]?[0-9][时|点][0-5]?[0-9]分)",  # 20年3月12日  12时23分
    "(\d{1,2}月\d{1,2}日?\s*?[0-2]?[0-9]:[0-5]?[0-9]:[0-5]?[0-9])",  # 3月12日  12:23:23
    "(\d{1,2}月\d{1,2}日?\s*?[0-2]?[0-9]:[0-5]?[0-9])",  # 3月12日  12:23
    "(\d{1,2}[-|/|.]\d{1,2}\s*?[0-2]?[0-9]:[0-5]?[0-9]:[0-5]?[0-9])",  # 04-05 12:23:23
    "(\d{1,2}[-|/|.]\d{1,2}\s+[0-2]?[0-9]:[0-5]?[0-9])",  # 04-05 12:23
    "([1-2]\d{3}[-|/|.]\d{1,2}[-|/|.]\d{1,2})",  # 2020-3-12
    "([1-2]\d{1}[-|/|.]\d{1,2}[-|/|.]\d{1,2})",  # 20-3-12
    "([1-2]\d{3}年\d{1,2}月\d{1,2}日?)",  # 2020年3月12日
    "([0-2]\d{1}年\d{1,2}月\d{1,2}日?)",  # 20年3月12日

]


def jp_sub_func(match):
    if match.group(1) == '令和':

        if str(match.group(2)).isdigit():
            return str(2018 + int(match.group(2))) + '年'
        elif match.group(2) == '元':
            return str(2019) + '年'

    elif match.group(1) == '平成':
        if str(match.group(2)).isdigit():
            return str(2018 + int(match.group(2))) + '年'
        elif match.group(2) == '元':
            return str(1989) + '年'

    else:
        return match.group()


def sub_st(match):
    if match.group(0).strip() in ['august', 'Agustus']:
        return match.group(0)
    else:
        return ' '


RE_SUB_MAP = {
    '(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)': ' ',
    '(Mon|Tues|Wed|Thur|Fri|Sat|Sun)': ' ',
    '(Mon|Tue|Wed|Thu|Fri|Sat|Sun)': ' ',
    '(Mon.|Tues.|Wed.|Thur.|Fri.|Sat.|Sun.)': ' ',
    # '(AM|PM|a.m.|p.m.)': ' ',
    '(on|at)': ' ',
    '(nd|rd|th)': ' ',
    '(平成|令和)(\S+)年': jp_sub_func,
    '.*?st.*?': sub_st,
    '時': '时'

}
# name itemprop property

MATA_TIME_TOKEN = {
    'article:published_time',
    'datePublished',
    'dateUpdate',
    'pubDate',
    'pubdate',
    'date',
    'og:published_time',
    'og:article:published_time',
    'og:release_date',
    'og:time',
    'render_timestamp',
    'weibo: article:create_at',
    '_pubtime',
    'cXenseParse:recs:publishtime',
    'pubtime',
    'PubDate',
    'publishdate',
    'PublishDate',
    'publishDate',
    'sailthru.date',
    'publication_date',
    'apub:time',
    'article_date_original',
    'OriginalPublicationDate',
    'dcterms.date',
    'nv:news:date',
    'parsely-pub-date',
    'citation_publication_date',
    'article:published_time',
    'issueDate',
    'date.release'
}
PUBLISH_TIME_META_EXTRA = [
    '//meta[starts-with(@pubdate, "pubdate")]/@content',
    '//meta[contains(@name, "date")]/@content',
    '//meta[contains(@name, "publish")]/@content',
    '//meta[contains(@name, "published")]/@content',
    '//meta[contains(@property, "published")]/@content',
    '//meta[contains(@property, "publish")]/@content',
    '//meta[contains(@property, "date")]/@content',
    '//meta[contains(@itemprop, "date")]/@content',
    '//meta[contains(@itemprop, "publish")]/@content',
    '//meta[contains(@itemprop, "published")]/@content',
]


def generate_meta_xpath():
    for prop in ['name', 'itemprop', 'property']:
        for class_name in MATA_TIME_TOKEN:
            pattern = '//meta[starts-with(@%s, "%s")]/@content'
            PUBLISH_TIME_META.append(pattern % (prop, class_name))
    PUBLISH_TIME_META.extend(PUBLISH_TIME_META_EXTRA)


STOPWORDS_DIR = ''

generate_meta_xpath()

PUBLISH_TIME_TAG = [
    '//time/@datetime',  # h5 time 标签
    '//time/@dateTime',  # h5 time 标签
    '//relative-time/@datetime',  # h5 time 标签
    '//*[@id="story_date"]/text()',
    '//*[@class="time"]/text()',
    '//time/@content',
    '//*[@class="date"]/text()',
    '//*[contains(@class,"date-time")]/text()',
    '//*[contains(@class,"updated-date-time")]/text()',
    '//*[contains(@class,"num_date")]/text()',
    '//*[contains(@class,"se_date")]/text()',
    '//*[contains(@class,"post-date")]/text()',
    '//*[contains(@class,"teaser-byline-text-date")]/text()',
    '//*[contains(@class,"date_posted")]/text()',
    '//*[@itemprop="datePublished"]/@content',
    '//time/text()',
    '//*[@class="time"]/text()',
    '//*[contains(@class,"date")]/text()',
    '//*[contains(@class,"time")]/text()',
]

SCRIPT_TIME_RE = [

]

## 只取group 1 的这个要注意
BASE_SCRIPT_TIME_RE = """["\']?%s *["\']? *: *["\']?(.*?)["\']"""
SCRIPT_TIME_RE_TOKEN = [
    'datePublished',
    'publishedDate',
    'created_date',
    'publish_date',
    'publishedDateCro',
    'publishedDateUtc',
    'publishedAtDate',
    'articlePublishTime',
    'ep_contentdata_delivered_date',
    'deliveredDate',
    "createdAt",
    'dateModified',
]
SCRIPT_TIME_RE_EXTRA = [

]


def generate_script_re():
    for token in SCRIPT_TIME_RE_TOKEN:
        SCRIPT_TIME_RE.append(re.compile(BASE_SCRIPT_TIME_RE % token, re.I))
    SCRIPT_TIME_RE.extend(SCRIPT_TIME_RE_EXTRA)


generate_script_re()

USELESS_TAG_TO_TIME = ['style', 'link', 'iframe', 'blockquote']

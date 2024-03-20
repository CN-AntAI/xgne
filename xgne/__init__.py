from .utils import pre_parse, remove_noise_node, config, html2element, normalize_text
from .extractor import ContentExtractor, TitleExtractor, TimeExtractor, AuthorExtractor, ListExtractor, LangExtractor, \
    HeadMetaExtractor
from newspaper import Config, Article


class GeneralNewsExtractor:
    def __init__(self):
        # 配置 newspaper
        self.config = Config()
        self.article = Article('')

    def extract(self,
                html,
                title_xpath='',
                author_xpath='',
                publish_time_xpath='',
                host='',
                body_xpath='',
                noise_node_list=None,
                with_body_html=False,
                use_visiable_info=False):
        # 对 HTML 进行预处理可能会破坏 HTML 原有的结构，导致根据原始 HTML 编写的 XPath 不可用
        # 因此，如果指定了 title_xpath/author_xpath/publish_time_xpath，那么需要先提取再进行
        self.article.set_html(html)
        self.article.parse()
        # 预处理
        normal_html = normalize_text(html)
        element = html2element(normal_html)
        lang = LangExtractor().language(html)
        headmeta = HeadMetaExtractor().extractor(element)
        title = TitleExtractor().extract(element, title_xpath=title_xpath)
        author = AuthorExtractor().extractor(element, author_xpath=author_xpath) or self.article.authors
        element = pre_parse(element)
        remove_noise_node(element, noise_node_list)
        if not host:
            host = headmeta.get('host')
        content = ContentExtractor().extract(element,
                                             host=host,
                                             with_body_html=with_body_html,
                                             body_xpath=body_xpath,
                                             use_visiable_info=use_visiable_info)
        publish_time = TimeExtractor().extractor(element,
                                                 publish_time_xpath=publish_time_xpath,
                                                 normal_html=normal_html,
                                                 title=title,
                                                 content=content[0][1]['text'],
                                                 html=html,
                                                 npp_pt=self.article.publish_date
                                                 )
        text = content[0][1]['text']
        npp_text = self.article.text
        if npp_text and len(npp_text) > len(text):
            text = npp_text
        result = {'title': title,
                  'author': author,
                  'publish_time': publish_time,
                  'lang': lang,
                  'content': text,
                  'images': content[0][1]['images'],
                  'headmeta': headmeta,
                  'top_image': headmeta.pop('top_image'),
                  'website': headmeta.pop('host')
                  }
        if with_body_html or config.get('with_body_html', False):
            result['body_html'] = content[0][1]['body_html']
        return result


class ListPageExtractor:
    def extract(self, html, feature):
        normalize_html = normalize_text(html)
        element = html2element(normalize_html)
        extractor = ListExtractor()
        return extractor.extract(element, feature)

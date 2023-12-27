import re
import locale
import langid
from lxml import html


class LangExtractor:
    def __init__(self):
        self.name = "langid"
        # 用于提取语言代码的正则表达式模式
        self.langcode_pattern = re.compile(r'\b[a-zA-Z]{2}(?=([-_]|\b))')

    def language(self, response):
        try:
            root = html.fromstring(response)
        except ValueError:
            root = html.fromstring(response.encode("utf-8"))

        # 从不同的源提取语言
        lang = self.extract_from_attributes(root) or \
               self.extract_from_meta_tags(root) or \
               self.extract_from_articles(root) or \
               self.extract_from_body(root)

        if lang:
            lang = self.normalize_language(lang)

        return lang

    def extract_from_attributes(self, root):
        # 从 HTML 属性中提取语言代码
        lang = root.get('lang') or root.get('xml:lang')
        return lang

    def extract_from_meta_tags(self, root):
        # 从 meta 标签中提取语言代码
        lang = root.xpath('string(//meta[@name="language"]/@content)') or \
               root.xpath('string(//meta[@property="og:locale"]/@content)')
        return lang.strip() if lang else None

    def extract_from_articles(self, root):
        # 从文章中提取语言代码，选择最长的文章
        article_texts = [re.sub(r'\s+', ' ', article.text_content().strip()) for article in root.xpath('//article')]
        longest_article = max(article_texts, key=len, default='')
        return langid.classify(longest_article)[0] if longest_article else None

    def extract_from_body(self, root):
        # 从整个 HTML 主体中提取语言代码
        return langid.classify(root.text_content().strip())[0]

    def normalize_language(self, lang):
        # 规范化语言代码的输出
        matches = self.langcode_pattern.search(lang)
        if matches:
            return matches.group(0)
        else:
            normalized = locale.normalize(re.split(r'\s|;|,', lang.strip())[0])
            matches = self.langcode_pattern.search(normalized)
            return matches.group(0) if matches else None

# 高级用法
## 常用参数
- **排除干扰元素**:
  如果网页中有一些元素（如广告或评论）可能会干扰正文的提取，您可以使用 `noise_node_list` 参数指定这些元素的 XPath 来排除它们：

  ```python
  result = extractor.extract(html_content, noise_node_list=['//div[@class="ad"]'])
  ```

- **指定 XPath**:
  如果您知道网页中标题或作者的具体 XPath，可以直接指定这些 XPath 来提高提取的准确性：

  ```python
  result = extractor.extract(html_content, title_xpath='//h1/text()', author_xpath='//span[@class="author"]/text()')
  ```
## 其它参数
根据提供的源码，`extractor.extract` 方法是 `GeneralNewsExtractor` 类的一个核心功能，用于从 HTML 内容中提取新闻文章的关键信息。以下是 `extractor.extract` 方法的参数说明和可能的返回结果：

### 参数说明：

- `html`: 网页的 HTML 源码字符串。这是必需的参数，`extract` 方法将解析这个 HTML 来提取信息。
- `title_xpath` (可选): 一个 XPath 表达式，用于指定如何从 HTML 中提取标题。如果未提供，将使用默认的逻辑来提取标题。
- `author_xpath` (可选): 一个 XPath 表达式，用于指定如何从 HTML 中提取作者信息。如果未提供，将使用默认的逻辑来提取作者。
- `publish_time_xpath` (可选): 一个 XPath 表达式，用于指定如何从 HTML 中提取发布时间。如果未提供，将使用默认的逻辑来提取发布时间。
- `host` (可选): 网站的主机名或域名，用于构造完整的图片 URL 等。
- `body_xpath` (可选): 一个 XPath 表达式，用于指定从哪个部分的 HTML 中提取正文内容。如果未提供，将使用整个 HTML 文档。
- `noise_node_list` (可选): 一个 XPath 表达式列表，用于指定需要在提取前移除的干扰元素。这些元素可能会影响正文内容的准确性。
- `with_body_html` (可选): 一个布尔值，如果设置为 `True`，则方法会返回正文的 HTML 内容。
- `use_visiable_info` (可选): 一个布尔值，如果设置为 `True`，则方法会使用页面元素的可见性信息来辅助提取。

## 返回结果：

`extractor.extract` 方法返回一个字典，其中包含了以下可能的键值对：

- `title`: 新闻文章的标题，是一个字符串。
- `author`: 文章的作者，可能是一个字符串或字符串列表。
- `publish_time`: 文章的发布时间，可能是一个格式化的时间字符串或时间戳。
- `lang`: 文章内容的语言代码。
- `content`: 文章的正文内容，是一个字符串。
- `images`: 文章中引用的图片列表，每个元素是一个 URL 字符串。
- `headmeta`: 包含页面头部元数据的字典。
- `top_image`: 文章顶部的图片 URL，是一个字符串。
- `website`: 发布文章的网站名称或域名。

如果提取过程中发生错误或内容无法解析，方法可能会返回包含错误信息的字典，例如：

- `error`: 包含错误描述的字符串。

## 使用示例：

```python
extractor = GeneralNewsExtractor()
html_content = '这里是网页的HTML源码'

# 基本提取
result = extractor.extract(html_content)

# 带自定义参数的提取
result = extractor.extract(
    html_content,
    title_xpath='//h1/text()',
    author_xpath='//p[@class="author"]/text()',
    publish_time_xpath='//time[@class="publish-time"]/@datetime',
    noise_node_list=['//div[@class="comments"]', '//aside']
)

print(result)
```

请注意，具体的参数名称和返回值结构可能会根据 `xgne` 库的实际实现有所不同，上述说明基于提供的源码片段。在使用 `xgne` 库时，建议查阅最新的官方文档以获取准确的参数和返回结果信息。

## 注意事项

- 确保您使用的 HTML 源码是完整的，特别是对于动态加载内容的网页，可能需要使用工具（如 Selenium）来获取完整的 HTML。
- `xgne` 的提取效果可能因不同网站的网页结构而异，您可能需要根据具体情况调整参数。

以上就是 `xgne` 的基本安装和使用指南。您可以根据项目的具体需求，进一步探索 `xgne` 的高级功能和参数。
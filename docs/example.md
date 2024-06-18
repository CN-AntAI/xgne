# 使用 xgne

## 1. **导入 xgne**:
   在您的 Python 脚本或交互式环境中，首先导入 `xgne` 中的类：

   ```python
   from xgne import GeneralNewsExtractor
   ```

## 2. **创建 GeneralNewsExtractor 实例**:
   创建 `GeneralNewsExtractor` 类的实例：

   ```python
   extractor = GeneralNewsExtractor()
   ```

## 3. **提取网页内容**:
   使用 `extractor` 实例的 `extract` 方法来提取网页的新闻内容。您需要提供网页的 HTML 源码。例如：

   ```python
   html_content = '这里是网页的HTML源码'
   result = extractor.extract(html_content)
   print(result)
   ```

   `extract` 方法将返回一个包含网页信息的字典，可能包括 `title`（标题）、`content`（正文内容）、`author`（作者）、`publish_time`（发布时间）等字段。

## 4. **处理提取结果**:
   根据返回的字典结果，您可以获取所需的信息。例如，打印标题和正文：

   ```python
   print("Title:", result.get('title'))
   print("Content:", result.get('content'))
   ```

## 5. **自定义提取**:
   `extract` 方法还允许您通过参数自定义提取过程，例如指定标题或作者的 XPath，或者排除某些干扰元素的 XPath 等。

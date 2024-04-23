# #!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2023-12-24 15:26
# @Author : BruceLong
# @FileName: setup.py
# @Email   : 18656170559@163.com
# @Software: PyCharm
# @Blog ：http://www.cnblogs.com/yunlongaimeng/
from setuptools import setup, find_packages
import os

# 如果readme文件中有中文，那么这里要指定encoding='utf-8'，否则会出现编码错误
with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as readme:
    README = readme.read()

# 允许setup.py在任何路径下执行
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="xgne",
    version="0.0.9",
    packages=find_packages(),
    long_description=README,  # 详细描述（一般会写在README.md中）
    long_description_content_type="text/markdown",  # README.md中描述的语法（一般为markdown）
    author="BruceLong",
    license="MIT Licence",
    author_email="18656170559@163.com",
    include_package_data=True,
    platforms="any",
    install_requires=['wheel', 'w3lib', 'lxml', 'numpy', 'langid', 'pyyaml', 'newspaper3k', 'dateutils', 'parsel']
)

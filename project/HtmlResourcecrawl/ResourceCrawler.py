#!/usr/bin/python
# -*- coding:utf-8 -*-
import re


class Crawler(object):
    def __init__(self):
        pass

    @staticmethod
    def craw_resource_in_js(js):
        # 搜索所有图片文件引用的字符串
        re.search(r'', js, pattern=re.I)

        pass

    @staticmethod
    def craw_resource_in_css(css):
        pass

print(re.search(r'WWW', 'www.runoob.com\n', flags=re.I).string)

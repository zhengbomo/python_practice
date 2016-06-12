#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'bomo'

import os
import hashlib
import urllib
import urllib2


class Downloader(object):

    def __init__(self):
        pass

    @staticmethod
    def get_html(url, folder):

        content = Downloader.__get_file_content(url, folder)
        if not content:
            content = Downloader.__download(url)
            if content:
                # 保存到文件
                Downloader.__cache_url(url, content, folder)
            return content
        else:
            return content

    @staticmethod
    def __download(url):
        """下载url内容"""
        request = urllib2.Request(url)
        try:
            response = urllib2.urlopen(request)
            return response.read()
        except Exception, e:
            print str(e)
            return None

    @staticmethod
    def __get_file_content(url, folder):

        path = Downloader.__get_file_path(url, folder)
        if os.path.isfile(path):
            file_object = open(path)
            try:
                return file_object.read()
            finally:
                file_object.close()
        return None

    @staticmethod
    def __cache_url(url, html, folder):
        path = Downloader.__get_file_path(url, folder)
        output = open(path, 'w')
        output.write(html)
        output.close()

    @staticmethod
    def __get_file_path(url, folder):
        """返回缓存的路径"""
        name = Downloader.__hash(url)
        folder = os.path.join(os.getcwd(), '.html', folder)
        if not os.path.isdir(folder):
            os.mkdir(folder)
        return os.path.join(folder, name)

    @staticmethod
    def __hash(url):
        """对url做hash"""
        m2 = hashlib.md5()
        m2.update(url)
        return m2.hexdigest()




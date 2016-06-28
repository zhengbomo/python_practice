#!/usr/bin/python
# -*- coding:utf-8 -*-


import os
import shutil
import hashlib
import urllib
import urllib2


class Downloader(object):

    def __init__(self):
        pass

    @staticmethod
    def get_html(url, data, folder):
        file_url = url + data
        file_url = file_url.encode('UTF-8')
        file_url = urllib.quote(file_url)
        content = Downloader.__get_file_content(file_url, folder)
        if not content:
            content = Downloader.__download(url, data)
            if content:
                # 保存到文件
                Downloader.__cache_url(file_url, content, folder)
            return False, content
        else:
            return True, content

    @staticmethod
    def move_file(url, data, src, dst):
        file_url = url + data
        file_url = file_url.encode('UTF-8')
        file_url = urllib.quote(file_url)
        src = Downloader.__get_file_path(file_url, src)
        dst = Downloader.__get_file_path(file_url, dst)
        shutil.move(src, dst)


    @staticmethod
    def remove_file(url, data, folder):
        file_url = url + data
        file_url = file_url.encode('UTF-8')
        file_url = urllib.quote(file_url)
        src = Downloader.__get_file_path(file_url, folder)
        os.remove(src)


    @staticmethod
    def __download(url, data):
        """下载url内容"""
        request = urllib2.Request(url)
        try:
            response = urllib2.urlopen(request, data)
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
        html_folder = os.path.join(os.getcwd(), '.html')
        if not os.path.isdir(html_folder):
            os.mkdir(html_folder)

        folder = os.path.join(html_folder, folder)
        if not os.path.isdir(folder):
            os.mkdir(folder)

        return os.path.join(folder, name)

    @staticmethod
    def __hash(url):
        """对url做hash"""
        m2 = hashlib.md5()
        m2.update(url)
        return m2.hexdigest()




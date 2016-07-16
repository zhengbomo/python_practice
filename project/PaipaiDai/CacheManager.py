#!/usr/bin/python
# -*- coding:utf-8 -*-
import hashlib
import os
import datetime


class CacheManager(object):
    @staticmethod
    def get(url):
        path = CacheManager.__md5(url)
        path = CacheManager.get_path(path)
        return CacheManager.open(path)

    @staticmethod
    def set(url, data):
        path = CacheManager.__md5(url)
        path = CacheManager.get_path(path)
        return CacheManager.save(path, data)

    @staticmethod
    def open(path):
        if os.path.isfile(path):
            f = open(path, 'r')
            content = f.read()
            f.close()
            return content
        else:
            return None

    @staticmethod
    def save(path, data):
        if os.path.isfile(path):
            os.remove(path)
        f = open(path, 'w')
        f.write(data)
        f.close()

    @staticmethod
    def get_path(path):
        folder = os.getcwd()
        folder = os.path.join(folder, '.html')
        if not os.path.isdir(folder):
            os.mkdir(folder)
        folder = os.path.join(folder, CacheManager.__get_date())
        if not os.path.isdir(folder):
            os.mkdir(folder)

        return os.path.join(folder, path)

    @staticmethod
    def __get_date():
        return str(datetime.date.today())

    @staticmethod
    def __md5(url):
        """对url做hash"""
        m2 = hashlib.md5()
        m2.update(url)
        return m2.hexdigest()
#!/usr/bin/python
# -*- coding:utf-8 -*-
import sqlite3
import threading


class WeiboDb(object):
    def __init__(self):
        self.path = 'spider.db'
        self.mutex = threading.Lock()           # 线程锁,解决同步问题

        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.text_factory = str
        self.create_table()
        pass

    def create_table(self):
        pass

    def insert_use_info(self, user_info):
        pass

    def insert_user_status(self, statuses):
        for status in statuses:
            pass



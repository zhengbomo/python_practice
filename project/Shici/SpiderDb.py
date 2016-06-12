#!/usr/bin/python
# -*- coding:utf-8 -*-

__author__ = 'bomo'

import sqlite3
import threading


class SpiderDb(object):
    def __init__(self):
        self.path = 'spider.db'
        self.mutex = threading.Lock()

        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.text_factory = str
        self.create_table()

    def create_table(self):
        cu = self.connection.cursor()
        if self.mutex.acquire():
            # url 列表表（id, type, url, downloaded）
            sql = 'create table IF NOT EXISTS urls(id integer primary key, ' \
                  'type INTEGER INTEGER DEFAULT 0, ' \
                  'subtype Text, ' \
                  'url Text UNIQUE, ' \
                  'analyzed INTEGER INTEGER DEFAULT 0)'
            cu.execute(sql)

            # 获取失败表（url，reason, type）
            sql = 'create table IF NOT EXISTS errors(id integer primary key, ' \
                  'type INTEGER INTEGER DEFAULT 0, message Text, url Text, reason Text)'
            cu.execute(sql)

            # 诗词主表（内容，朝代，作者）
            sql = 'create table IF NOT EXISTS poems(id integer primary key, ' \
                  'type INTEGER INTEGER DEFAULT 0, title Text, content Text, ' \
                  'dynasty Text, author Text, authorurl, url Text)'
            cu.execute(sql)

            # 分析表（内容）
            sql = """create table IF NOT EXISTS infomation(id integer primary key,
                                type INTEGER,
                                title Text,
                                summary Text,
                                content Text,
                                url Text,
                                analyzed INTEGER DEFAULT 0)
                  """
            cu.execute(sql)

            # 相关资料关联表id, value
            sql = 'create table IF NOT EXISTS reactive(id integer primary key, key Text, value Text, type)'
            cu.execute(sql)

            # 作者表
            sql = 'create table IF NOT EXISTS author(id integer primary key, name Text, content Text, avatar Text, url Text)'
            cu.execute(sql)

            self.connection.commit()
            cu.close()

            self.mutex.release()

    def insert_url(self, url, type_):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            cu.execute('select count(*) from urls WHERE url=?', (url,))
            result = cu.fetchone()
            if result[0] == 0:
                # 插入
                cu.execute(u'INSERT INTO urls (type, url) VALUES (?, ?)', (type_, url))
                self.connection.commit()
            cu.close()
            self.mutex.release()

    def insert_urls(self, urls, type_):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            for url in urls:
                cu.execute('select count(*) from urls WHERE url=?', (url,))
                result = cu.fetchone()
                if result[0] == 0:
                    # 插入
                    cu.execute(u'INSERT INTO urls (type, url) VALUES (?, ?)', (type_, url))

            self.connection.commit()
            cu.close()
            self.mutex.release()

    def select_unanalyzed_url(self, type_):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            cu.execute('select * from urls WHERE (analyzed IS NULL OR analyzed=0) and type=? LIMIT 1', (type_,))
            result = cu.fetchall()
            cu.close()
            self.mutex.release()
            if len(result) > 0:
                return result[0]
            else:
                return None

    def url_analyzed(self, url):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            cu.execute('select count(*) from urls WHERE url=? and analyzed=?', (url, 1))
            result = cu.fetchone()
            cu.close()
            self.mutex.release()
            return result[0] > 0

    def url_count(self):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            cu.execute('select count(*) from urls')
            result = cu.fetchone()
            cu.close()
            self.mutex.release()
            return result[0]

    def update_url(self, url):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            cu.execute('update urls set analyzed=1 WHERE url=?', (url,))
            self.connection.commit()
            cu.close()
            self.mutex.release()

    def insert_error(self, message, t, reason, url):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            cu.execute('INSERT INTO errors(type, message, url, reason) VALUES (?,?,?,?)', (t, message, url, reason))
            self.connection.commit()
            cu.close()
            self.mutex.release()

    def select_error(self, types):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            types = map(str, types)
            types = ','.join(types)
            cu.execute('SELECT * FROM errors WHERE type in (%s)' % types)
            result = cu.fetchall()
            cu.close()
            self.mutex.release()
            return result

    def insert_infomations(self, type_, url, infos):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            for info in infos:
                # 插入关联表
                cu.execute('insert into reactive (type, key, value) values (?,?,?)',
                           (type_, url, info['url']))

                cu.execute('select count(*) from urls WHERE url=?', (info['url'],))
                result = cu.fetchone()
                if result[0] == 0:
                    cu.execute('INSERT INTO infomation(type, title, summary, content, url) VALUES (?,?,?,?,?)',
                               (info['type'], info['title'], info['summary'], info['content'], info['url']))
            self.connection.commit()
            cu.close()
            self.mutex.release()

    def update_infomationurl(self, url, content):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            cu.execute('update infomation set content=?, analyzed=1 WHERE url=?', (content, url))
            self.connection.commit()
            cu.close()
            self.mutex.release()

    def infomation_count(self):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            cu.execute('select count(*) from infomation where analyzed=1')
            result = cu.fetchone()
            cu.close()
            self.mutex.release()
            return result[0]

    def infomation_exists(self, url):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            cu.execute('select count(*) from infomation WHERE url=?', (url,))
            result = cu.fetchone()
            cu.close()
            self.mutex.release()
            return result[0] > 0

    def select_unanalyzed_infomation(self):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            cu.execute('select * from infomation WHERE analyzed=0 LIMIT 1')
            result = cu.fetchone()
            cu.close()
            self.mutex.release()
            return result

    def delete_infomation(self, url):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            cu.execute('delete from infomation WHERE url=?', (url,))
            result = cu.fetchone()
            cu.close()
            self.connection.commit()
            self.mutex.release()
            return result

    def select_authors(self):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            cu.execute('select DISTINCT authorurl from poems')
            result = cu.fetchall()
            cu.close()
            self.mutex.release()
            return result

    def insert_poem(self, poem_content):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            cu.execute('select count(*) from poems WHERE url=?', (poem_content['url'],))

            result = cu.fetchone()
            if result[0] == 0:
                cu.execute('INSERT INTO poems(type, title, content, dynasty, author, authorurl, url) VALUES (?,?,?,?,?,?,?)',
                           (poem_content['type'], poem_content['title'], poem_content['content'], poem_content[
                               'dynasty'], poem_content['author'], poem_content['authorurl'], poem_content['url']))
                self.connection.commit()
            cu.close()
            self.mutex.release()

    def poem_exists(self, url):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            cu.execute('select count(*) from poems WHERE url=?', (url,))

            result = cu.fetchone()
            cu.close()
            self.mutex.release()
            return result[0] > 0

    def poem_count(self):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            cu.execute('select count(*) from poems')
            result = cu.fetchone()
            cu.close()
            self.mutex.release()
            return result[0]

    def insert_author(self, author):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            cu.execute('select count(*) from poems WHERE url=?', (author['url'],))

            result = cu.fetchone()
            if result[0] == 0:
                cu.execute('INSERT INTO author(name, content, avatar, url) VALUES (?,?,?,?)',
                           (author['name'], author['content'], author[
                               'avatar'], author['url']))
                self.connection.commit()
            cu.close()
            self.mutex.release()

    def author_exists(self, url):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            cu.execute('select count(*) from author WHERE url=?', (url,))

            result = cu.fetchone()
            cu.close()
            self.mutex.release()
            return result[0] > 0






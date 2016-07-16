#!/usr/bin/python
# -*- coding:utf-8 -*-
import sqlite3
import MySQLdb

class ErrorType:
    PageList = 1
    User = 2
    Detail = 3


class Database(object):
    def __init__(self):
        try:
            self.conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="111111", db="PaipaiDai", charset="utf8")
            self.__create_table()
        except:
            print "数据库连接失败"

    def __create_table(self):
        cursor = self.conn.cursor()

        # 列表表
        # cursor.execute("CREATE TABLE IF NOT EXISTS test (id int(11) NOT NULL AUTO_INCREMENT, "\
        #                "url Text, "\
        #                "PRIMARY KEY (id)"\
        #                ");")
        # self.conn.commit()

        # 详情表
        # cursor.execute('')

        # 用户表
        cursor.execute('Create table if not EXISTS users (id int not null AUTO_INCREMENT, '
                       'userid text,'
                       'outcredit text,'
                       'incredit text,'
                       'gender text,'
                       'age int,'
                       'jobtype text,'
                       'studyvalid int,'		# 学历认证
                       'hukouvalid int,'		# 户口认证
                       'renbankcredit int,'		# 人行征信认证
                       'registtime text,'

                       'PRIMARY KEY (id)'
                       ')')

        self.conn.commit()

        cursor.close()
        pass

    def insert_list(self, data):
        # 入库之前需要判断
        pass

    def insert_detail(self, detail):
        pass

    def insert_user_info(self, user_info):
        pass

    def insert_error(self, url, error_type):
        pass

    def get_errors(self, error_type):
        pass

    def get_uncrawl_detail(self):
        pass

    def get_uncrawl_user(self):
        pass

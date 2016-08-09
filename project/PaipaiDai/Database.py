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
        except Exception, e:
            print "数据库连接失败", e

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

        # 散标概览表
        cursor.execute('Create table if not EXISTS loans (id int not null AUTO_INCREMENT, '
               'loan_id varchar(16),'
               'amount real,'
               'lilv real,'
               'title text,'
               'user_url text,'
               'rankcode text,'         # 魔镜等级
               'detail_url text,'		# 学历认证
               'limit_time int,'		# 户口认证
               'rank int,'		        # 人行征信认证
               'PRIMARY KEY (id),'
               'INDEX (loan_id)'
               ')')

        # 审核表
        cursor.execute('Create table if not EXISTS shenhes (id int not null AUTO_INCREMENT, '
               'username varchar(32),'
               'title text,'
               'PRIMARY KEY (id),'
               'INDEX (username)'
               ')')

        # 散标详情表
        cursor.execute('Create table if not EXISTS userinfo (id int not null AUTO_INCREMENT, '
               'username varchar(32),'
               'user_url text,'

               'rankcode varchar(32),'
               'rank integer,'

               'wenhua text,'
               'gouche varchar(32),'
               'age integer,'
               'zhuzhai text,'
               'gender nvarchar(8),'
               'jiehun nvarchar(8),'

               'total_borrow_amount real,'
               'total_daishou real,'
               'total_daihuan real,'

               'total_huanqing integer,'
               'total_yuqi_16 integer,'
               'total_yuqi_15 integer,'

               'regist_time real,'
               'first_borrow_time real,'

               'yuqi_days real,'
               'tiqian_days real,'

               'PRIMARY KEY (id),'
               'INDEX (username)'
               ')')

        self.conn.commit()

        cursor.close()
        pass

    def insert_loans(self, loans):
        cursor = self.conn.cursor()
        for loan in loans:
            cursor.execute('select count(*) from loans where loan_id = %s', (loan['loan_id'],))
            result = cursor.fetchone()
            if result[0] == 0:
                params = [loan['loan_id'], loan['amount'], loan['lilv'], loan['title'], loan['user_url'],
                          loan['rankcode'], loan['detail_url'], loan['limit_time'], loan['rank']]
                cursor.execute('insert into loans(loan_id, amount, lilv, title, user_url, rankcode, detail_url, limit_time, rank) values'
                               '(%s, %s, %s, %s, %s, %s, %s, %s, %s)', params)
        self.conn.commit()
        cursor.close()

    # 从散标列表获取散标详情url
    def get_loan_urls_from_loans(self, count):
        cu = self.conn.cursor()
        if count > 0:
            sql = """
                SELECT detail_url FROM loans l
                where not exists (
                    select * from userinfo u
                    where u.user_url = l.user_url and u.yuqi_days is null
                )
                limit %s, %s
            """
            cu.execute(sql, [0, count])
        else:
            sql = """
                SELECT detail_url FROM loans l
                where not exists (
                    select * from userinfo u
                    where u.user_url = l.user_url and u.yuqi_days is null
                )
            """
            cu.execute(sql, [])
        result = cu.fetchall()
        cu.close()
        return result

    def insert_user_info(self, info):
        username = info['username']
        user_url = info['user_url']
        yuqi_days = info['yuqi_days']
        tiqian_days = info['tiqian_days']


        if username and user_url:
            cursor = self.conn.cursor()

            cursor.execute('select count(*) from userinfo where username = %s', [username])
            result = cursor.fetchone()
            if result[0] == 0:
                cursor.execute('insert into userinfo(username, user_url) values(%s, %s)', [username, user_url])

            tongji_info = info['tongji_info']
            params = [tongji_info.get('total_borrow_amount'), tongji_info.get('total_huanqing'), tongji_info.get(
                'total_daishou'), tongji_info.get('total_yuqi_16'), tongji_info.get('total_yuqi_15'), tongji_info.get(
                'total_daihuan'), tongji_info.get('regist_time'), tongji_info.get('first_borrow_time'), username]

            cursor.execute('update userinfo set total_borrow_amount=%s, total_huanqing=%s, total_daishou=%s, '
                           'total_yuqi_16=%s, total_yuqi_15=%s, total_daihuan=%s, regist_time=%s, '
                           'first_borrow_time=%s where username=%s', params)

            cursor.execute('update userinfo set yuqi_days=%s, tiqian_days=%s where username=%s', [yuqi_days,
                                                                                                  tiqian_days, username])

            borrower_info = info['borrower_info']

            wenhua = borrower_info.get(u'文化程度')
            gouche = borrower_info.get(u'是否购车')
            age = borrower_info.get(u'年龄')
            if age:
                age = int(age)

            zhuzhai = borrower_info.get(u'住宅状况')
            gender = borrower_info.get(u'性别')
            jiehun = borrower_info.get(u'婚姻情况')

            params = [wenhua, gouche, zhuzhai, age, gender, jiehun, username]
            cursor.execute('update userinfo set wenhua=%s, gouche=%s, zhuzhai=%s, age=%s, gender=%s, jiehun=%s where '
                           'username=%s', params)

            shenhe_infos = info['shenhe_infos']
            for shenhe_info in shenhe_infos:
                params = [username, shenhe_info]
                cursor.execute('select count(*) from shenhes where username = %s and title = %s', params)
                result = cursor.fetchone()
                if result[0] == 0:
                    cursor.execute('insert into shenhes(username, title) values'
                                   '(%s, %s)', params)

            self.conn.commit()
            cursor.close()

    def insert_error(self, url, error_type):
        pass

    def get_errors(self, error_type):
        pass

    def get_uncrawl_detail(self):
        pass

    def get_empty_user_urls(self, count=0):
        cu = self.conn.cursor()
        if count > 0:
            sql = """
                select user_url from userinfo
                where wenhua is null
                limit %s, %s
            """
            cu.execute(sql, [0, count])
        else:
            sql = """
                select user_url from userinfo
                where wenhua is null
            """
            cu.execute(sql, [])
        result = cu.fetchall()
        cu.close()
        return result

    def get_most_tiqian_cd_user_urls(self, count=10):
        cu = self.conn.cursor()
        if count > 0:
            sql = """
                select user_url, tiqian_days from userinfo
                where rankcode='C' or rankcode='D'
                order by tiqian_days
                limit %s, %s
            """
            cu.execute(sql, [0, count])
        else:
            sql = """
                select user_url, tiqian_days from userinfo
                where rankcode='C' or rankcode='D'
                order by tiqian_days
            """
            cu.execute(sql, [])
        result = cu.fetchall()
        cu.close()
        return result

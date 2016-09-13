#!/usr/bin/python
# -*- coding:utf-8 -*-
import sqlite3
import MySQLdb
import warnings

# 忽略警告
warnings.filterwarnings("ignore")


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

        # 我的投标
        cursor.execute('Create table if not EXISTS my_loan (id int not null AUTO_INCREMENT, '
               'url text,'
               'buy_date real,'
               'amount real,'
               'loan_id text,'
               'finished integer,'
               'lilv real,'
               'PRIMARY KEY (id)'
               ')')

        # 我的每日利率任务
        cursor.execute('Create table if not EXISTS lilv_task (id int not null AUTO_INCREMENT, '
               'create_date real,'
               'normal_lilv real,'              # 综合利率
               'finished_lilv real,'            # 完成利率
               'unfinished_lilv real,'          # 未完成利率
               'total_buy real,'                # 总投资
               'PRIMARY KEY (id)'
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

    def get_empty_lilv_user_url(self):
        cursor = self.conn.cursor()
        cursor.execute('select user_url from userinfo where weight_lilv is null limit 0, 1')
        result = cursor.fetchone()
        if result:
            return result[0]

        else:
            return None

    # 获取未分析的标url
    def get_un_analyzed_bid_user_loan_url(self):
        cursor = self.conn.cursor()
        cursor.execute('select detail_url from loans where has_analyze_for_bid_users is null or '
                       'has_analyze_for_bid_users = 0 limit 0, 1')
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
     # 获取未分析的标url
    def set_un_analyzed_bid_user_loan_url(self, url, flag=True):
        cursor = self.conn.cursor()
        cursor.execute('update loans set has_analyze_for_bid_users=%s where detail_url=%s', [flag, url])
        self.conn.commit()
        cursor.close()

    def insert_user_urls(self, urls):
        cursor = self.conn.cursor()

        cursor.execute('select user_url from userinfo where user_url in (%s)' % (','.join(urls)))
        result = cursor.fetchone()

        for url in urls:
            cursor.execute('select count(*) from userinfo where user_url = %s', [url])
            result = cursor.fetchone()
            if result[0] == 0:
                cursor.execute('insert into userinfo(user_url) values(%s)', [url])
        self.conn.commit()
        cursor.close()


    def insert_user_with_weight_lilv(self, url, lilv):
        cursor = self.conn.cursor()
        cursor.execute('select count(*) from userinfo where user_url = %s', [url])
        result = cursor.fetchone()
        if result[0] == 0:
            cursor.execute('insert into userinfo(user_url, weight_lilv) values(%s, %s)', [url, lilv])
        else:
            cursor.execute('update userinfo set weight_lilv=%s where user_url=%s', [lilv, url])
        self.conn.commit()
        cursor.close()


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

    # 我的投标列表
    def insert_my_loan(self, url, date, amount, loan_id):
        cursor = self.conn.cursor()
        cursor.execute('select count(*) from my_loan where url=%s', [url])
        result = cursor.fetchone()
        if result[0] == 0:
            cursor.execute('insert into my_loan(url, buy_date, amount, loan_id) values(%s, %s, %s, %s)', [url, date,
                                                                                                          amount, loan_id])
        self.conn.commit()
        cursor.close()

     # 我的投标列表
    def insert_my_loans(self, my_loans):
        cursor = self.conn.cursor()
        for loan in my_loans:
            url = loan['url']
            date = loan['date']
            amount = loan['amount']
            loan_id = loan['loan_id']

            cursor.execute('select count(*) from my_loan where url=%s', [url])
            result = cursor.fetchone()
            if result[0]:
                cursor.execute('select sum(amount) from my_loan where url=%s and buy_date!=%s', [url, date])
                result = cursor.fetchone()
                if result[0]:
                    amount += result[0]
                    cursor.execute('update my_loan set amount=%s where url = %s', [amount, url])
                else:
                    cursor.execute('update my_loan set amount=%s where url = %s', [amount, url])
            else:
                cursor.execute('insert into my_loan(url, buy_date, amount, loan_id) values(%s, %s, %s, %s)', [url, date,
                                                                                              amount, loan_id])
        self.conn.commit()
        cursor.close()


    def get_my_loan(self, index, count):
        cu = self.conn.cursor()
        if count > 0:

            sql = """
                select * from my_loan
                where finished is null or lilv is null or finished = 0
                order by buy_date
                limit %s, %s
            """
            cu.execute(sql, [index, count])
        else:
            sql = """
                select * from my_loan
                where finished is null or lilv is null or finished = 0
                order by buy_date
            """
            cu.execute(sql, [])
        result = cu.fetchall()
        cu.close()
        return result

    def update_my_loan(self, url, finished, lilv):
        cursor = self.conn.cursor()
        if finished:
            finished = 1
        else:
            finished = 0
        cursor.execute('update my_loan set finished = %s, lilv=%s where url = %s', [finished, lilv, url])
        self.conn.commit()
        cursor.close()

    # 我的每日利率任务
    def lilv_task_exist(self, date):
        cursor = self.conn.cursor()

        cursor.execute('select count(*) from lilv_task where create_date = %s', [date])
        result = cursor.fetchone()
        cursor.close()
        if result[0]:
            return True
        else:
            return False

    # 我的每日任务
    def insert_lilv_task(self, date, normal_lilv, finished_lilv, unfinished_lilv):
        cursor = self.conn.cursor()
        cursor.execute('insert into lilv_task(create_date, normal_lilv, finished_lilv, unfinished_lilv) values(%s, '
                       '%s, %s, %s)', [date, normal_lilv, finished_lilv, unfinished_lilv])
        self.conn.commit()
        cursor.close()

    # 更新我的每日任务
    def update_lilv_task(self):
        sql = """
insert into lilv_task (create_date, create_date2, normal_lilv, finished_lilv, unfinished_lilv, total_buy, current_buy)

SELECT
UNIX_TIMESTAMP(CURDATE()) as create_date,

CURDATE() as create_date2,

(select avg(lilv) from my_loan
where `finished` is not null
order by lilv) as normal_lilv,

(select avg(lilv) from my_loan
where `finished` = 1
order by lilv) as finished_lilv,

(select avg(lilv) from my_loan
where `finished` = 0
order by lilv) as unfinished_lilv,

(select sum(`amount`) from my_loan) as total_buy,

(select sum(amount) from my_loan where finished = 0) as current_buy

WHERE NOT EXISTS(
      SELECT *
      FROM lilv_task
      WHERE create_date = UNIX_TIMESTAMP(CURDATE()))
                """
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()

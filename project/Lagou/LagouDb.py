#!/usr/bin/python
# -*- coding:utf-8 -*-
import sqlite3
import threading


class LagouDb(object):
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
            sql = 'create table IF NOT EXISTS jobs(id INTEGER PRIMARY KEY, ' \
                  'type INTEGER DEFAULT 0, ' \
                  'companyId INTEGER, ' \
                  'companyName Text, ' \
                  'positionName Text, ' \
                  'positionType Text, ' \
                  'workYear Text, ' \
                  'education Text, ' \
                  'jobNature Text, ' \
                  'createTime Text, ' \
                  'companyShortName Text, ' \
                  'approve INTEGER, ' \
                  'city Text, ' \
                  'positionFirstType Text, ' \
                  'positionId INTEGER, ' \
                  'salary Text, ' \
                  'positionAdvantage Text, ' \
                  'companyLogo Text, ' \
                  'industryField Text, ' \
                  'financeStage Text, ' \
                  'companyLabelList Text, ' \
                  'district Text, ' \
                  'deliverCount INTEGER, ' \
                  'score INTEGER, ' \
                  'leaderName Text, ' \
                  'companySize Text, ' \
                  'randomScore INTEGER, ' \
                  'formatCreateTime Text, ' \
                  'countAdjusted INTEGER, ' \
                  'adjustScore INTEGER, ' \
                  'relScore INTEGER, ' \
                  'calcScore INTEGER, ' \
                  'orderBy INTEGER, ' \
                  'showOrder INTEGER, ' \
                  'haveDeliver INTEGER, ' \
                  'adWord INTEGER, ' \
                  'imstate Text, ' \
                  'createTimeSort INTEGER, ' \
                  'positonTypesMap Text, ' \
                  'hrScore INTEGER, ' \
                  'flowScore INTEGER, ' \
                  'showCount INTEGER, ' \
                  'pvScore REAL, ' \
                  'plus Text, ' \
                  'businessZones Text, ' \
                  'publisherId INTEGER, ' \
                  'loginTime INTEGER, ' \
                  'appShow INTEGER, ' \
                  'totalCount INTEGER, ' \
                  'searchScore INTEGER)'
            cu.execute(sql)

            # 创建key关联表
            sql = 'CREATE TABLE IF NOT EXISTS keyjobs(id INTEGER PRIMARY KEY, ' \
                  'key INTEGER,'\
                  'value INTEGER) '
            cu.execute(sql)

            # 创建扩展列
            sql = 'PRAGMA table_info("jobs")'
            cu.execute(sql)
            columns = cu.fetchall()
            columns = map(lambda c: c[1], columns)
            if u'maxsalary' not in columns:
                sql = 'ALTER TABLE jobs ADD COLUMN maxsalary INTEGER'
                cu.execute(sql)
            if u'minsalary' not in columns:
                sql = 'ALTER TABLE jobs ADD COLUMN minsalary INTEGER'
                cu.execute(sql)
            if u'midsalary' not in columns:
                sql = 'ALTER TABLE jobs ADD COLUMN midsalary INTEGER'
                cu.execute(sql)

            self.connection.commit()
            cu.close()

            self.mutex.release()

    def insert_jobs(self, jobs):
        sql = '''INSERT INTO jobs
(type,
companyId,
companyName,
positionName,
positionType,
workYear,
education,
jobNature,
createTime,
companyShortName,
approve,
city,
positionFirstType,
positionId,
salary,
positionAdvantage,
companyLogo,
industryField,
financeStage,
companyLabelList,
district,
deliverCount,
score,
leaderName,
companySize,
randomScore,
formatCreateTime,
countAdjusted,
adjustScore,
relScore,
calcScore,
orderBy,
showOrder,
haveDeliver,
adWord,
imstate,
createTimeSort,
positonTypesMap,
hrScore,
flowScore,
showCount,
pvScore,
plus,
businessZones,
publisherId,
loginTime,
appShow,
totalCount,
searchScore) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
'''
        if self.mutex.acquire():
            cu = self.connection.cursor()

            for job in jobs:
                cu.execute('select count(*) from jobs WHERE positionId=?', (job['positionId'],))
                result = cu.fetchone()
                if result[0] == 0:
                    # 插入
                    cu.execute(sql, (
                        1,
                        job['companyId'],
                        job['companyName'],
                        job['positionName'],
                        job['positionType'],
                        job['workYear'],
                        job['education'],
                        job['jobNature'],
                        job['createTime'],
                        job['companyShortName'],
                        job['approve'],
                        job['city'],
                        job['positionFirstType'],
                        job['positionId'],
                        job['salary'],
                        job['positionAdvantage'],
                        job['companyLogo'],
                        job['industryField'],
                        job['financeStage'],
                        str(job['companyLabelList']),
                        job['district'],
                        job['deliverCount'],
                        job['score'],
                        job['leaderName'],
                        job['companySize'],
                        job['randomScore'],
                        job['formatCreateTime'],
                        job['countAdjusted'],
                        job['adjustScore'],
                        job['relScore'],
                        job['calcScore'],
                        job['orderBy'],
                        job['showOrder'],
                        job['haveDeliver'],
                        job['adWord'],
                        job['imstate'],
                        job['createTimeSort'],
                        job['positonTypesMap'],
                        job['hrScore'],
                        job['flowScore'],
                        job['showCount'],
                        job['pvScore'],
                        job['plus'],
                        str(job['businessZones']),
                        job['publisherId'],
                        job['loginTime'],
                        job['appShow'],
                        job['totalCount'],
                        job['searchScore']
                    ))
            self.connection.commit()
            cu.close()
            self.mutex.release()

    def select_jobs(self, nomidsalary=False):
        cu = self.connection.cursor()
        if nomidsalary:
            cu.execute('select * from jobs where midsalary IS NULL')
        else:
            cu.execute('select * from jobs')
        result = cu.fetchall()
        cu.close()
        return result

    def update_job(self, id, minsalary, midsalary, maxsalary):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            cu.execute('update jobs set minsalary=?, midsalary=?, maxsalary=? WHERE id=?', (minsalary, midsalary,
                                                                                            maxsalary, id))
            self.connection.commit()
            cu.close()
            self.mutex.release()

    def associate_key_job(self, key, positionids):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            for positionid in positionids:
                cu.execute('select count(*) from keyjobs WHERE key=? and value=?', (key, positionid))
                result = cu.fetchone()
                if result[0] == 0:
                    cu.execute('insert into keyjobs(key, value) values(?,?)', (key, positionid))

            self.connection.commit()
            cu.close()
            self.mutex.release()

    def key_persent(self, count=0):
        cu = self.connection.cursor()
        if count > 0:
            sql = 'select key, count(value) as count from keyjobs group by key order by count desc limit ?'
            cu.execute(sql, (count,))
        else:
            sql = 'select key, count(value) as count from keyjobs group by key order by count desc'
            cu.execute(sql)
        result = cu.fetchall()
        cu.close()
        return result

    def key_persent_for_city(self, city, count=0):
        cu = self.connection.cursor()
        if count > 0:
            sql = 'select b.key, count(b.value) as count from jobs a, keyjobs as b where a.positionId = b.value and a.city=? group by ' \
                  'key order by count desc limit ?'
            cu.execute(sql, (city, count))
        else:
            sql = 'select b.key, count(b.value) as count from jobs a, keyjobs as b where a.positionId = b.value and a.city=? group by ' \
                  'key order by count desc'
            cu.execute(sql, (city,))
        result = cu.fetchall()
        cu.close()
        return result

    def high_salary(self, count=0):
        cu = self.connection.cursor()
        if count > 0:
            sql = 'select b.key, avg(a.midsalary) salary from jobs as a, keyjobs as b where a.positionid = b.value ' \
                  'group by b.key order by salary desc limit ?';
            cu.execute(sql, (count,))
        else:
            sql = 'select b.key, avg(a.midsalary) salary from jobs as a, keyjobs as b where a.positionid = b.value ' \
                  'group by b.key order by salary desc'
            cu.execute(sql)
        result = cu.fetchall()
        cu.close()
        return result


    def high_salary(self, city, count=0, mincount=10):
        cu = self.connection.cursor()
        if count > 0:
            if city:
                sql = 'select b.key, avg(a.midsalary) salary, count(*) as count from jobs as a, keyjobs as b where a.positionid = b.value ' \
                      'and a.city=? group by b.key having count > ? order by salary desc limit ?';
                cu.execute(sql, (city, mincount, count))
            else:
                sql = 'select b.key, avg(a.midsalary) salary, count(*) as count from jobs as a, keyjobs as b where a.positionid = b.value ' \
                      'group by b.key having count > ? order by salary desc limit ?';
                cu.execute(sql, (mincount, count))
        else:
            if city:
                sql = 'select b.key, avg(a.midsalary) salary, count(*) as scount from jobs as a, keyjobs as b where a.positionid = b.value ' \
                      'and a.city=? group by b.key having count > ? order by salary desc';
                cu.execute(sql, (city, mincount))
            else:
                sql = 'select b.key, avg(a.midsalary) salary, count(*) as scount from jobs as a, keyjobs as b where a.positionid = b.value ' \
                      'group by b.key having count > ? order by salary desc';
                cu.execute(sql, (mincount,))
        result = cu.fetchall()
        cu.close()
        return result

    def salary_in_city_by_key(self, key, count=0, mincount=5):
        cu = self.connection.cursor()
        if count > 0:
            if key:
                sql = 'select a.city, avg(a.midsalary) salary, count(a.midsalary) as count from jobs as a, keyjobs as b ' \
                      'where a.positionid = b.value and b.key=? group by a.city having count > ? order by salary desc limit ?'
                cu.execute(sql, (key, mincount, count))
            else:
                sql = 'select a.city, avg(a.midsalary) salary, count(a.midsalary) as count from jobs as a, keyjobs as b ' \
                      'where a.positionid = b.value group by a.city having count > ? order by salary desc limit ?'
                cu.execute(sql, (mincount, count))
        else:
            if key:
                sql = 'select a.city, avg(a.midsalary) salary, count(a.midsalary) as count from jobs as a, keyjobs as b ' \
                      'where a.positionid = b.value and b.key=? group by a.city having count > ? order by salary desc'
                cu.execute(sql, (key, mincount))
            else:
                sql = 'select a.city, avg(a.midsalary) salary, count(a.midsalary) as count from jobs as a, keyjobs as ' \
                      'where a.positionid = b.value group by a.city having count > ? order by salary desc'
                cu.execute(sql, (mincount,))
        result = cu.fetchall()
        cu.close()
        return result

    def adapt_job_city(self):
        if self.mutex.acquire():
            cu = self.connection.cursor()
            sql = u'select distinct city from jobs where city like "%市"'
            cu.execute(sql)
            citys = cu.fetchall()
            for city in citys:
                sql = "update jobs set city=? where city=?"
                cu.execute(sql, (city['city'].rstrip('市'), city['city']))
            self.connection.commit()
            cu.close()
            self.mutex.release()


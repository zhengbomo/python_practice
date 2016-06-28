#!/usr/bin/python
# -*- coding:utf-8 -*-
from LagouDb import LagouDb


class Analyzer(object):
    def __init__(self):
        self.db = LagouDb()

    # 统计最受欢迎的工作
    @staticmethod
    def get_popular_jobs(since=None):
        if since:
            pass
        else:
            pass

    # 统计职位在不同城市的薪资情况
    def get_salary_in_city(self, key, count, mincount=10):
        result = self.db.salary_in_city_by_key(key, count, mincount)
        kv = {}
        for i in result:
            if i['count'] >= 5:
                # 过滤数量小于5的城市
                k = '{0} ({1})'.format(i['city'], i['count'])
                kv[k] = i['salary']
        return kv

    # 统计工资最高的工作
    def get_high_salary_jobs(self, city, count, mincount=10):
        result = self.db.high_salary(city, count, mincount=mincount)
        kv = {}
        for i in result:
            k = '{0} ({1})'.format(i['key'], i['count'])
            kv[k] = i['salary']
        return kv

    # 关键字搜索结果比例
    def key_persent(self, city, count):
        if city:
            result = self.db.key_persent_for_city(city, count)
        else:
            result = self.db.key_persent(count)
        kv = {}
        for i in result:
            k = '{0} ({1})'.format(i['key'], i['count'])
            kv[k] = i['count']
        return kv

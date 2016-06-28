#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import json
from time import sleep

import re

from Downloader import Downloader
from LagouDb import LagouDb


class Spider(object):
    def __init__(self):
        self.db = LagouDb()

    def get_types(self):
        msg = '''
            后端开发
Java Python PHP .NET C# C++ C VB Delphi Perl Ruby Hadoop Node.js 数据挖掘 自然语言处理 搜索算法 精准推荐 全栈工程师 Go ASP Shell 后端开发其它
移动开发
HTML5 Android iOS WP 移动开发其它
前端开发
web前端 Flash html5 JavaScript U3D COCOS2D-X 前端开发其它
测试
测试工程师 自动化测试 功能测试 性能测试 测试开发 游戏测试 白盒测试 灰盒测试 黑盒测试 手机测试 硬件测试 测试经理 测试其它
运维
运维工程师 运维开发工程师 网络工程师 系统工程师 IT支持 IDC CDN F5 系统管理员 病毒分析 WEB安全 网络安全 系统安全 运维经理 运维其它
DBA
MySQL SQLServer Oracle DB2 MongoDB ETL Hive 数据仓库 DBA其它
高端职位
技术经理 技术总监 架构师 CTO 运维总监 技术合伙人 项目总监 测试总监 安全专家 高端技术职位其它
项目管理
项目经理 项目助理
硬件开发
硬件 嵌入式 自动化 单片机 电路设计 驱动开发 系统集成 FPGA开发 DSP开发 ARM开发 PCB工艺 模具设计 热传导 材料工程师 精益工程师 射频工程师 硬件开发其它
企业软件
实施工程师 售前工程师 售后工程师 BI工程师 企业软件其它
            '''
        ts = re.split(r'\s+', msg)
        return filter(lambda t: re.match(r'^\s*$', t) is None, ts)

    def crawljobs(self):
        error = []
        types = self.get_types()
        for kw in types:
            error.extend(self.__crawljobs(kw))

        return error

    def __crawljobs(self, keyword, city=u'全国'):

        page_num = 1

        url = u'http://www.lagou.com/jobs/positionAjax.json?px=default&city=%s&needAddtionalResult=false' % (city,)

        page_size = sys.maxint

        errors = []

        while page_num < page_size:
            data = u'first=false&pn=%d&kd=%s' % (page_num, keyword)
            cache, content = Downloader.get_html(url, data, city)
            if content:
                try:
                    result = json.loads(content)
                    page_no = result['content']['pageNo']
                    if page_no > 0:
                        print '{kv}: {page_num}'.format(kv=keyword, page_num=page_num)
                        page_num += 1
                        if not cache:
                            # 每个网络请求间隔一秒
                            sleep(0.1)
                    else:
                        # 为空,说明最后一页
                        break
                except Exception, e:
                    page_num += 1
                    # 发生异常, 删除缓存文件
                    Downloader.remove_file(url, data, city)
                    errors.append((1, url, data, city, e))
            else:
                # 请求结果为空
                errors.append((2, url, data, city, e))

        return errors

    # 入库
    def insert_jobs(self):
        errors = []

        types = self.get_types()
        for keyword in types:
            page_num = 1
            city = u'全国'
            url = u'http://www.lagou.com/jobs/positionAjax.json?px=default&city=%s&needAddtionalResult=false' % (city,)
            page_size = sys.maxint

            while page_num < page_size:
                data = u'first=false&pn=%d&kd=%s' % (page_num, keyword)
                cache, content = Downloader.get_html(url, data, city)
                if content:
                    try:
                        result = json.loads(content)
                        pos_result = result['content']['positionResult']
                        jobs = pos_result['result']
                        if len(jobs) > 0:
                            self.db.insert_jobs(jobs)
                            print data
                        else:
                            # 为空说明是最后一页
                            errors.append('result empty {0} {1}'.format(url, data, content))
                            break

                        page_num += 1
                    except Exception, e:
                        page_num += 1
                        # 发生异常
                        errors.append((1, url, data, city, e))
                else:
                    # 请求结果为空
                    errors.append((2, url, data, city, e))

        return errors

    # 关联搜索关键字
    def associate_key_and_job(self):
        types = self.get_types()
        errors = []
        for keyword in types:
            page_num = 1
            city = u'全国'
            url = u'http://www.lagou.com/jobs/positionAjax.json?px=default&city=%s&needAddtionalResult=false' % (city,)
            page_size = sys.maxint

            while page_num < page_size:
                data = u'first=false&pn=%d&kd=%s' % (page_num, keyword)
                cache, content = Downloader.get_html(url, data, city)
                if content:
                    try:
                        result = json.loads(content)
                        pos_result = result['content']['positionResult']
                        jobs = pos_result['result']
                        if len(jobs) > 0:
                            self.db.associate_key_job(keyword, map(lambda i: i['positionId'], jobs))
                            print data
                        else:
                            # 为空说明最后一页
                            errors.append('result empty {0} {1}'.format(url, data, content))
                            break

                        page_num += 1
                    except Exception, e:
                        page_num += 1
                        # 发生异常
                        errors.append((1, url, data, city, e))
                else:
                    # 请求结果为空
                    errors.append((2, url, data, city, e))

        return errors

    # 创建一些额外的字段, 存放额外的数据
    def analyze_jobs(self):
        errors = []
        jobs = self.db.select_jobs(nomidsalary=True)
        for i in jobs:
            salary = i['salary']
            twosalary = salary.split('-')

            maxsalary = None
            midsalary = None
            minsalary = None
            # 验证
            if len(twosalary) is not 2:
                if twosalary[0].endswith(u'k以上'):
                    minsalary = int(twosalary[0].rstrip('k以上')) * 1000
                    midsalary = minsalary
                    self.db.update_job(i['id'], minsalary, midsalary, maxsalary)
                elif twosalary[0].endswith(u'k以下'):
                    maxsalary = int(twosalary[0].rstrip('k以下')) * 1000
                    midsalary = maxsalary
                    self.db.update_job(i['id'], minsalary, midsalary, maxsalary)
                else:
                    errors.append(u'数据错误1')
            else:
                if (twosalary[0].endswith('k') and twosalary[1].endswith('k')):
                    minsalary = int(twosalary[0].rstrip('k')) * 1000
                    maxsalary = int(twosalary[1].rstrip('k')) * 1000
                    midsalary = int((maxsalary - minsalary) * 0.5 + minsalary)
                    self.db.update_job(i['id'], minsalary, midsalary, maxsalary)
                else:
                    errors.append(u'数据错误2')

            print i['id']

        self.db.adapt_job_city()
        return errors

    def adapt_job_city(self):
        self.db.adapt_job_city()

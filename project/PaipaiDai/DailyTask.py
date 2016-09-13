#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import time

import datetime

from Analyzer import Analyzer
from Server import Server
from PaipaiDai import PaipaiDai
from Database import Database


class DailyTask(object):
    def __init__(self):
        self.db = Database()
        pass

    # <editor-fold desc="扫描所有投资的散标还款情况,结合提前还款,计算综合利率">

    # 扫描所有投资的散标还款情况,结合提前还款,计算综合利率
    def scan_lilv(self):
        today = datetime.datetime.today().date()
        date = long(time.mktime(today.timetuple()))
        if not self.db.lilv_task_exist(date):
            # 1. 下载我的所有散标
            self.__get_buy_loans()

            # 2. 下载我的所有散标还款详情
            self.__get_loan_huankuan_detail()

            # 3. 分析
            self.db.update_lilv_task()

    # 获取我的所有散标投资列表
    def __get_buy_loans(self):
        days = 180
        url = 'http://www.ppdai.com/moneyhistory?Type=3&Time={0}&page=1'.format(days)
        self.__get_buy_loans2(url)

    # 获取所有散标投资列表
    def __get_buy_loans2(self, url):
        domain = PaipaiDai.get_domain(url)
        content, cache = Server.get(url, cache=False, use_cookie=True)
        if content:
            my_loans, next_page = Analyzer.get_my_loan_list(content)
            self.db.insert_my_loans(my_loans)
            print url
            if next_page:
                if not cache:
                    time.sleep(2)
                next_page = os.path.join(domain, next_page.lstrip('/'))
                self.__get_buy_loans2(next_page)
        else:
            time.sleep(2)



    # 获取我的散标的还款详情
    def __get_loan_huankuan_detail(self):
        my_loans = self.db.get_my_loan(0, 0)
        for my_loan in my_loans:
            url = 'http://invest.ppdai.com/account/paybacklendview/?ListingId={0}'.format(my_loan[4])
            content, cache = Server.get(url, cache=True, use_cookie=True)
            if content:
                huankuans, huanqin = Analyzer.get_my_loan_huankuan_detail(content)

                if len(huankuans) > 0:
                    dengerbenxi = map(lambda i: i[0], huankuans)
                    tiqians = map(lambda i: i[1], huankuans)
                    benjin = my_loan[3]

                    lilv = self.__getLilv(benjin, dengerbenxi, tiqians)
                    print '{0}: {1}'.format(my_loan[1], lilv)
                    if huanqin:
                        self.db.update_my_loan(my_loan[1], True, lilv)
                    else:
                        self.db.update_my_loan(my_loan[1], False, lilv)
                    if not cache:
                        time.sleep(2)

    # 计算综合利率
    def __getLilv(self, benjin, dengerbenxi, tiqians):
        lixi = sum(dengerbenxi) - benjin
        qishu = len(dengerbenxi)
        tians = []
        for i, tiqian in enumerate(tiqians):
            tian = i * 31 + 31 + tiqian
            if tian == 0:
                tian = 1
            tians.append(tian)

        tians2 = [tians[0]]
        for first, second in zip(tians[0:-1], tians[1:]):
            tians2.append(second - first)

        tians = tians2

        amounts = []
        for i in range(0, qishu):
            amounts.append(benjin - sum(dengerbenxi[0:i]))

        sa = 0

        for amount, day in zip(amounts, tians):
            sa += amount * day / 365.0

        return lixi / sa




    # </editor-fold>

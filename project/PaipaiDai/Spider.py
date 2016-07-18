#!/usr/bin/python
# -*- coding:utf-8 -*-
import httplib
import os
import re
import urllib
import urllib2
import cookielib
from termcolor import colored, cprint
import time
import sys

from Server import Server
from Analyzer import Analyzer
from Database import Database, ErrorType
from PaipaiDai import PaipaiDai

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class Spider(object):
    count = 0

    def __init__(self):
        self.db = Database()
        self.ppdai = PaipaiDai()

    def buy_best_bond(self):
        """ 获取债券列表,选取最优债券购买 """
        url = 'http://invest.ppdai.com/AllDebtList/DebtList?monthgroup=1&nodelayrate=0&CType=1&SortType=6&levels='
        while True:
            bonds = []
            # 筛选
            try:
                bonds = self.ppdai.get_bond_list(url, 1)
                bonds = filter(lambda i: i['debtdealid'] > 0, bonds)
                bonds = filter(lambda i: i['youhui'] < 0, bonds)
                bonds = filter(lambda i: (i['lilv'] > 18 and i['totaldays'] <= 30) or (i['lilv'] > 25 and i[
                    'totaldays'] <= 100), bonds)
                bonds = filter(lambda i: i['price'] < 500, bonds)
            except Exception, e:
                print bonds, e

            if bonds and len(bonds):
                # 按照利率排序
                lilv_bonds = sorted(bonds, key=lambda i: i['lilv'], reverse=True)

                # 按照价格排序
                price_bonds = sorted(bonds, key=lambda i: i['price'], reverse=True)

                # 按照时间排序
                time_bonds = sorted(bonds, key=lambda i: i['totaldays'], reverse=True)

                # 取利率最高的
                bond = lilv_bonds[0]
                try:
                    success, message = self.ppdai.buy_bond(bond['debtdealid'], bond['youhui'])
                    if success:
                        print bond
                        cprint(message, 'cyan')
                    else:
                        cprint(message, 'red')

                    print bond
                except Exception, e:
                    print bond, e

            sys.stdout.write('\r{0}, {1}'.format(url, self.__class__.count))
            self.__class__.count += 1
            time.sleep(2)

    def buy_best_loan(self):
        """ 获取散标列表,选取最优散标购买 """
        url = 'http://invest.ppdai.com/loan/list?monthgroup=1&rate=8&didibid=&listingispay='
        while True:
            loans = self.ppdai.get_loan_all_list(url, 0)
            # 筛选
            loans = filter(lambda i: i['rank'] > 7, loans)
            loans = filter(lambda i: 'AA' in i['rankcode'] > 0, loans)
            loans = filter(lambda i: i['lilv'] > 8, loans)
            loans = filter(lambda i: i['limit_time'] <= 3, loans)


            if len(loans):
                # 按照利率排序
                lilv_loans = sorted(loans, key=lambda i: i['lilv'], reverse=True)

                # 按照时间排序
                time_bonds = sorted(loans, key=lambda i: i['limit_time'], reverse=False)

                # 取利率最高的
                loan = lilv_loans[0]
                # success, message = self.ppdai.buy_loan(loan['loan_id'], 50)
                # if success:
                #     cprint(message, 'cyan')
                # else:
                #     cprint(message, 'red')

                print lilv_loans[0]
                if time_bonds[0]['limit_time'] < lilv_loans[0]['limit_time']:
                    print time_bonds[0]

            sys.stdout.write('\r{0}, {1}'.format(url, self.__class__.count))
            self.__class__.count += 1
            time.sleep(5)

    # 爬去散标列表
    def crawl_loan_list(self, url):
        data, next_page, cache = self.ppdai.get_loan_list(url, True)
        self.db.insert_loans(data)
        print url
        if next_page:
            if not cache:
                time.sleep(3)
            self.crawl_loan_list(next_page)

    # 根据散标列表爬去用户信息
    def crawl_users_from_loan_list(self, count):
        detail_urls = self.db.get_loan_urls_from_loans(count)
        for url in detail_urls:
            url = url[0]
            try:
                content, cache = Server.get(url, cache=True)
                if content:
                    info = Analyzer.get_loan_detail(content)
                    # 入库
                    self.db.insert_user_info(info)
                    print(url)
                if not cache:
                    time.sleep(3)
            except Exception, e:
                print e

    def crawl_user_detail(self, user_id):
        pass




























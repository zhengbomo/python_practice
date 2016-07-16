#!/usr/bin/python
# -*- coding:utf-8 -*-
import httplib
import os
import re
import ssl
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
                bonds = self.ppdai.get_bond_list(url, 0)
                bonds = filter(lambda i: i['debtdealid'] > 0, bonds)
                bonds = filter(lambda i: i['youhui'] < 0, bonds)
                bonds = filter(lambda i: i['lilv'] > 18, bonds)
                bonds = filter(lambda i: i['totaldays'] <= 30, bonds)
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
            time.sleep(3)

    def buy_best_loan(self):
        """ 获取散标列表,选取最优散标购买 """
        url = 'http://invest.ppdai.com/loan/list?monthgroup=1&rate=8&didibid=&listingispay='
        while True:
            loans = self.ppdai.get_loan_list(url, 0)
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

    def crawl_user(self, url):
        user_info = self.ppdai.get_user_detail(url)




        # context = ssl._create_unverified_context()
        # urllib.urlopen("https://no-valid-cert", context=context)
        # ssl._create_default_https_context = ssl._create_unverified_context
        #
        # url = 'https://wirelessgateway.ppdai.com/Invest/BorrowerinfoService/Borrowerinfo'
        # data = {
		 #    "ListingId": "15659580",
		 #    "Borrowernumber": "1325891"
        # }
        # data = urllib.urlencode(data)
        # headers = {
        #     "Host": "wirelessgateway.ppdai.com",
        #     "Content-Type": "application/json",
        #     "Accept": "*/*",
        #     "Proxy-Connection": "keep-alive",
        #     "X-PPD-APPID": "10080001",
        #     "X-PPD-DEVICEID": "FA89B250-6C04-4A7C-9CB6-0E0B7F3CAA29",
        #     "Accept-Language": "1111",
        #     "Host": "zh-cn",
        #     "X-PPD-TIMESTAMP": str(int(time.time())),
        #     "X-PPD-KEYVERSION": "1",
        #     "X-PPD-APPVERSION": "2.5.0",
        #     "X-PPD-KEY": "tc-001",
        #     "Accept-Encoding": "gzip, deflate",
        #     "User-Agent": "Lender/2.5.7 CFNetwork/758.4.3 Darwin/15.5.0",
        # }
        #
        # host = 'wirelessgateway.ppdai.com'
        # url = '/Invest/BorrowerinfoService/Borrowerinfo'
        # conn = httplib.HTTPSConnection(host)
        # conn.request('POST', url, data, headers)
        # r1 = conn.getresponse()
        # print r1.status, r1.reason
        #
        # urllib.urlopen("https://wirelessgateway.ppdai.com", context=context)




    def crawl_user_detail(self, user_id):
        pass




























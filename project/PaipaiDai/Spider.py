#!/usr/bin/python
# -*- coding:utf-8 -*-
import httplib
import os
import re
import urllib
import urllib2
import cookielib
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
        url = 'http://invest.ppdai.com/AllDebtList/DebtList?monthgroup=0&nodelayrate=0&CType=1&SortType=6&levels='
        max_lilv = 0

        while True:
            bonds = []
            origin_bonds = []
            # 筛选
            try:
                origin_bonds = self.ppdai.get_bond_list(url, 1)
                bonds = filter(lambda i: i['debtdealid'] > 0, origin_bonds)
                bonds = filter(lambda i: i['youhui'] < 0, bonds)
                bonds = filter(lambda i: (i['lilv'] > 13 and i['totaldays'] <= 30) or (i['lilv'] > 20 and i[
                    'totaldays'] <= 100), bonds)
                bonds = filter(lambda i: i['price'] < 500, bonds)
            except Exception, e:
                print bonds, e

            max_lilv = max(max(origin_bonds, key=lambda i: i['lilv']), max_lilv)

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
                        print message
                    else:
                        print message

                    print bond
                except Exception, e:
                    print bond, e

            sys.stdout.write('\r{0}, {1} {2}'.format(url, self.__class__.count, max_lilv['lilv']))
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

    # 爬取散标(中风险),总金额小于5000, 利率大于20%, 等级为C, 期限为10个月以内的标
    def crawl_best_loan(self):
        # 中风险,11月以下,利率高于18%
        url = 'http://invest.ppdai.com/loan/list_RiskMiddle_s12_p1?monthgroup=1,2,3&rate=18&didibid=&listingispay='
        while True:
            loan, info = self.crawl_loan_list(url, page_count=10)
            if loan:
                # 购买
                print loan, info
                success, message = self.ppdai.buy_loan(loan['loan_id'], 50)
                print message
            time.sleep(1)

        pass

    # 爬去散标列表,并爬去出详情,更新用户信息,满足条件则返回
    def crawl_loan_list(self, url, page_count=1):
        data, next_page, cache = self.ppdai.get_loan_list(url, cache=False, use_cookie=True)
        self.db.insert_loans(data)

        for i in data:
            url = i['detail_url']
            info = self.craw_user_info_from_loan_url(url)
            if info:
                # 1. 金额小于5000
                # 2. 利率大于20%
                # 3. 等级为C
                # 4. 期限为10个月以内
                if i['amount'] < 5000 and i['lilv'] >= 20 and i['rankcode'] == 'C' and i['limit_time'] < 10:
                    # 1. 平均预期天数<=0, 提前天数>15, 总还清数 > 2
                    if info['yuqi_days'] <= 0 and info['tiqian_days'] < -15 and info['tongji_info'].get(
                            'total_huanqing') > 2:
                        # 满足条件
                        return i, info
            time.sleep(1)
            sys.stdout.write('\r{0}, {1}'.format(url, self.__class__.count,))
            self.__class__.count += 1

        if next_page and page_count > 0:
            page_count -= 1
            return self.crawl_loan_list(next_page, page_count)
        return None, None

    # 爬取中风险, 高风险散标列表,存入数据库
    def crawl_mid_high_fengxian_loan_list(self):
        # 中风险
        url = 'http://invest.ppdai.com/loan/list_riskmiddle_s0_p1?monthgroup=1%2C2%2C3&rate=18&didibid=&listingispay='
        self.crawl_loan_list_and_insert(url, 100)
        # 高风险
        url = 'http://invest.ppdai.com/loan/list_riskhigh?monthgroup=&rate=18&didibid=&listingispay='
        self.crawl_loan_list_and_insert(url, 100)

    # 爬去散标列表,并爬去出详情,更新用户信息,满足条件则返回
    def crawl_loan_list_and_insert(self, url, page_count=1):
        data, next_page, cache = self.ppdai.get_loan_list(url, True, use_cookie=True)
        self.db.insert_loans(data)

        for i in data:
            url = i['detail_url']
            self.craw_user_info_from_loan_url(url)
            sys.stdout.write('\r{0}, {1}'.format(url, self.__class__.count,))
            self.__class__.count+=1
            if not cache:
                time.sleep(1)

        # 下一页
        if next_page and page_count:
            page_count -= 1
            self.crawl_loan_list_and_insert(next_page, page_count=page_count)

    # 爬取用户未完成的借款链接,并入库
    def craw_user_uncompleted_borrow_url(self, user_url):
        url = user_url
        domain = PaipaiDai.get_domain(url)
        content, cache = Server.get(url, cache=False, use_cookie=True)
        if content:
            info = Analyzer.get_user_info(content)
            if info['href']:
                info['href'] = os.path.join(domain, info['href'].lstrip('/'))

                content, cache = Server.get(info['href'], cache=False, use_cookie=True)
                if content:
                    if not Analyzer.is_manbiao(content):
                        info = Analyzer.get_loan_detail(content)
                        # 入库
                        self.db.insert_user_info(info)

    # 根据散标url爬取用户数据
    def craw_user_info_from_loan_url(self, url):
        content, cache = Server.get(url, cache=True, use_cookie=True)
        if content:
            info = Analyzer.get_loan_detail(content)
            # 入库
            self.db.insert_user_info(info)
            return info
        else:
            return None

    def crawl_user_detail(self, user_id):
        pass

    # 爬取最多提前的用户的标
    def crawl_most_tiqian_cd_user_loan(self, count):
        user_urls = self.db.get_most_tiqian_cd_user_urls(count)
        for user_url in user_urls:
            url = user_url[0]
            domain = PaipaiDai.get_domain(url)
            # 爬取用户可用标
            content, cache = Server.get(url, cache=True, use_cookie=True)
            if content:
                info = Analyzer.get_user_info(content)
                if info['href']:
                    # 有可用标
                    info['href'] = os.path.join(domain, info['href'].lstrip('/'))
                    content, cache = Server.get(info['href'], cache=True, use_cookie=True)
                    if content:
                        # 未满标,验证通过
                        if not Analyzer.is_manbiao(content):
                            info = Analyzer.get_loan_detail(content)
                            # 是否已购买和判断金额
                            print '\t' + info['href']
                            if (not info['has_buy']) and info['rest_buy'] >= 50 and info['amount'] < 5000 and info[
                                'lilv'] > 20 and info['qixian'] <= 11:
                                # 满足条件
                                print '\t\t' + info['href']

                            # 写入数据库
                            self.db.insert_user_info(info)

            print url, user_url[1]
            if not cache:
                time.sleep(1)


























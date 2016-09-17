#!/usr/bin/python
# -*- coding:utf-8 -*-

from PaipaiDai import PaipaiDai
from Server import Server
from Analyzer import Analyzer

import os
import time
import webbrowser


class PpOpen(object):
    def __init__(self):
        pass

    @staticmethod
    def open_well_loan():
        # 循环二十次
        for i in range(1, 20):
            url = 'http://invest.ppdai.com/loan/list_RiskMiddle_s12_p1?monthgroup=&rate=20&didibid=&listingispay='
            PpOpen.__open_well_loan(url, page_count=10)

            # 中风险, 利率18%+, 进度排序
            url = 'http://invest.ppdai.com/loan/list_RiskMiddle_s1_p1?monthgroup=&rate=20&didibid=&listingispay='
            PpOpen.__open_well_loan(url, page_count=10)

    # 打开符合条件的标: 非第一次借款, 近期有已还完的借款, 还款利率>18%, 发布时间在2016/2之后
    @staticmethod
    def __open_well_loan(url, page_count=1):
        domain = PaipaiDai.get_domain(url)
        data, cache = Server.get(url, cache=False, use_cookie=True)
        if data:
            loans, next_page = Analyzer.get_loan_list(data)

            # 处理列表
            for loan in loans:
                if u'首次' not in loan['title'] and u'第1次' not in loan['title']:
                    # 过滤第一次的用户
                    PpOpen.analyze_loan(loan['detail_url'])
                    time.sleep(2)

            if next_page and page_count > 0:
                time.sleep(2)
                next_page = os.path.join(domain, next_page.lstrip('/'))
                PpOpen.open_well_loan(next_page, page_count=page_count-1)

    @staticmethod
    def analyze_loan(url):
        data, cache = Server.get(url, cache=False, use_cookie=True)
        if data:
            info = Analyzer.get_loan_detail(data)
            if info and info['amount'] < 4000:
                print url
                # 判断借款成功次数>0
                huanqing = info['tongji_info'].get('total_huanqing')
                if huanqing and huanqing > 0:
                    # 已还完时间在2016/2之后
                    if info['lishi_borrowed'] \
                            and not info['has_buy'] \
                            and info['tiqian_days'] < -30 \
                            and len(info['tiqian_days_list']) > 2:

                        print u'买买买' + url
                        if len(info['tiqian_days_list']) > 3 and info['tiqian_days'] < -50:
                            res, msg = PaipaiDai.buy_loan(info['loan_id'], 50)
                            if not res:
                                print u'买买买失败:{0}'.format(msg)
                        else:
                            webbrowser.open_new_tab(url)

    @staticmethod
    def check_loan_qishu(url):
        data, cache = Server.get(url, cache=False, use_cookie=True)
        if data:
            info = Analyzer.get_loan_detail(data)
            if info:
                qishu = info['qishu']
                
            
  

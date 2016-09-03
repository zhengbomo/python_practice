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

    # 打开符合条件的标: 非第一次借款, 近期有已还完的借款, 还款利率>18%, 发布时间在2016/2之后
    @staticmethod
    def open_well_loan(url, page_count=1):
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
    def analyze_loan2(url):
        data, cache = Server.get(url, cache=False, use_cookie=True)
        if data:
            info = Analyzer.get_loan_detail(data)
            if info:
                print url        
                # 判断借款成功次数>0
                huanqing = info['tongji_info'].get('total_huanqing')
                if huanqing and huanqing > 0:
					# 还款记录利率>18%, 已还完时间在2016/2之后
                    if info['lishi_borrowed'] and not info['has_buy']:
                        # print info                
                        for borrow in info['lishi_borrowed']:
                            if borrow['lilv'] > 12 and '已还完' in borrow['status']:
                                publish_time = borrow['publish_time'].split('/')
                                # 时间在2016/2之后
                                if int(publish_time[0]) >= 2016 and int(publish_time[1]) > 1:
                                    print '\t' + url
                                    webbrowser.open_new_tab(url)
                                    return

    @staticmethod
    def analyze_loan(url):
        data, cache = Server.get(url, cache=False, use_cookie=True)
        if data:
            info = Analyzer.get_loan_detail(data)
            if info:
                print url
                # 判断借款成功次数>0
                huanqing = info['tongji_info'].get('total_huanqing')
                if huanqing and huanqing > 0:
					# 还款记录利率>18%, 已还完时间在2016/2之后
                    if info['lishi_borrowed'] and not info['has_buy'] and info['tiqian_days'] < -30:
                        print info
                        webbrowser.open_new_tab(url)

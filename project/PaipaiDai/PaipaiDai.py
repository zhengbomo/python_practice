#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import re
import json
import time
import urllib
import urllib2

from Server import Server
from Analyzer import Analyzer


class PaipaiDai(object):
    @staticmethod
    def login(uname, pwd):
        """ 登陆 """
        data = {
            "IsAsync": "true",
            "Redirect": "",
            "UserName": uname,
            "Password": pwd,
            "RememberMe": "true",
        }
        url = 'https://ac.ppdai.com/User/Login'
        return Server.login(url, data) is not None

    @staticmethod
    def get_loan_list(url, total_page=1):
        """ 获取散标列表, 返回列表 """
        domain = PaipaiDai.get_domain(url)
        result = []
        data, cache = Server.get(url, cache=False)
        if data:
            data, next_page = Analyzer.get_loan_list(data)
            print url
            result.extend(data)

            if next_page and total_page > 0:
                next_page = os.path.join(domain, next_page.lstrip('/'))
                time.sleep(3)
                result.extend(PaipaiDai.get_loan_list(next_page, total_page-1))
        return result

    @staticmethod
    def get_bond_list(url, total_page=0):
        """ 获取债券列表 """
        domain = PaipaiDai.get_domain(url)
        bonds = []
        try:
            data, cache = Server.get(url, cache=False)
            if data:
                data, next_page = Analyzer.get_bond_list(data)
                bonds.extend(data)

                if next_page and total_page > 0:
                    next_page = os.path.join(domain, next_page.lstrip('/'))
                    PaipaiDai.get_best_bond(next_page, total_page-1)
        except Exception, e:
            print e
        return bonds

    @staticmethod
    def buy_loan(listing_id, amount):
        """ 购买散标 """
        data = {
            "Reason": "",
            "Amount": amount,
            "ListingId": listing_id,
            "UrlReferrer": "1",
            "SubListType": "0",
        }
        url = 'http://invest.ppdai.com/Bid/Bid'
        content = Server.post(url, data)
        if content:
            try:
                result = json.loads(content)
                if result:
                    if result['Code'] > 0:
                        return True, "购买成功"
                    else:
                        return False, result['Message']
                else:
                    return False, "json解析失败"
            except Exception, e:
                return False, 'error {0}: {1}'.format(e, result)
        else:
            return False, "post失败"

    @staticmethod
    def buy_bond(debtid, youhui):
        """ 购买债券 """
        url = 'http://invest.ppdai.com/AllDebtList/DebtBuy'
        data = {
            "debtDealId": debtid,
            "preferencedegree": youhui
        }
        data = urllib.urlencode(data)
        result = Server.post(url, data)
        if result:
            try:
                if result['Code'] > 0:
                    return True, "购买成功"
                else:
                    return False, '\n{0}'.format(result['Message'])

            except Exception, e:
                print False, '\nerror {0}: {1}'.format(e, result)
        else:
            print False, 'post失败'

    @staticmethod
    def get_lean_detail(leanid):
        pass

    @staticmethod
    def get_user_detail(url):
        """ 获取用户详情 """
        try:
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, sdch",
                "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
                "Connection": "keep-alive",
                "Host": "www.ppdai.com",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
            }

            request = urllib2.Request(url, headers=headers)
            response = urllib.urlopen(request)
            data = response.read()
            if data:
                print data
            else:
                print False, 'get失败'

        except Exception, e:
            print False, '\nerror {0}: {1}'.format(e)


    @staticmethod
    def get_domain(url):
        reg = r'^(https?:\/\/[a-z0-9\-\.]+)[\/\?]?'
        match = re.match(reg, url)
        return match.group()
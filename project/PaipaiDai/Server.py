#!/usr/bin/python
# -*- coding:utf-8 -*-
import cookielib
import os
import urllib
import urllib2
import gzip
import StringIO
import json
import requests
import requests.utils
import pickle
from CacheManager import CacheManager


class Server(object):
    @staticmethod
    def bid(listing_id, amount):
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
            return json.loads(content)
        else:
            return None

    @staticmethod
    def post(url, data):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "invest.ppdai.com",
            "Origin": "http://invest.ppdai.com",
            "Referer": "http://invest.ppdai.com/AllDebtList/DebtList?monthgroup=1&nodelayrate=0&CType=1&SortType=4&levels=",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/51.0.2704.103 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }

        session = requests.Session()
        session.headers = headers
        cookies, exists = Server.__get_cookie()
        if exists:
            session.cookies = cookies
            response = session.post(url, data=data)
            return response.text
        else:
            return None

    @staticmethod
    def login(url, data):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "ac.ppdai.com",
            "Origin": "https://ac.ppdai.com",
            "Referer": "https://ac.ppdai.com/User/Login?message=&Redirect=",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/51.0.2704.103 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }

        cookies, exists = Server.__get_cookie()
        if not exists:
            session = requests.Session()
            session.headers = headers
            response = session.post(url, data=data)

            # 写入cookie
            with open('cookie', 'w') as f:
                pickle.dump(requests.utils.dict_from_cookiejar(response.cookies), f)

    @staticmethod
    def get(url, cache=True, use_cookie=False):
        if cache:
            data = CacheManager.get(url)
            if not data:
                data = Server.download(url, use_cookie=use_cookie)
                if data:
                    CacheManager.set(url, data)
                return data, False
            else:
                return data, True
        else:
            data = Server.download(url, use_cookie=use_cookie)
            return data, False

    @staticmethod
    def download(url, use_cookie=False):
        cookies, _ = Server.__get_cookie()
        try:
            session = requests.session()
            if use_cookie:
                session.cookies = cookies
            response = session.get(url)
            response.encoding = 'utf8'
            return response.text
        except Exception, e:
            return None

    @staticmethod
    def __get_cookie():
        path = os.getcwd()
        path = os.path.join(path, 'cookie')

        if os.path.isfile(path):
            with open('cookie') as f:
                cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
                return cookies, True
        else:
            return None, False

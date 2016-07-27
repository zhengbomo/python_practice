#!/usr/bin/python
# -*- coding:utf-8 -*-
import cookielib
import os
import urllib
import urllib2
import gzip
import StringIO
import json
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

        opener_headers = []
        for k, v in headers.iteritems():
            opener_headers.append((k, v))

        cookie, exists = Server.__get_cookie()
        if exists:
            try:
                cookie_handler = urllib2.HTTPCookieProcessor(cookie)
                opener = urllib2.build_opener(cookie_handler)
                opener.addheaders = opener_headers
                response = opener.open(url, data=data, timeout=30)
                content = response.read()
                cookie.save(ignore_discard=True, ignore_expires=True)
                return content
            except Exception, e:
                return None
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

        opener_headers = []
        for k, v in headers.iteritems():
            opener_headers.append((k, v))

        cookie, exists = Server.__get_cookie()
        if not exists:
            try:
                cookie_handler = urllib2.HTTPCookieProcessor(cookie)
                opener = urllib2.build_opener(cookie_handler)
                opener.addheaders = opener_headers
                data = urllib.urlencode(data)
                response = opener.open(url, data=data, timeout=30)
                content = response.read()
                cookie.save(ignore_discard=True, ignore_expires=True)
                return content
            except Exception, e:
                return None
        else:
            return None

    @staticmethod
    def get(url, cache=True):
        if cache:
            data = CacheManager.get(url)
            if not data:
                data = Server.download(url)
                if data:
                    CacheManager.set(url, data)
                return data, False
            else:
                return data, True
        else:
            data = Server.download(url)
            return data, False


    @staticmethod
    def download(url):
        cookie, _ = Server.__get_cookie()
        try:
            cookie_handler = urllib2.HTTPCookieProcessor(cookie)
            opener = urllib2.build_opener(cookie_handler)
            # response = opener.open(url, timeout=30)
            response = urllib.urlopen(url)
            content = response.read()

            if response.headers.dict.get('content-encoding') == 'gzip':
                gzipper = gzip.GzipFile(fileobj=StringIO.StringIO(content))
                content = gzipper.read()
                gzipper.close()

            return content
        except Exception, e:
            return None

    @staticmethod
    def __get_cookie():
        path = os.getcwd()
        path = os.path.join(path, 'cookie')

        if os.path.isfile(path):
            cookie = cookielib.LWPCookieJar(filename=path)
            cookie.load('cookie', ignore_discard=True, ignore_expires=True)
            return cookie, True
        else:
            return cookielib.LWPCookieJar(filename=path), False

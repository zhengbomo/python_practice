#!/usr/bin/python
# -*- coding:utf-8 -*-
import re
import json
import urllib2
import cookielib
import urllib
import base64
import rsa
import binascii
import time

# TODO:缓存处理,出错处理,不要每次都登陆,用保存的Cookie,登陆方法私有,需要的时候自动掉用


class WeiboServer(object):
    def __init__(self, username, pwd):
        self.userName = username
        self.passWord = pwd
        self.enableProxy = False
        self.cookiejar = None
        self.serverUrl = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.18)&_=" + str(int(time.time())*1000)
        self.loginUrl = "http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)"
        self.postHeader = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36'}

    def login(self):
        self.__login()

    def get_user_id(self):
        # TODO:如果没登陆,自动登陆后分析返回
        return "1891587992"

    def get_user_info(self, user_id):

        pass

    def get_user_status(self, user_id):
        pass

    def get_fance_id(self, user_id):
        url = 'http://weibo.com/{userid}/fans'.format(userid=user_id)
        cookie_handler = urllib2.HTTPCookieProcessor(self.cookiejar)
        opener = urllib2.build_opener(cookie_handler)
        return opener.open(url).read()


    def __login(self):
        """登陆程序"""
        self.EnableCookie(self.enableProxy)     # cookie或代理服务器配置

        serverTime, nonce, pubkey, rsakv = self.GetServerTime()     # 登陆的第一步
        postData = self.PostEncode(self.userName, self.passWord, serverTime, nonce, pubkey, rsakv)  # 加密用户和密码
        print "Post data length:\n", len(postData)
        req = urllib2.Request(self.loginUrl, postData, self.postHeader)
        print "Posting request..."
        result = urllib2.urlopen(req)   # 登陆的第二步——解析新浪微博的登录过程中3
        text = result.read()
        try:
            loginUrl = self.sRedirectData(text)     # 解析重定位结果
            if self.testResult(text) == '0':
               print 'Login sucess!'
            elif self.testResult(text) == '4049':
               print 'need verification code'
               return False
            else:
               print 'wrong password'
            urllib2.urlopen(loginUrl)
        except:
            print 'Login error!'
            return False
        return True

    def EnableCookie(self, enableProxy):
        """Enable cookie & proxy (if needed)."""
        self.cookiejar = cookielib.LWPCookieJar(
                filename='/Users/zhengxiankai/Documents/Code/Responsitory/weibocookie.ck')
        # 建立cookie
        cookie_support = urllib2.HTTPCookieProcessor(self.cookiejar)
        if enableProxy:
            proxy_support = urllib2.ProxyHandler({'http':'202.106.16.36:3128'})#使用代理
            opener = urllib2.build_opener(proxy_support, cookie_support, urllib2.HTTPHandler)
            print "Proxy enabled"
        else:
            opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)

        urllib2.install_opener(opener)  # 构建cookie对应的opener

    def GetServerTime(self):
        "Get server time and nonce, which are used to encode the password"

        print "Getting server time and nonce..."
        serverData = urllib2.urlopen(self.serverUrl).read()#得到网页内容
        print serverData
        try:
            serverTime, nonce, pubkey, rsakv = self.sServerData(serverData)#解析得到serverTime，nonce等
            return serverTime, nonce, pubkey, rsakv
        except:
            print 'Get server time & nonce error!'
            return None

    def sServerData(self, serverData):
        "Search the server time & nonce from server data"

        p = re.compile('\((.*)\)')
        jsonData = p.search(serverData).group(1)
        data = json.loads(jsonData)
        serverTime = str(data['servertime'])
        nonce = data['nonce']
        pubkey = data['pubkey']#
        rsakv = data['rsakv']#
        print "Server time is:", serverTime
        print "Nonce is:", nonce
        return serverTime, nonce, pubkey, rsakv

    def sRedirectData(self, text):
        p = re.compile('location\.replace\([\'"](.*?)[\'"]\)')
        loginUrl = p.search(text).group(1)
        print 'loginUrl:',loginUrl
        return loginUrl

    def testResult(self, text):
        p = re.compile('retcode=(\d*)')
        testNum = p.search(text).group(1)
        return testNum

    def PostEncode(self, userName, passWord, serverTime, nonce, pubkey, rsakv):
        """Used to generate POST data"""

        encodedUserName = self.GetUserName(userName)#用户名使用base64加密
        encodedPassWord = self.get_pwd(passWord, serverTime, nonce, pubkey)#目前密码采用rsa加密
        postPara = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'userticket': '1',
            'ssosimplelogin': '1',
            'vsnf': '1',
            'vsnval': '',
            'su': encodedUserName,
            'service': 'miniblog',
            'servertime': serverTime,
            'nonce': nonce,
            'pwencode': 'rsa2',
            'sp': encodedPassWord,
            'encoding': 'UTF-8',
            'prelt': '115',
            'rsakv': rsakv,
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        }
        postData = urllib.urlencode(postPara)#网络编码
        return postData

    def GetUserName(self, userName):
        """Used to encode user name"""
        userNameTemp = urllib.quote(userName)
        userNameEncoded = base64.encodestring(userNameTemp)[:-1]
        return userNameEncoded

    def get_pwd(self, password, servertime, nonce, pubkey):
        rsaPublickey = int(pubkey, 16)
        key = rsa.PublicKey(rsaPublickey, 65537) #创建公钥
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(password) #拼接明文js加密文件中得到
        passwd = rsa.encrypt(message, key) #加密
        passwd = binascii.b2a_hex(passwd) #将加密信息转换为16进制。
        return passwd

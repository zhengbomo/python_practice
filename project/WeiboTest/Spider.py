#!/usr/bin/python
# -*- coding:utf-8 -*-
from WeiboServer import WeiboServer
from Analyzer import Analyzer
from WeiboDb import WeiboDb
from Logger import Logger

# 主爬虫程序
class Spider(object):
    def __init__(self):
        self.db = WeiboDb()
        self.server = WeiboServer("449179249@qq.com", '******')

        #TODO 登陆让内部自动调用
        self.server.login()
        self.user_id = self.server.get_user_id()

    def get_my_fans(self):
        pass

    def get_my_follower(self):
        pass

    def user_crawl(self, user_id):
        html = self.server.get_user_info(user_id)
        if html:
            user_info = Analyzer.get_user_info(html)
            if user_info:
                # 入库
                self.db.insert_use_info(user_info)
            else:
                Logger.error(1, "用户数据解析失败")
        else:
            Logger.error(1, "用户数据下载失败")

    def status_crawl(self, user_id):
        pass

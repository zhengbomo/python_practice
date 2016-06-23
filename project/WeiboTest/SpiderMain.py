#!/usr/bin/python
# -*- coding:utf-8 -*-
from Spider import Spider

# 入口
spider = Spider()

fans = spider.get_my_fans()
for fan in fans:
    spider.user_crawl(fan.user_id)
    spider.status_crawl(fan.user_id)


followers = spider.get_my_follower()
for follower in followers:
    spider.user_crawl(fan.user_id)
    spider.status_crawl(fan.user_id)

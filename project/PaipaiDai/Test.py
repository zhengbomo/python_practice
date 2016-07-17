#!/usr/bin/python
# -*- coding:utf-8 -*-
from Spider import Spider


spider = Spider()
spider.ppdai.login(uname='18600490785', pwd='Zz111111')

# 中风险
# url = 'http://invest.ppdai.com/loan/list_riskmiddle?monthgroup=&rate=0&didibid=&listingispay='
# url = 'http://invest.ppdai.com/loan/list_riskhigh?monthgroup=&rate=0&didibid=&listingispay='
# url = 'http://invest.ppdai.com/loan/list_safe?monthgroup=&rate=0&didibid=&listingispay='
# spider.crawl_loan_list(url)

while True:
    spider.crawl_users_from_loan_list(10)
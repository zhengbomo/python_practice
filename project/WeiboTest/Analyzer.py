#!/usr/bin/python
# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup


class Analyzer(object):
    @staticmethod
    def get_user_info(html):
        pass

    @staticmethod
    def get_fans(html):
        soup = BeautifulSoup(html, 'html.parser')
        f_list = soup.find('div', class_='follow_box')
        lis = f_list.findAll('li')

        fans = []
        for li in lis:
            # TODO 解析
            fans.append(li)
        return fans
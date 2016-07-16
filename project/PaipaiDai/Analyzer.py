#!/usr/bin/python
# -*- coding:utf-8 -*-
import re
from lxml import etree


class Analyzer(object):
    @staticmethod
    def get_loan_list(html):
        tree = etree.HTML(html)

        remove_nodes = tree.xpath("//div[@class='wapSameList']")
        for i in remove_nodes:
            i.getparent().remove(i)

        nodes = tree.xpath("//ol[@class='clearfix']")
        data = []
        for node in nodes:
            node = node.xpath('li')[0]

            rank_node = node.xpath("div[@class='w110 info']")[0]
            rank_node = rank_node.xpath('a')[0]
            rank = rank_node.attrib['rank']
            rank = int(rank)

            rankcode_node = rank_node.xpath('i')[0]
            rankcode = rankcode_node.attrib['class']
            rankcode = rankcode.replace('creditRating ', '')

            title_node = node.xpath("div[@class='w230 listtitle']")[0]
            title_node1 = title_node.xpath("a[@class='title ell']")[0]
            title = title_node1.attrib['title']

            detail_url = title_node1.attrib['href']

            title_node1 = title_node.xpath("p[@class='userInfo clearfix']")[0]
            title_node1 = title_node1.xpath('a')[0]
            user_url = title_node1.attrib['href']

            lilv_node = node.xpath("div[@class='w110 brate']")[0]
            lilv = lilv_node.text
            lilv = float(lilv)

            lilv_node = node.xpath("div[@class='w90 sum']")[0]
            span_node = lilv_node.xpath('span')[0]
            span = etree.tostring(span_node)
            match = re.search(r'</span>([\s\S]+$)', span, re.I)
            amount = match.group(1).replace(',', '').strip()
            amount = float(amount)

            lilv_node = node.xpath("div[@class='w82 limitTime']")[0]
            limit_time = lilv_node.text
            limit_time = int(limit_time)

            lilv_node = node.xpath("div[@class='w140 operate']")[0]
            lilv_node = lilv_node.xpath('div/input')[0]
            loan_id = lilv_node.attrib['id']

            info = {
                "rankcode": rankcode,
                "rank": rank,
                "title": title,
                "detail_url": detail_url,
                "user_url": user_url,
                "lilv": lilv,
                "amount": amount,
                "limit_time": limit_time,
                "loan_id": loan_id,
            }
            data.append(info)

        href = None
        nodes = tree.xpath("//a[@class='nextpage']")
        if len(nodes) > 0:
            href = nodes[0].attrib.get('href')
            if href == 'javascript:void(0)':
                return data, None
            else:
                return data, href
        else:
            pass

        return data, href

    @staticmethod
    def get_bond_list(html):
        tree = etree.HTML(html)
        nodes = tree.xpath("//li[@class='clearfix']")

        data = []
        for node in nodes:
            rank_node = node.xpath("div[@class='w82 creditRating creditCode']")[0]
            rank_code = rank_node.attrib.get('creditcode')
            debtdealid = rank_node.attrib.get('debtdealid')

            rank_node = rank_node.xpath('a[@rank]')[0]
            rank = rank_node.attrib.get('rank')
            rank = int(rank)

            lilv_node = node.xpath("div[@class='w120 originalinterest']")[0]
            lilv = lilv_node.text.strip()
            lilv = lilv[:-1]
            if lilv is '-':
                lilv = 0
            else:
                lilv = float(lilv)

            benxi_node = node.xpath("div[@class='w130 remainamount']")[0]
            benxi = benxi_node.text.strip()
            benxi = benxi[1:].replace(',', '')
            benxi = float(benxi)

            price_node = node.xpath("div[@class='w130 transferprice']")[0]
            price = price_node.text.strip()
            price = price[1:].replace(',', '')
            price = float(price)

            youhui_node = node.xpath("div[@class='w82 favourable']")[0]
            youhui_nodes = youhui_node.xpath("span[@class='green airBubble']")
            if len(youhui_nodes) > 0:
                youhui_node = youhui_nodes[0]
            else:
                youhui_nodes = youhui_node.xpath("span[@class='red airBubble']")
                youhui_node = youhui_nodes[0]

            youhui = youhui_node.text.strip()[:-1]

            if youhui is '-':
                youhui = 0
            else:
                youhui = float(youhui)

            qishu_node = node.xpath("div[@class='w82 remaintime']")[0]
            qishu_text = qishu_node.text.strip()
            qishu_text = qishu_text.split('/')
            qishu = int(qishu_text[1])

            yuqi_node = node.xpath("div[@class='w82 overdue']")[0]
            yuqi = int(yuqi_node.text)

            nextpay_node = node.xpath("div[@class='w120 nextpaytime']")[0]
            nextpay_text = nextpay_node.text.strip()
            nextpay_text = nextpay_text[0:-1].strip()

            if nextpay_text is '-':
                nextpay = 30
            else:
                nextpay = int(nextpay_text)

            total_days = nextpay + (qishu - 1) * 30

            day_interest = (benxi - price) / total_days

            if lilv == 0:
                lilv = (benxi - price) / total_days * 365 / price * 100

            info = {
                "rank_code": rank_code,
                "debtdealid": debtdealid,
                "rank": rank,
                "lilv": lilv,
                "benxi": benxi,
                "price": price,
                "youhui": youhui,
                "qishu": qishu,
                "yuqi": yuqi,
                "nextpay": nextpay,
                "totaldays": total_days,
                "day_interest": day_interest
            }
            data.append(info)

        href = None
        nodes = tree.xpath("//a[@class='nextpage']")
        if len(nodes) > 0:
            href = nodes[0].attrib.get('href')
            if href == 'javascript:void(0)':
                return data, None
            else:
                return data, href
        else:
            pass

        return data, href

    @staticmethod
    def get_detail(html):
        pass

    @staticmethod
    def get_user_info(html):
        pass
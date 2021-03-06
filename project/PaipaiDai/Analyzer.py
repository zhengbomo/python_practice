#!/usr/bin/python
# -*- coding:utf-8 -*-
import re
import time
import datetime
from lxml import etree


class Analyzer(object):
    def test(self):
        pass

    def _test(self):
        pass

    def __test(self):
        pass

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

            # lilv_node = node.xpath("div[@class='w140 operate']")[0]
            # lilv_node = lilv_node.xpath('div/input')[0]
            # loan_id = lilv_node.attrib['id']
            loan_id = '' 

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
    def get_loan_detail(html):
        parser = etree.HTMLParser(encoding='utf-8')
        tree = etree.HTML(html, parser=parser)

        # 借款目的	性别	年龄	婚姻情况	文化程度	住宅状况	是否购车
        info = {
            'loan_id': '0',
            'username': None,
            'user_url': None,
            "borrower_info": {},
            "borrower_detail": '',
            "shenhe_infos": [],
            'tongji_info': {},
            'yuqi_days': 0,
            'tiqian_days': 0,

            # 利率
            'lilv': 0,
            # 已购
            'has_buy': 0,
            # 剩余
            'rest_buy': 0,
            # 金额
            'amount': 0,
            # 期限
            'qixian': 0,

            # 投资者列表
            'bid_users': []
        }

        nodes = tree.xpath(u"//input[@class='inputAmount'and @type='text']")
        if nodes and len(nodes):
            info['loan_id'] = nodes[0].attrib['id']

        nodes = tree.xpath(u"//div[@class='newLendDetailMoneyLeft']")
        if nodes and len(nodes):
            node = nodes[0]
            dls = node.xpath("dl")
            for dl in dls:
                if '借款金额' in dl.xpath('dt')[0].text:
                    jine = dl.xpath('dd')[0].xpath('em')[0].tail
                    jine = jine.replace(',', '')
                    jine = float(jine)
                    info['amount'] = jine
                elif '年利率' in dl.xpath('dt')[0].text:
                    lilv = dl.xpath('dd')[0].text
                    lilv = float(lilv)
                    info['lilv'] = lilv
                elif '期限' in dl.xpath('dt')[0].text:
                    qixian = dl.xpath('dd')[0].text
                    qixian = float(qixian)
                    info['qixian'] = qixian

        nodes = tree.xpath(u"//div[@class='wrapNewLendDetailInfoRight']/div[@class='restMoney']/span[@id='listRestMoney']")
        if nodes and len(nodes):
            node = nodes[0]
            rest = node.text.replace('¥', '').replace(',', '')
            info['rest_buy'] = float(rest)

        nodes = tree.xpath(u"//p[@class='profit' and @style='color: red; font-size: 12px;']")
        if nodes and len(nodes):
            nodes = nodes[0].xpath('a')
            if len(nodes) > 0:
                if '尚未投标' in nodes[0].tail:
                    info['has_buy'] = False
                else:
                    info['has_buy'] = True
            else:
                info['has_buy'] = False
        else:
            info['has_buy'] = False

        nodes = tree.xpath(u"//input[@id and @type='hidden']")
        if nodes and len(nodes):
            info['username'] = nodes[0].attrib['value']

        # <a href="http://www.ppdai.com/user/pdu5357282613" class="username">pdu5357282613</a>
        nodes = tree.xpath(u"//a[@href and @class='username']")
        if nodes and len(nodes):
            info['user_url'] = nodes[0].attrib['href']


        nodes = tree.xpath(u"//h3[text()='借款人相关信息']")
        if nodes and len(nodes):
            nodes = nodes[0].xpath('following-sibling::table[@class="lendDetailTab_tabContent_table1"]')
            if nodes and len(nodes) > 0:
                # 审核信息
                table_node = nodes[0]
                nodes1 = table_node.xpath(u"tr[1]")
                nodes2 = table_node.xpath(u"tr[2]")
                if nodes1 and nodes2 and len(nodes1) and len(nodes2):
                    # 借款人信息
                    borrower_info = {}
                    ths = nodes1[0].xpath(u"th")
                    tds = nodes2[0].xpath(u"td")
                    for th, td in zip(ths, tds):
                        borrower_info[th.text.strip()] = td.text.strip() if td.text else None
                    info['borrower_info'] = borrower_info


        nodes = tree.xpath(u"//h3[text()='借款详情']")
        if nodes and len(nodes):
            nodes = nodes[0].xpath('following-sibling::p')
            if nodes and len(nodes):
                # 借款详情
                borrower_detail = nodes[0].text
                info['borrower_detail'] = borrower_detail

        nodes = tree.xpath(u"//h3[text()='拍拍贷审核信息']")
        if nodes and len(nodes):
            nodes = nodes[0].xpath('following-sibling::table[@class="lendDetailTab_tabContent_table1"]')
            if nodes and len(nodes):
                # 审核信息
                table_node = nodes[0]
                nodes = table_node.xpath(u"tr/td[1]")
                shenhe_infos = map(lambda i: i.text.strip(), nodes)
                info['shenhe_infos'] = shenhe_infos


        # 逾期天数
        nodes = tree.xpath(u"//p[text()='12个月的逾期天数记录（与应还款日期比较，负数表示提前还款）']")
        if nodes and len(nodes):
            nodes = nodes[0].xpath(u"following-sibling::table[@class='lendDetailTab_tabContent_table1']")
            if nodes and len(nodes):
                nodes = nodes[0].xpath('descendant::td[not(@style)]')
                nodes = map(lambda i: i.text.strip(), nodes)
                nodes = filter(lambda i: '--' not in i, nodes)
                nodes = map(lambda i: int(i), nodes)

                yuqi_days = filter(lambda i: i>0, nodes)
                tiqian_days = filter(lambda i: i<=0, nodes)

                info['tiqian_days_list'] = tiqian_days

                if len(yuqi_days):
                    info['yuqi_days'] = sum(yuqi_days) * 1.0 / len(yuqi_days)
                if len(tiqian_days):
                    info['tiqian_days'] = sum(tiqian_days) * 1.0 / len(tiqian_days)

        nodes = tree.xpath(u"//h3[text()='拍拍贷统计信息']")
        if nodes and len(nodes):
            nodes = nodes[0].xpath('following-sibling::p')
            if nodes and len(nodes):
                # 审核信息
                pnodes = nodes

                tongji_info = {
                    "total_huanqing": 0,
                    "total_yuqi_15": 0,
                    "total_yuqi_16": 0,

                    "total_daihuan": 0,
                    "total_daishou": 0,
                    "total_borrow_amount": 0,

                    "first_borrow_time": 0,
                    "regist_time": 0,
                }

                for pnode in pnodes:
                    text = pnode.text.strip()
                    if text.startswith(u'正常还清'):
                        # 正常还清：34 次，逾期还清(1-15)：2 次，逾期还清(>15)：0 次
                        match = re.search(u'\u6b63\u5e38\u8fd8\u6e05\uff1a(\\d+?) \u6b21', text)
                        if match:
                            total_huanqing = match.group(1)
                            total_huanqing = int(total_huanqing)
                            tongji_info['total_huanqing'] = total_huanqing

                        match = re.search(u'\u903e\u671f\u8fd8\u6e05\(1-15\)\uff1a(\\d+?) \u6b21', text)
                        if match:
                            total_yuqi_15 = match.group(1)
                            total_yuqi_15 = int(total_yuqi_15)
                            tongji_info['total_yuqi_15'] = total_yuqi_15

                        match = re.search(u'\u903e\u671f\u8fd8\u6e05\(\>15\)\uff1a(\\d+?) \u6b21', text)
                        if match:
                            total_yuqi_16 = match.group(1)
                            total_yuqi_16 = int(total_yuqi_16)
                            tongji_info['total_yuqi_16'] = total_yuqi_16

                    if text.startswith(u'共计借入'):
                        # 共计借入：¥1,900,000， 待还金额：¥0.00， 待收金额： ¥0.00
                        u'共计借入：¥[0-9,\.]+?，'
                        if u'共计借入：' in text:
                            span = pnode.xpath('span[1]')[0]
                            total_borrow_amount = span.text.lstrip('¥')
                            total_borrow_amount = total_borrow_amount.replace(',', '')
                            total_borrow_amount = float(total_borrow_amount)
                            tongji_info['total_borrow_amount'] = total_borrow_amount

                            if '待还金额' in span.tail:
                                span = span.xpath('following-sibling::*[1]')[0]
                                total_daihuan = span.text.lstrip('¥')
                                total_daihuan = total_daihuan.replace(',', '')
                                total_daihuan = float(total_daihuan)
                                tongji_info['total_daihuan'] = total_daihuan

                            if '待收金额' in span.tail:
                                span = span.xpath('following-sibling::*[1]')[0]
                                total_daishou = span.text.strip().lstrip('¥')
                                total_daishou = total_daishou.replace(',', '')
                                total_daishou = float(total_daishou)
                                tongji_info['total_daishou'] = total_daishou

                    if text.startswith('第一次成功借款时间'):
                        # 第一次成功借款时间：2013/9/16 (34个月前)
                        text = pnode.text.strip()
                        match = re.search(u'\u7b2c\u4e00\u6b21\u6210\u529f\u501f\u6b3e\u65f6\u95f4\uff1a([0-9/]+?)\\s*\(',
                                  text)

                        if match:
                            first_borrow_time = match.group(1)
                            first_borrow_time = datetime.datetime.strptime(first_borrow_time,'%Y/%m/%d')
                            first_borrow_time = time.mktime(first_borrow_time.timetuple())
                            tongji_info['first_borrow_time'] = first_borrow_time

                        pass
                    if text.startswith('注册时间'):
                        # 注册时间：2013/9/4 (34个月前)
                        text = pnode.text.strip()
                        match = re.search(u'\u6ce8\u518c\u65f6\u95f4\uff1a([0-9/]+?)\\s*\(',
                                  text)

                        if match:
                            regist_time = match.group(1)
                            regist_time = datetime.datetime.strptime(regist_time,'%Y/%m/%d')
                            regist_time = time.mktime(regist_time.timetuple())
                            tongji_info['regist_time'] = regist_time
                        pass

                info['tongji_info'] = tongji_info

        # 历史借款
        nodes = tree.xpath(u"//p[text()='历史借款']")
        if nodes and len(nodes):
            nodes = nodes[0].xpath(u"following-sibling::table[@class='lendDetailTab_tabContent_table1']")
            if nodes and len(nodes):
                lishi_borrowed = []
                trs = nodes[0].xpath('tr')
                for tr in trs:
                    tds = tr.xpath('td')
                    if len(tds) == 6:
                        jiekuan = {}
                        jiekuan['url'] = tds[1].xpath('a')[0].attrib['href']
                        jiekuan['status'] = tds[4].text.strip()
                        jiekuan['lilv'] = float(tds[2].text.strip().rstrip('%'))
                        jiekuan['publish_time'] = tds[5].text.strip()
                        lishi_borrowed.append(jiekuan)
                info['lishi_borrowed'] = lishi_borrowed

        # 投资者列表
        nodes = tree.xpath(u"//div[@id='bidTable_div']")
        if nodes and len(nodes):
            node = nodes[0]
            aa = node.xpath("div/ol/li[@class='w266']/a[@class='listname']")
            info['bid_users'] = map(lambda i: i.attrib['href'], aa)


        return info

    # 获取用户信息
    @staticmethod
    def get_user_info(html):
        tree = etree.HTML(html)


        info = {
            'weighting_lilv': 0,
            "href": ""
        }

        # 加权投标利率（反映风险偏好）：
        nodes = tree.xpath(u'//th[text()="加权投标利率（反映风险偏好）： "]')
        if nodes and len(nodes):
            th = nodes[0];
            info['weighting_lilv'] = float(th.xpath('following-sibling::td/span')[0].text)

        # 已还完
        nodes = tree.xpath("//div[@class='borrowinglist']")
        if nodes and len(nodes):
            node = nodes[0]
            nodes = node.xpath("ul/li")
            for n in nodes:
                span = n.xpath("div[@class='rightlist fl']/div[@class='borrow_list']/table/tbody/tr/td/span["
                          "@class='cf7971a fNormal']")
                if span and len(span):
                    span = span[0]
                    if u'正在进行中' in span.text:
                        anodes = n.xpath("div[@class='rightlist fl']/div[@class='borrowlist_tit']/a[@href]")
                        if anodes and len(anodes):
                            anode = anodes[0]
                            info['href'] = anode.attrib['href']
                            break

        return info

    @staticmethod
    def get_my_loan_list(html):
        parser = etree.HTMLParser(encoding='utf-8')
        tree = etree.HTML(html, parser=parser)
        nodes = tree.xpath('//table[@class="receivetab c666666"]')
        my_loans = []
        if nodes and len(nodes):
            table = nodes[0]
            trs = table.xpath('tr')
            for tr in trs:
                tds = tr.xpath('td')
                if len(tds) == 6:
                    date = tds[0].text.strip()
                    date = datetime.datetime.strptime(date,'%Y/%m/%d %H:%M:%S')
                    date = time.mktime(date.timetuple())
                    date = long(date)

                    amount = tds[2].text.strip().lstrip(u'¥').replace(',', '')
                    amount = float(amount)

                    loan_id = tds[5].xpath('a')[0].text.strip()
                    url = tds[5].xpath('a')[0].attrib['href']
                    my_loans.append({"date": date, 'amount': amount, 'loan_id': loan_id, 'url': url})

        # 下一页
        href = None
        nodes = tree.xpath("//a[@class='nextpage']")
        if len(nodes) > 0:
            href = nodes[0].attrib.get('href')
            if href == 'javascript:void(0)':
                href = None

        return my_loans, href

    # 散标还款详情
    @staticmethod
    def get_my_loan_huankuan_detail(html):
        parser = etree.HTMLParser(encoding='utf-8')
        tree = etree.HTML(html, parser=parser)
        nodes = tree.xpath('//table')
        huankuans = []
        huanqing = True
        if nodes and len(nodes):
            table = nodes[0]
            trs = table.xpath('tr')
            for tr in trs:
                tds = tr.xpath('td')
                if len(tds) == 7:
                    benxi = float(tds[1].text.strip().lstrip(u'¥').replace(',', ''))
                    tiqian = int(tds[5].text.strip().lstrip(u'¥').split('/')[-1])

                    state = tds[6].xpath('span')[0].text.strip()
                    if u'逾期还款' in state:
                        pass
                    elif u'准时还款' in state:
                        pass
                    elif u'等待还款中' in state:
                        huanqing = False
                        benxi = float(tds[2].text.strip().lstrip(u'¥').replace(',', ''))
                    else:
                        huanqing = False
                        tiqian = 0
                        benxi = float(tds[2].text.strip().lstrip(u'¥').replace(',', ''))

                    huankuans.append([benxi, tiqian])
        return huankuans, huanqing

    # 判断是否已经签到
    @staticmethod
    def check_attendance(html):
        parser = etree.HTMLParser(encoding='utf-8')
        tree = etree.HTML(html, parser=parser)
        nodes = tree.xpath('//span[@id="btnGetPaiMoney"]')
        if nodes and len(nodes):
            return nodes[0].text == '已签'
        else:
            return False

    # 判断是否满标
    @staticmethod
    def is_manbiao(html):
        return u'结束时间：' in html









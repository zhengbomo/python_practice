#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
from bs4 import BeautifulSoup


class Analyzer(object):
    def __init__(self):
        pass

    @staticmethod
    def get_page_count(html):
        soup = BeautifulSoup(html, 'html.parser')

        # <span style="color:#65645F;">共75661篇</span>
        span = soup.find('span', style='color:#65645F;')
        return int(span.get_text().strip(u'共篇'))

    @staticmethod
    def get_poems_from_list_page(html):
        soup = BeautifulSoup(html, 'html.parser')
        sons = soup.findAll('div', class_='sons')
        poems = []
        for son in sons:
            a = son.find('a', target='_blank', style=' font-size:14px;')
            url = 'http://www.haoshiwen.org%s' % a.get('href')
            poems.append(url)

        return poems

    @staticmethod
    def check_poem_list_last_page(html):
        soup = BeautifulSoup(html, 'html.parser')
        page_node = soup.find('div', class_='pages')
        # <span class="disabled">下一页</span>
        next_node = page_node.find('a', text='下一页', attrs={"href": True})
        if next_node:
            return False
        else:
            return True

    @staticmethod
    def get_poem_detail(html, poem_url):
        soup = BeautifulSoup(html, 'html.parser')

        # <div class="shileft">
        div_content = soup.find('div', class_='shileft')

        son1 = div_content.find('div', class_='son1')
        title = son1.get_text().strip()

        dynasty = ''
        author = ''
        author_url = ''

        son2 = div_content.find('div', class_='son2')

        # 删除评分
        ping_fen = son2.find('div', class_='pingfen')
        if ping_fen:
            ping_fen.decompose()

        ps = son2.findAll('p', style='margin-top:0px;', recursive=False)
        for p in ps:
            span = p.find('span', text='朝代：', recursive=False)
            if span:
                span.decompose()
                dynasty = p.get_text()
                p.decompose()

            span = p.find('span', text='作者：', recursive=False)
            if span:
                span.decompose()
                a = p.find('a', recursive=False)
                if a:
                    author_url = 'http://www.haoshiwen.org/' + a.attrs['href']
                    author = a.get_text()
                    pass
                else:
                    # 匿名or无链接
                    author = p.get_text()

                p.decompose()

            span = p.find('span', text='原文：', recursive=False)
            if span:
                p.decompose()

        content = str(son2)

        # 分析赏析
        son5s = div_content.findAll('div', class_='son5', recursive=False)
        info_list = []
        for son5 in son5s:
            # 验证,只有2个p
            div = son5.find('div', recursive=False)
            ps = son5.findAll('p', recursive=False)
            if len(ps) == 2 and not div:
                a = ps[0].find('a', recursive=False)
                url = a.attrs['href']
                url = os.path.join('http://www.haoshiwen.org/', url)
                title2 = a.get_text()

                a = ps[1].find('a', text='...', recursive=False)
                if a:
                    a.decompose()
                summary = str(ps[1])

                poem_info = {"type": 1, "title": title2, "summary": summary, "content": "", "url": url}
                info_list.append(poem_info)

            else:
                # 过滤作者
                a = son5.find('a')
                href = a.attrs['href']
                if son5.attrs['style'] == u'overflow:auto;' and 'author' in href:
                    pass
                else:
                    print '出错'

        poem_content = {"type": 1, "title": title, "author": author, "authorurl": author_url, "dynasty": dynasty,
                        "content": content, "url": poem_url}
        return poem_content, info_list

    @staticmethod
    def get_info_detail(html):
        soup = BeautifulSoup(html, 'html.parser')

        # <div class="shileft">
        div_content = soup.find('div', class_='shileft')

        son1 = div_content.find('div', class_='son1', recursive=False)
        son1.decompose()

        shang_xi_content = div_content.find('div', class_='shangxicont', recursive=False)

        # 除去免责声明之后的节点
        p = shang_xi_content.find('p', style=' color:#858484;margin:0px; font-size:12px;line-height:160%;')
        next_siblings = p.next_siblings

        next_siblings = filter(lambda n: isinstance(n, bs4.element.Tag), next_siblings)
        for tag in next_siblings:
            tag.decompose()

        p.decompose()

        return str(div_content)

    @staticmethod
    def get_author_detail(html, url):
        soup = BeautifulSoup(html, 'html.parser')

        # <div class="shileft">
        div_content = soup.find('div', class_='shileft')

        son1 = div_content.find('div', class_='son1')
        author = son1.get_text().strip()

        son2 = div_content.find('div', class_='son2')
        img_div = son2.find('div', style=u' float:left; width:111px; height:155x; border:1px solid #E0DEDE; '
                                  u'text-align:center; padding-top:3px; padding-bottom:2px; margin-right:8px;',
                                recursive=False)

        img = img_div.find('img', recursive=False)
        avatar = img.attrs['src']
        img_div.decompose()

        content = str(son2)

        # 分析赏析
        son5s = div_content.findAll('div', class_='son5', recursive=False)
        info_list = []
        for son5 in son5s:
            # 验证,只有2个p
            div = son5.find('div', recursive=False)
            ps = son5.findAll('p', recursive=False)
            if len(ps) == 2 and not div:
                a = ps[0].find('a', recursive=False)
                content_url = a.attrs['href']
                content_url = os.path.join('http://www.haoshiwen.org/', content_url)
                title2 = a.get_text()

                a = ps[1].find('a', text='...', recursive=False)
                if a:
                    a.decompose()
                summary = str(ps[1])

                a_info = {"type": 2, "title": title2, "summary": summary, "content": "", "url": url}
                info_list.append(a_info)

            else:
                # 过滤作者
                a = son5.find('a')
                href = a.attrs['href']
                if son5.attrs['style'] == u'overflow:auto;' and 'author' in href:
                    pass
                else:
                    print '出错'

        author_content = {"type": 2, "name": author, "avatar": avatar, "content": content, "url": url}
        return author_content, info_list

    @staticmethod
    def get_poem_types(html):
        soup = BeautifulSoup(html, 'html.parser')

        # <div class="typeleft">
        div_content = soup.find('div', class_='typeleft')
        son2s = div_content.findAll("div", class_='son2', recursive=False)

        type_list = []
        for son2 in son2s:
            sleft = son2.find('div', class_='sleft', recursive=False)
            type_name = sleft.get_text().strip()

            sright = son2.find('div', class_='sright', recursive=False)
            aa = sright.findAll('a', recursive=False)
            types = []
            for a in aa:
                types.append((a.get_text(), 'http://www.haoshiwen.org' + a.attrs['href']))

            type_list.append((type_name, types))

        return type_list

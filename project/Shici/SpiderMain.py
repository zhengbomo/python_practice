#!/usr/bin/python
# -*- coding:utf-8 -*-

from Downloader import Downloader
from Analyzer import Analyzer
from SpiderDb import SpiderDb
import thread


class SpiderMain(object):
    def __init__(self):
        self.db = SpiderDb()
        pass

    def poem_list_crew(self):
        for i in range(1, 6):
            url = 'http://www.haoshiwen.org/type.php?x=%d' % i

            content = Downloader.get_html(url, 'poemlist')
            if content:
                page_count = Analyzer.get_page_count(content)
                # 分析
                for j in range(1, page_count + 1):
                    page_url = 'http://www.haoshiwen.org/type.php?x=%d&page=%d' % (i, j)
                    # 入库
                    self.db.insert_url(page_url, 1)

                    # 判断是否分析过
                    if self.db.url_analyzed(page_url):
                        pass
                    else:
                        content = Downloader.get_html(page_url, 'poemlist')
                        if content:
                            # 分析诗的列表
                            poems = Analyzer.get_poems_from_list_page(content)

                            if poems:
                                # 入库
                                self.db.insert_urls(poems, 2)
                                self.db.update_url(page_url)
                                print '%d %d/%d: %s' % (i, j, page_count, page_url)
                            else:
                                if Analyzer.check_poem_list_last_page(content):
                                    # 最后一页
                                    break
                                else:
                                    print u'分析失败'
                                    self.db.insert_error('analyze_poem_list_error', 3, 'reason', page_url)
                                    # 错误入库：analyze_poem_list_error

                        else:
                            print u'获取页面诗词列表错误'
                            self.db.insert_error('get_poem_list_error', 2, 'reason', page_url)
                            # 错误入库：get_poem_list_error
            else:
                print u'分析首页失败'
                self.db.insert_error('analyze_poem_list_first_page_error', 1, 'reason', page_url)
                # 错误入库：analyze_poem_list_first_page_error

    def poem_detail_crew(self):
        # update urls set analyzed = 1 where url = 'http://www.haoshiwen.org/view.php?id=9510'
        # 一条一条取
        total_count = 10
        c = 1
        while c < total_count:
            c += 1
            continue

            # 去除诗词的详情页url
            url = self.db.select_unanalyzed_url(2)

            if url is not None:
                url = url['url']

                # 判断是否抓取过
                if not self.db.poem_exists(url):
                    content = Downloader.get_html(url, 'poem')
                    if content:
                        try:
                            poem = Analyzer.get_poem_detail(content, url)
                            if poem:
                                # 分析成功,入库
                                poem_content = poem[0]
                                poem_info = poem[1]

                                self.db.insert_poem(poem_content)
                                self.db.insert_infomations(url, 1, poem_info)

                                self.db.update_url(url)

                                print "%d/%d %s %s" % (c, total_count, poem_content['title'], poem_content['url'])
                            else:
                                self.db.insert_error('analyze_poem_detail_error', 5, 'reason', url)
                        except Exception, e:
                            continue

                    else:
                        self.db.insert_error('get_poem_detail_error', 4, 'reason', url)
                else:
                    self.db.update_url(url)
            else:
                count = total_count

    def infomation_crew(self):
        # 一条一条取
        total_count = 20000
        i = 0
        while i < total_count:
            i += 1
            # 去除诗词的详情页url
            info = self.db.select_unanalyzed_infomation()

            if info is not None:
                # 下载分析
                url = info['url']
                html = Downloader.get_html(url, 'infomation')
                if html:
                    content = Analyzer.get_info_detail(html)
                    if content:
                        self.db.update_infomationurl(url, content)
                        print '%d/%d %s %s' % (i, total_count, info['title'], url)
                    else:
                        self.db.insert_error('analyze_info_detail_error', 7, 'reason', url)
                else:
                    self.db.insert_error('download_info_detail_error', 6, 'reason', url)
            else:
                # 没有了
                return

    def poem_author_crew(self):
        # 一条一条取
        total_count = 20000
        i = 0
        while i < total_count:
            i += 1
            # 去除诗词的详情页url
            authors = self.db.select_authors()
            cou = len(authors)
            i = 1
            for author in authors:
                url = author[0]

                if url is not None and url is not '':
                    # 判断是否存在
                    if not self.db.author_exists(url):
                        html = Downloader.get_html(url, 'author')
                        if html:
                            try:
                                author_info = Analyzer.get_author_detail(html, url)

                                if author_info:
                                    author_content = author_info[0]
                                    author_infos = author_info[1]

                                    self.db.insert_author(author_content)
                                    self.db.insert_infomations(url, 2, author_infos)
                                    print '%d/%d %s %s' % (i, cou, author_content['name'], url)
                                    i += 1
                                else:
                                    self.db.insert_error('analyze_author_detail_error', 9, 'reason', url)
                            except Exception, e:
                                print 'error %s' % (url,)

                        else:
                            self.db.insert_error('download_author_detail_error', 8, 'reason', url)
            else:
                # 没有了
                return

    def poem_type_crew(self):
        url = 'http://www.haoshiwen.org/type.php'
        content = Downloader.get_html(url, 'poemlist')
        if content:
            result = Analyzer.get_poem_types(content)
            k = 1
            for i in result:
                # 只处理类型
                if i[0] == u'类型':
                    for j in i[1]:
                        self.db.insert_poem_types(k, i[0], j[0], j[1])
                        print '\t' + j[0]
                    k += 1

    def poem_type_poem_list_craw(self):
        types = self.db.get_poem_types()
        for i in types:
            j = 1

            while True:
                page_url = i['url'] + "&page=" + str(j)

                # 入库
                self.db.insert_url(page_url, 3)

                # 判断是否分析过
                if self.db.url_analyzed(page_url):
                    j += 1
                    continue
                else:
                    content = Downloader.get_html(page_url, 'poemlist')
                    if content:
                        # 分析诗的列表
                        poems = Analyzer.get_poems_from_list_page(content)

                        if poems:
                            # 入库
                            self.db.insert_type_poems(i['id'], poems)
                            self.db.update_url(page_url)
                            print '%d: %s' % (j, page_url)
                            j += 1
                        else:
                            if Analyzer.check_poem_list_last_page(content):
                                # 最后一页
                                break
                            else:
                                print u'分析失败'
                                self.db.insert_error('analyze_poem_list_error', 3, 'reason', page_url)
                                # 错误入库：analyze_poem_list_error

                    else:
                        print u'获取页面诗词列表错误'
                        self.db.insert_error('get_poem_list_error', 2, 'reason', page_url)
                        # 错误入库：get_poem_list_error





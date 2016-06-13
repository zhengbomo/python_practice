#!/usr/bin/python
# -*- coding:utf-8 -*-  

from SpiderMain import SpiderMain

if __name__ == '__main__':
    spider = SpiderMain()

    # 1. 爬取诗词列表
    # spider.poem_list_crew()
    # count = spider.db.url_count()
    # errors = spider.db.select_error(range(1, 4))
    # print '诗词列表爬取完成,总共%d条数据, 错误%d条' % (count, len(errors))

    # 2. 爬取诗词详情
    # spider.poem_detail_crew()
    # count = spider.db.poem_count()
    # errors = spider.db.select_error(range(4, 6))
    # print '诗词详情爬取完成,总共%d条数据, 错误%d条' % (count, len(errors))

    # 3. 爬取诗人详情
    # spider.poem_author_crew()
    # count = spider.db.infomation_count()
    # errors = spider.db.select_error(range(6, 8))
    # print '诗词相关数据爬取完成,总共%d条数据, 错误%d条' % (count, len(errors))

    # 4. 爬去相关内容
    # spider.infomation_crew()
    # count = spider.db.infomation_count()
    # errors = spider.db.select_error(range(8, 10))
    # print '诗词相关数据爬取完成,总共%d条数据, 错误%d条' % (count, len(errors))

    print 'completed'

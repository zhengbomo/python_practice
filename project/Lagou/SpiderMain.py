#!/usr/bin/python
# -*- coding:utf-8 -*-
import re

from Spider import Spider

import sys
reload(sys)
sys.setdefaultencoding('utf8')


errors = []

spider = Spider()

# 爬数据
errors.extend(spider.crawljobs())

# 解析入库
errors.extend(spider.insert_jobs())

# 格式化职位的一些信息(薪资)
errors.extend(spider.analyze_jobs())

spider.adapt_job_city()

# 关联关键字
errors.extend(spider.associate_key_and_job())

# 输出错误
for e in errors:
    print e

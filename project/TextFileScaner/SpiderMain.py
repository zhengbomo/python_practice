#!/usr/bin/python
# -*- coding:utf-8 -*-
import os

from Scanner import Scanner


if __name__ == '__main__':
    # scan_folder = r'C:\Users\zheng\Desktop\classes-dex2jar.jar.src\client'
    # output_directory = u'C:\\Users\\zheng\\Desktop\\未命名文件夹\\1'
    # file_filter_pattern = r'.java'
    # search_pattern = r'BaseActivity'
    #
    # Scanner.scan_and_copy(scan_folder, file_filter_pattern, search_pattern, output_directory)
    # print 'complete'


    # 扫描目录下所有图片
    scan_folder = r'C:\Users\bomo\Desktop\fdsafdsa'
    file_filter_pattern = r'.java'
    content_pattern = r'/api/platformLinkIn/weibo'
    files = Scanner.scan(scan_folder, file_filter_pattern, content_pattern)
    for i in files:
        _, name = os.path.split(i)
        print i








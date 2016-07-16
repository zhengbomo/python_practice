#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import re

from Scanner import Scanner
from ImageScanner import ImageScanner


# 扫描工程里的target,比较BuildPhases差异
def scan_project():
    scanner = Scanner('/Users/zhengxiankai/Documents/Code/WebCacheTest/WebCacheTest.xcodeproj/project.pbxproj')

    target1 = 'WebCacheTest copy'
    target2 = 'WebCacheTest'

    build_phases1 = scanner.get_build_phases_by_target_name(target1)
    build_phases2 = scanner.get_build_phases_by_target_name(target2)

    print ' "{0}" 包含,而 "{1}" 不包含的文件\n'.format(target1, target2)
    for key1, kv1 in build_phases1.iteritems():
        kv2 = build_phases2[key1]
        for _, v in kv1.iteritems():
            if v not in kv2.itervalues():
                print '\t' + v
    print '\n'

    print ' "{0}" 包含,而 "{1}" 不包含的文件\n'.format(target2, target1)
    for key1, kv1 in build_phases2.iteritems():
        kv2 = build_phases1[key1]
        for _, v in kv1.iteritems():
            if v not in kv2.itervalues():
                print '\t' + v


# 扫描工程里的所有图片资源,并扫描出没有被引用的资源
def scan_image():
    folder = '/Users/zhengxiankai/Documents/uShareit/App/code/ushareit'
    scanner = ImageScanner(folder)

    # 获取所有图片资源,包括.imageset
    images = scanner.scan_image_name()

    names, match_values = scanner.scan_resources_in_path(images)
    print '\n--- unfound ---'
    for i in names:
        print i

    # 扫描的结果需要进一步确认,再删除
    print len(names)


if __name__ == '__main__':
    print '开始扫描'
    # scan_project()
    # scan_image()
    print '扫描结束'


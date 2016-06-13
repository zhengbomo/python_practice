#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import re
import shutil


class Scanner(object):
    def __init__(self):
        pass

    @staticmethod
    def __get_all_files(folder, file_filter):
        files = []
        for res in os.walk(folder):
            # (文件夹, 当前子文件夹, 当前子文件)
            for f in res[2]:
                if file_filter(f):
                    files.append('%s\%s ' % (res[0], f))
        return files

    @staticmethod
    def scan(folder, file_filter, pattern):
        files = Scanner.__get_all_files(folder, file_filter)

        match_files = []
        for f in files:
            # 读出内容，判断
            fo = open(f, "r")
            content = fo.read()
            m1 = re.search(pattern, content)
            if m1:
                match_files.append(f)
            fo.close()
        return match_files

    @staticmethod
    def copy_file_to_folder(files, folder):
        for f in files:
            path_name = os.path.split(f)
            target_file = os.path.join(folder, path_name[1])
            shutil.copy(f, target_file)

if __name__ == '__main__':
    scan_folder = r'C:\Users\zheng\Desktop\classes-dex2jar.jar.src\com\pianke\client'
    pattern = r'String getSigString\(String'

    fs = Scanner.scan(scan_folder, lambda f: re.search(r'.java', f), pattern)
    output_folder = u'C:\\Users\\zheng\\Desktop\\未命名文件夹\\1'
    Scanner.copy_file_to_folder(fs, output_folder)

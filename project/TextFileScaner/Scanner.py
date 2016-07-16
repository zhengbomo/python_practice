#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import re
import shutil


class Scanner(object):
    def __init__(self):
        pass

    @staticmethod
    def __get_all_files(folder, file_pattern):
        files = []
        for res in os.walk(folder):
            # (文件夹, 当前子文件夹, 当前子文件)
            for f in res[2]:
                if re.search(file_pattern, f):
                    files.append('%s/%s ' % (res[0], f))
        return files

    @staticmethod
    def scan(folder, file_pattern, pattern):
        files = Scanner.__get_all_files(folder, file_pattern)

        if pattern:
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
        else:
            return files

    def scan_and_copy(folder, file_pattern, pattern, output_folder):
        files = Scanner.scan(folder, file_pattern, pattern)
        Scanner.copy_file_to_folder(files, output_folder)

    @staticmethod
    def copy_file_to_folder(files, folder):
        for f in files:
            path_name = os.path.split(f)
            target_file = os.path.join(folder, path_name[1])
            shutil.copy(f, target_file)

#!/usr/bin/python
# -*- coding:utf-8 -*-
import os

# 扫描资源引用
import re


class ImageScanner(object):
    def __init__(self, path):
        self.path = path

    def scan_image_name(self):
        # 扫描所有图片资源,遇到.imageset结尾的文件夹,则返回
        files = self.__class__.__get_all_files(self.path, r'.png|.jpg|.pdf')
        image_files = set()
        for i in files:
            match = re.search(r'[\s\S]+?.imageset/', i, re.I)
            if match:
                image_files.add(match.group())
            else:
                image_files.add(i)

        return image_files

    def scan_resource_in_path(self, name, percent):
        files = self.__class__.__get_all_files(self.path, r'.h$|.m$|.mm$|.cpp$')

        # 过滤掉.framework的文件
        files = filter(lambda i: '.framework/' not in i, files)

        for path in files:
            f = open(path, 'r')
            content = f.read()
            f.close()

            match = re.search(r'{0}@"{1}"'.format('[\s\S]{15}', name), content, re.I)
            if match:
                print match.group()
                return True
            match = re.search(r'{0}@"{1}\..+?"'.format('[\s\S]{15}', name), content, re.I)
            if match:
                print match.group()
                return True
            print '%2f: %s' % (percent, path)
        return False


    def scan_resources_in_path(self, names):
        return self.scan_resources_with_pattern(names, r'.h$|.m$|.mm$|.cpp$|.xib$|.plist$')

    def scan_resources_with_pattern(self, names, pattern):
        files = self.__class__.__get_all_files(self.path, pattern)
        return self.scan_resources_in_files(files, names)


    def scan_resources_in_files(self, files, names):
        # 过滤掉.framework的文件
        files = filter(lambda i: '.framework/' not in i, files)

        # 过滤掉第三方库的文件
        files = filter(lambda i: not i.startswith('/Users/zhengxiankai/Documents/uShareit/App/code/ushareit/3rdparty/'),
                       files)

        # 过滤Pods文件夹下的文件
        files = filter(lambda i: not i.startswith('/Users/zhengxiankai/Documents/uShareit/App/code/ushareit/Pods/'),
                       files)

        match_values = []

        for index, path in enumerate(files):
            f = open(path, 'r')
            content = f.read()
            f.close()
            _, file_ext = os.path.splitext(path)


            match_names = []
            for i in names:
                # 取出名称
                _, name = os.path.split(i.rstrip('/'))

                name = name.replace(".imageset", '')

                # 去掉扩展名
                name, ext = os.path.splitext(name)

                if file_ext == '.xib':
                    if self.__class__.__find_resource_in_xib(content, name):
                        match_names.append(i)
                    else:
                        print '{0}/{1} {2} {3}'.format(index, len(files), path, name)
                elif file_ext == '.plist':
                    if name in content:
                        match_names.append(i)
                    else:
                        print '{0}/{1} {2} {3}'.format(index, len(files), path, name)
                else:
                    match = re.search(r'{0}@"{1}"'.format('', name), content, re.I)
                    if match:
                        match_values.append(match.group())
                        match_names.append(i)
                        continue

                    match = re.search(r'{0}@"{1}\..+?"'.format('', name), content, re.I)
                    if match:
                        match_values.append(match.group())
                        match_names.append(i)
                        continue
                    print '{0}/{1} {2} {3}'.format(index, len(files), path, name)

            for i in match_names:
                names.remove(i)

            if len(names) == 0:
                break
        return names, match_values

    def scan_file_ext_in_folder(self):
        files = self.__class__.__get_all_files(self.path, r'')
        exts = set()
        for i in files:
            _, name = os.path.split(i)
            n, ext = os.path.splitext(name)
            exts.add(ext)
        return exts


    @staticmethod
    def __get_all_files(folder, file_pattern):
        files = []
        for res in os.walk(folder):
            # (文件夹, 当前子文件夹, 当前子文件)
            for f in res[2]:
                if re.search(file_pattern, f, re.I):
                    files.append('%s/%s' % (res[0], f))
        return files

    @staticmethod
    def __find_resource_in_xib(content, resource):
        # image="ic_mp_speaker_pressed"
        pattern = 'image="{0}"'.format(resource)
        match = re.search(pattern, content, re.I)
        return match is not None



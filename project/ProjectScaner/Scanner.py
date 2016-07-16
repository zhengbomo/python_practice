#!/usr/bin/python
# -*- coding:utf-8 -*-
import json

import re


class Scanner(object):
    def __init__(self, path):
        self.path = path
        f = open(self.path, 'r')
        self.content = f.read()
        f.close()

    def get_build_phases_by_target_name(self, target):
        targets = self.get_targets()
        for key, name in targets.iteritems():
            if name == target:
                buildPhases = self.get_buildPhases(key, name)
                return {v: self.get_buildPhasesItems(k, v) for k, v in buildPhases.iteritems()}
                #
                # for k, v in buildPhases:
                #     items = self.get_buildPhasesItems(k, v)
                # return buildPhases.iteritems()
        return None




    def get_targets(self):
        # targets = (
        # 	6BDC5E181D25072700FFC201 /* WebCacheTest */,
        # 	6BDC5E311D25072700FFC201 /* WebCacheTestTests */,
        # 	6BDC5E3C1D25072700FFC201 /* WebCacheTestUITests */,
        # 	6B9870E91D2CA83B00DD19C3 /* Test */,
        # 	6B9871011D2CA83B00DD19C3 /* TestTests */,
        # 	6B98710C1D2CA83B00DD19C3 /* TestUITests */,
        # 	6B9871211D2CA93F00DD19C3 /* WebCacheTest copy */,
        # );

        match = re.search(r'targets = \(([\s\S]+?)\);', self.content, re.I)
        values = match.group(1)
        lines = values.splitlines()

        # 过滤空行
        lines = filter(lambda i: not re.match(r'^\s*$', i), lines)


        # 取出每一行
        lines = map(lambda i: i.strip(), lines)

        # 取出KeyValue
        lines = map(lambda i: re.search(r'(\w+?) /\* ([\s\S]+?) \*/', i), lines)

        return {i.group(1): i.group(2) for i in lines}

    def get_buildPhases(self, target_key, target_name):
        # 6B9871211D2CA93F00DD19C3 /* WebCacheTest copy */ = {
        # 	isa = PBXNativeTarget;
        # 	buildConfigurationList = 6B9871301D2CA93F00DD19C3 /* Build configuration list for PBXNativeTarget
        #       "WebCacheTest copy" */;
        # 	buildPhases = (
        # 		6B9871221D2CA93F00DD19C3 /* Sources */,
        # 		6B98712B1D2CA93F00DD19C3 /* Frameworks */,
        # 		6B98712C1D2CA93F00DD19C3 /* Resources */,
        # 	);
        # 	buildRules = (
        # 	);
        # 	dependencies = (
        # 	);
        # 	name = "WebCacheTest copy";
        # 	productName = WebCacheTest;
        # 	productReference = 6B9871331D2CA93F00DD19C3 /* WebCacheTest copy.app */;
        # 	productType = "com.apple.product-type.application";
        # };
        key = r'{key} /\* {name} \*/'.format(key=target_key, name=target_name)
        return self.__get_items(key, 'buildPhases')

    def get_buildPhasesItems(self, key, name):
        key = r'{key} /\* {name} \*/'.format(key=key, name=name)
        return self.__get_items(key, 'files')

    def __get_kv(self, value):
        lines = value.splitlines()

        # 过滤空行
        lines = filter(lambda i: not re.match(r'^\s*$', i), lines)


        # 取出每一行
        lines = map(lambda i: i.strip(), lines)

        # 取出KeyValue
        lines = map(lambda i: re.search(r'(\w+?) /\* ([\s\S]+?) \*/', i), lines)

        return {i.group(1): i.group(2) for i in lines}

    def __get_items(self, value, key):
        # 6B9871211D2CA93F00DD19C3 /* WebCacheTest copy */ = {
        # 	isa = PBXNativeTarget;
        # 	buildConfigurationList = 6B9871301D2CA93F00DD19C3 /* Build configuration list for PBXNativeTarget
        #       "WebCacheTest copy" */;
        # 	buildPhases = (
        # 		6B9871221D2CA93F00DD19C3 /* Sources */,
        # 		6B98712B1D2CA93F00DD19C3 /* Frameworks */,
        # 		6B98712C1D2CA93F00DD19C3 /* Resources */,
        # 	);
        # 	buildRules = (
        # 	);
        # 	dependencies = (
        # 	);
        # 	name = "WebCacheTest copy";
        # 	productName = WebCacheTest;
        # 	productReference = 6B9871331D2CA93F00DD19C3 /* WebCacheTest copy.app */;
        # 	productType = "com.apple.product-type.application";
        # };

        pattern = value + r' = \{[\s\S]+?\};'
        match = re.search(pattern, self.content, re.I)
        if match:
            value = match.group(0)

            # buildPhases = (
            # 	6B9871221D2CA93F00DD19C3 /* Sources */,
            # 	6B98712B1D2CA93F00DD19C3 /* Frameworks */,
            # 	6B98712C1D2CA93F00DD19C3 /* Resources */,
            # );

            match = re.search(key + r' = \(([\s\S]+?)\)', value)
            value = match.group(1)
            return self.__get_kv(value)
        else:
            return {}
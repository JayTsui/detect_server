#!/bin/env python
# -*- coding: UTF-8 -*-

import json
from jsoncomment import JsonComment
from jsonsempai.sempai import DottedDict


def load_conf(path):
    """
    加载配置文件类
    """
    ret = None
    parser = JsonComment(json)
    with open(path) as infile:
        ret = parser.load(infile, object_hook=DottedDict)
    return ret


def singleton(cls, *args, **kw):
    """
    单例模式修饰器
    """
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

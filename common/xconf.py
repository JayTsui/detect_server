#!/bin/env python
# -*- coding: UTF-8 -*-

import os
from .xutils import load_conf, singleton
from .xlog import LOG


@singleton
class ConfigLoader:
    """
    单例模式
    """

    def __init__(self):
        self.conf_dir = None
        self.__init_conf()

    def __init_conf(self):
        exec_dir = os.path.dirname(__file__)
        conf_dir = os.path.join(exec_dir, '..', 'conf')
        self.conf_dir = os.path.abspath(conf_dir)

    def get_conf(self, filename):
        """
        获取配置
        """
        path = os.path.join(self.conf_dir, filename)
        return load_conf(path)


@singleton
class ConfigManager(object):


    def __init__(self):
        self.conf = {}
        self.suffix = None
        self.init_conf()
        self.loader = ConfigLoader()


    def init_conf(self, debug=False):
        """
        定义配置文件环境
        """
        self.suffix = '.debug.json' if debug else '.json'


    def get_conf(self, conf_name):
        """
        读取文件配置
        """
        return self.loader.get_conf(conf_name + self.suffix)


    def get_db_conf(self, db_name):
        """
        获取数据库配置
        """
        conf_name = 'mysql'
        if conf_name not in self.conf:
            db_conf = self.get_conf('mysql')
            LOG.DEBUG('load db config: %r', db_name)
            self.conf[conf_name] = db_conf
        return self.conf[conf_name].get(db_name, {})

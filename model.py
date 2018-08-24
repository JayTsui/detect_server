#!/bin/env python
# -*- coding:utf-8 -*-

import time
import requests
import traceback

from common.xlog import LOG
from common.xconf import ConfigManager
from common.db_utils.xmysql import SqlHandler, XDBManager


class BaseModel(object):

    def __init__(self, db_conf):
        self.__db_handle = SqlHandler(**db_conf)


    def get_handle(self):
        return self.__db_handle
        

    def get_model(self, table):
        return XDBManager(self.__db_handle, table)


    def transaction(self, exec_func):
        """
        事务模式执行
        """
        try:
            self.__db_handle.transaction()
            f = exec_func()
            self.__db_handle.commit()
            return f
        except Exception as e:
            self.__db_handle.rollback()
            traceback.print_exc()
            raise e


class FaceIdentityModel(BaseModel):


    def __init__(self, db_conf=None):
        if not db_conf:
            db_conf = ConfigManager().get_db_conf('face_detect_data')
        BaseModel.__init__(self, db_conf)


    def get_model(self):
        return BaseModel.get_model(self, 'face_identity_info')

    
    def add(self, **kwargs):
        model = self.get_model()
        model.insert().fields(**kwargs).execute()


    def get(self, **kwargs):
        model = self.get_model()
        return model.select().where(**kwargs).query()

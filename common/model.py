#!/bin/env python
# -*- coding:utf-8 -*-

import traceback
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

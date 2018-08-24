#!/bin/env python
# -*-coding:utf-8-*-

from ..except_utils import XBaseErr


class DBConnectErr(XBaseErr):
    pass


class DBCloseErr(XBaseErr):
    pass


class DBQueryErr(XBaseErr):
    pass


class DBInsertErr(XBaseErr):
    """
    数据新增失败
    """
    def __init__(self, error):
        XBaseErr.__init__(self, err_desc=error)


class DBUpdateErr(XBaseErr):
    """
    数据更新失败
    """
    def __init__(self, error):
        XBaseErr.__init__(self, err_desc=error)

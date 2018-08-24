#!/bin/env python
# -*- coding: UTF-8 -*-

import traceback
import pymysql

from ..xlog import LOG
from .xexcept import DBConnectErr, DBQueryErr
from .xsql_builder import SqlBuilder


class SqlHandler(object):

    """
    数据库操作类
    """

    def __init__(self, host, user, pswd, dbname, port=3306, timeout=3):
        self.host       = host      # HOST
        self.port       = port      # 端口
        self.user       = user      # 帐号
        self.pswd       = pswd      # 密码
        self.dbname     = dbname    # 数据库名
        self.timeout    = timeout   # 超时
        self.__conn     = None      # 连接对象
        self.__cursor   = None      # 游标
        self.__tx_mode  = False     # 是否为事务模式
        self.connect()


    def open_tx_mode(self):
        """
        开启事务模式
        """
        self.__tx_mode = True

    
    def close_tx_mode(self):
        """
        关闭事务模式
        """
        self.__tx_mode = False


    def connect(self):
        """
        连接Mysql数据库
        """
        try:
            self.__conn = pymysql.connect(
                host            = self.host,
                port            = int(self.port),
                user            = self.user,
                passwd          = self.pswd,
                db              = self.dbname,
                connect_timeout = self.timeout,
                charset         = 'utf8'
            )
            return True
        except pymysql.Error as e:
            LOG.FATAL('database connection failed!')
            return False

    def reconnect(self):
        """
        重新连接
        """
        if not self.close():
            LOG.WARN('database close failed!')
        return self.connect()
    
    def close(self):
        try:
            self.__conn.close()
            return True
        except Exception as e:
            return False

    def connected(self):
        """
        是否保持连接
        """
        try:
            self.__conn.ping()
            return True
        except pymysql.Error as e:
            LOG.ERROR('database ping failed!')
        except AttributeError as e:
            LOG.ERROR('database ping failed!')
        return False


    def conn_verify(self):
        """
        保证连接存在
        """
        if not self.connected():
            return self.reconnect()
        return True


    def open_cursor(self):
        """
        打开游标
        """
        self.__cursor = self.__conn.cursor(
            cursor=pymysql.cursors.DictCursor
        )

    
    def close_cursor(self):
        """
        关闭游标
        """
        if self.__cursor:
            self.__cursor.close()


    def __format_sql(self, sql, args):
        """
        防止sql注入
        """
        if args is None or len(args) < 0:
            return sql
        for k, v in args.items():
            # if isinstance(v, str):
            #     v = self.__conn.escape_string(v)
            # if isinstance(v, unicode):
            #     v = self.__conn.escape_string(v.encode('utf8'))
            args[k] = v
        return sql.format(**args)

    
    def __exec_sql(self, func):
        """
        数据库操作执行函数
        """
        if not self.conn_verify():
            raise DBConnectErr()
        if not self.__tx_mode:
            self.__conn.autocommit(True)
            self.open_cursor()
        else:
            self.__conn.autocommit(False)
        f = func()
        if not self.__tx_mode:
            self.close_cursor()
        return f


    def execute(self, sql, args=None):
        """
        数据库增删改相关
        """
        def func():
            try:
                _sql = self.__format_sql(sql, args)
                LOG.DEBUG(_sql)
                return self.__cursor.execute(_sql)
            except pymysql.Error as e:
                if e.args[0] == 1062:
                    LOG.ERROR(str(e))
                    return -1
                LOG.ERROR('database execute failed!')
                LOG.ERROR("reason: %s" % traceback.format_exc())
                raise DBQueryErr()
        return self.__exec_sql(func)



    def query(self, sql, args=None):
        """
        数据库查询相关
        """
        def func():
            try:
                _sql = self.__format_sql(sql, args)
                LOG.DEBUG(_sql)
                self.__cursor.execute(_sql)
                return self.__cursor.fetchall()
            except pymysql.Error as e:
                LOG.ERROR('database query failed!')
                LOG.ERROR("reason: %s" % traceback.format_exc())
                raise DBQueryErr()
            return None
        return self.__exec_sql(func)


    def transaction(self):
        """
        事务开启
        """
        self.open_tx_mode()
        self.open_cursor()


    def commit(self):
        """
        事务提交
        """
        self.close_tx_mode()
        self.close_cursor()
        self.__conn.commit()


    def rollback(self):
        """
        事务回滚
        """
        self.close_tx_mode()
        self.close_cursor()
        if self.__conn:
            self.__conn.rollback()




class XDBManager(SqlBuilder):
    """
    自动构建sql管理类
    """

    def __init__(self, db_handle, table):
        SqlBuilder.__init__(self, table)
        self.db_handle = db_handle


    def execute_sql(self, sql, args=None):
        return self.db_handle.execute(sql, args)


    def query_sql(self, sql, args=None):
        return self.db_handle.query(sql, args)
        

    def execute(self):
        sql, args = self.build()
        return self.db_handle.execute(sql, args)


    def query(self):
        sql, args = self.build()
        return self.db_handle.query(sql, args)

    
    def query_first(self):
        ls = self.query()
        return ls[0] if ls else {}


# params = {
#     "host"  : "119.23.150.90",
#     "user"  : "admin",
#     "pswd"  : "fujia3188",
#     "dbname": "gunxueqiu"
# }
# db_handle = SqlHandler(**params)
# manager = TransactionManager(db_handle)

# @manager.transaction
# def add_gxq_(db_handle, name):
#     xdb = XSQLManager(db_handle, 't_invest_order').select(['', '', ''])


# if __name__=='__main__':
#     add_gxq_(name='jay')
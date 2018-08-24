#!/bin/env python
# -*- coding:utf-8 -*-

import copy

class SQL_MODE:
    INSERT = 0
    UPDATE = 1
    DELETE = 2
    SELECT = 3


class SqlBaseBuilder:

    def __init__(self, table):
        self.table = table

    def build_insert_sql(self, fields, values):
        sql_format = 'INSERT INTO `{table}` ({fields}) VALUES ({values})'
        return sql_format.format(table=self.table,
                                 fields=fields,
                                 values=values)

    def build_update_sql(self, fields_values, conditions):
        sql_format = 'UPDATE `{table}` SET {fields_values} {conditions}'
        return sql_format.format(table=self.table,
                                 fields_values=fields_values,
                                 conditions=conditions)

    def build_delete_sql(self, conditions):
        sql_format = 'DELETE FROM `{table}` {conditions}'
        return sql_format.format(table=self.table,
                                 conditions=conditions)

    def build_select_sql(self, fields, conditions):
        sql_format = 'SELECT {fields} FROM `{table}` {conditions}'
        return sql_format.format(table=self.table,
                                 fields=fields,
                                 conditions=conditions)

class SqlBuilder:


    def __init__(self, table):
        self.__builder      = SqlBaseBuilder(table)
        self.__exec_mode    = None
        self.__limit_clause = None
        self.__w_fields     = {} # 写入操作insert or update参数集
        self.__parameters   = {} # 参数format映射集
        self.__conditions   = {} # 查询where条件集
        self.__cus_cdicts   = [] # 自定义查询where条件集
        self.__order_list   = [] # 排序集
        self.__group_list   = [] # 分组集
        self.__select_list  = [] # 查询结果集
        self.__sl_sql_list  = [] # 自定义查询结果集
        


    def clear(self):
        self.__exec_mode    = None
        self.__limit_clause = None
        self.__w_fields.clear()
        self.__parameters.clear()
        self.__conditions.clear()
        del self.__cus_cdicts[:]
        del self.__order_list[:]
        del self.__group_list[:]
        del self.__select_list[:]
        del self.__sl_sql_list[:]


    def insert(self):
        self.__exec_mode = SQL_MODE.INSERT
        return self


    def update(self):
        self.__exec_mode = SQL_MODE.UPDATE
        return self


    def delete(self):
        self.__exec_mode = SQL_MODE.DELETE
        return self

    
    def select(self, params=None, sqls=None):
        param_list = {params} if isinstance(params, str) else params
        select_sql_list = {sqls} if isinstance(sqls, str) else sqls

        self.__exec_mode = SQL_MODE.SELECT
        self.__select_list = copy.deepcopy(param_list)
        self.__sl_sql_list = copy.deepcopy(select_sql_list)
        return self


    def field(self, key, value):
        self.__w_fields[key] = value
        self.__parameters[key] = value
        return self


    def fields(self, **kwargs):
        for key, val in kwargs.items():
            self.field(key, val)
        return self


    def where(self, *sqls, **kwargs):
        for sql in sqls:
            self.__cus_cdicts.append(sql)
        for k, v in kwargs.items():
            self.__conditions[k] = v
        return self


    def limit(self, length, offset=0):
        self.__limit_clause = ' LIMIT {offset}, {length}'.format(length=length, offset=offset)
        return self


    def order(self, fields, desc=False):
        if isinstance(fields, str):
            fields = {fields}
        for f in fields:
            self.__order_list.append({'field': f, 'desc': desc})
        return self


    def group(self, fields):
        if isinstance(fields, str):
            fields = {fields}
        for f in fields:
            self.__group_list.append(f)
        return self


    def __order_sql(self):
        if len(self.__order_list) > 0:
            order_sql = ' ORDER BY '
            order_list = []
            for item in self.__order_list:
                sql_format = '`{field}`'.format(field=item['field'])
                if item['desc']:
                    sql_format += ' DESC'
                order_list.append(sql_format)
            sql_format = ", ".join(order_list)
            return order_sql + sql_format
        return ''


    def __group_sql(self):
        if len(self.__group_list) > 0:
            group_sql = ' GROUP BY '
            group_list = []
            for field in self.__group_list:
                sql_format = '`{field}`'.format(field=field)
                group_list.append(sql_format)
            sql_format = ", ".join(group_list)
            return group_sql + sql_format
        return ''
    

    def __condition_sql(self):
        conditions = []
        for field, value in self.__conditions.items():
            ctype = '='
            if not isinstance(value, (int, list)):
                value = "'%s'" % value
            elif isinstance(value, list):
                ctype = 'IN'
                value = ", ".join(map(str, value))
            conditions.append('`{field}` {ctype} {value}'.format(field=field, value=value, ctype=ctype))
        for item in self.__cus_cdicts:
            conditions.append(item)
        sql_format = " AND ".join(conditions)
        return ('WHERE ' + sql_format) if len(conditions) > 0 else sql_format


    def __insert(self):
        fields = []
        values = []
        for k in self.__w_fields:
            fields.append('`{field}`'.format(field=k))
            values.append("'{%s}'" % k)
        fs = ", ".join(fields)
        vs = ", ".join(values)
        return self.__builder.build_insert_sql(fs, vs)


    def __update(self):
        fields = []
        for k in self.__w_fields:
            v = "'{%s}'" % k
            fields.append('`{field}` = {value}'.format(field=k, value=v))
        fields_values = ", ".join(fields)
        return self.__builder.build_update_sql(fields_values, self.__condition_sql())


    def __delete(self):
        return self.__builder.build_delete_sql(self.__condition_sql())


    def __select(self):
        if not (self.__select_list or self.__sl_sql_list):
            select_fields = '*'
        else:
            select_list = []
            if self.__select_list:
                for x in self.__select_list:
                    select_list.append('`{field}`'.format(field=x))
            if self.__sl_sql_list:
                for x in self.__sl_sql_list:
                    select_list.append(x)
            select_fields = ", ".join(select_list)
        conditions = self.__condition_sql() + self.__group_sql() + self.__order_sql()
        conditions = conditions + self.__limit_clause if self.__limit_clause != None else conditions
        return self.__builder.build_select_sql(select_fields, conditions)


    def __get_params(self):
        return self.__parameters


    def build(self):
        exec_func = {
            SQL_MODE.INSERT: self.__insert,
            SQL_MODE.UPDATE: self.__update,
            SQL_MODE.DELETE: self.__delete,
            SQL_MODE.SELECT: self.__select
        }
        return exec_func[self.__exec_mode](), self.__get_params()

        
    
if __name__=='__main__':
    db = SqlBuilder('user')
    db.select().where_ge(c_time=0).where_lt(c_time=50)
    sql, args = db.build()
    print(sql)
    print(sql.format(**args))
#!/bin/env python
# -*-coding:utf-8-*-

import time


def get_unix_time(time_str, time_format="%Y-%m-%d"):
    """
    获取unix时间戳
    """
    tmp = time.strptime(time_str, time_format)
    return int(time.mktime(tmp))


def get_time_str(timestamp, time_format="%Y-%m-%d %H:%M:%S"):
    """
    获取时间戳的日期时间字符串
    """
    if timestamp == 0:
        return ""
    tmp = time.localtime(timestamp)
    return time.strftime(time_format, tmp)


def get_date_str(timestamp, time_format="%Y%m%d"):
    """
    获取时间戳的日期字符串
    """
    return get_time_str(timestamp, time_format)


def last_midnight(ts):
    """
    获取当前时间的0点时间戳
    """
    ts -= time.timezone
    return ts - (ts % 86400) + time.timezone

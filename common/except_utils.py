#!/bin/env python
# -*-coding:utf-8-*-


class DisplayAttribute(object):
    def __str__(self):
        string = ''
        for key in self.__dict__:
            string += "%s: %s, " % (str(key), str(self.__dict__[key]))
        return string


class XBaseErr(Exception, DisplayAttribute):
    def __init__(self, err_code=0, err_desc=''):
        self.err_code = err_code
        self.err_desc = err_desc

    def __str__(self):
        return '%s: %s' % (self.__class__.__name__, DisplayAttribute.__str__(self))
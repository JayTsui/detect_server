#!/bin/env python
# -*- coding:utf-8 -*-

import json
import traceback
from common.xlog import LOG
from common.xerror import ECODE

from .except_utils import XBaseErr


class HttpInternalErr(XBaseErr):
    pass


def response(func):
    """
    HTTP接口修饰器
    """
    def _response(**kwargs):
        resp_code = None
        resp_data = None
        try:
            resp_code, resp_data = func(**kwargs)
        except HttpInternalErr as e:
            LOG.ERROR(traceback.format_exc(), e)
            resp_code = ECODE.E_INTERNAL_ERROR
        # 请求返回包
        resp_data = resp_data if resp_data else {}
        if resp_code != ECODE.E_SUCCESS:
            resp_data['error_msg'] = ECODE.get_desc(resp_code)
        resp_data['rtn'] = resp_code
        return json.dumps(resp_data)
    return _response

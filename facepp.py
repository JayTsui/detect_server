#!/bin/env python
# -*- coding:utf-8 -*-

import os
import json
import base64
import requests
from common.xlog import LOG
from model import FaceIdentityModel

class FaceDetector(object):

    """
    旷视人脸检测API
    """

    api_url = "https://api-cn.faceplusplus.com/facepp/v3/detect"

    def loadBase64Img(self, img_path):
        img_data = None
        with open(img_path, 'rb') as f:
            img_data = base64.b64encode(f.read())
        return img_data

    def _detect(self, img_path):
        image_base64 = self.loadBase64Img(img_path)
        response = requests.post(
            self.api_url,
            data=dict(
                api_key='xxx',
                api_secret='xxx',
                image_base64=image_base64,
                return_landmark=2,
                return_attributes="gender,age,smiling,headpose,facequality,blur,eyestatus,emotion,ethnicity,beauty,mouthstatus,eyegaze,skinstatus"
            ),
            timeout=10
        )
        if response.status_code != 200:
            LOG.ERROR('response status: %s', response.status_code)
            LOG.ERROR('response: %s', response.text)
            return None
        return response.json()

    def detect(self, img_path):
        try:
            return self._detect(img_path)
        except requests.exceptions.ConnectTimeout as e:
            LOG.ERROR('ConnectionTimeout: %s', e)
            return None
        except requests.exceptions.ConnectionError as e:
            LOG.ERROR('ConnectionError: %s', e)
            return None
        except requests.exceptions.ReadTimeout as e:
            LOG.ERROR('ReadTimeout: %s', e)
            return None


def detect():
    model = FaceIdentityModel()
    detector = FaceDetector()

    base_dir = os.path.join('E:\\', 'Data')
    identity_block = 'identities_0'
    identities_dir = os.path.join(base_dir, identity_block)
    
    i_dir_list = os.listdir(identities_dir)
    i_dir_list_len = len(i_dir_list)
    for i, identity in enumerate(i_dir_list):
        img_names = os.listdir(os.path.join(identities_dir, identity))
        img_names_len = len(img_names)
        for j, img_name in enumerate(img_names):
            record = model.get(block=identity_block, identity=identity, image=img_name)
            if record:
                print('Skip! dir: %s/%s, file: %s/%s' % (i, i_dir_list_len, j, img_names_len))
                continue

            img_path = os.path.join(identities_dir, identity, img_name)
            result = detector.detect(img_path)
            if result:
                mark_info = json.dumps(result)
                ret = model.add(block=identity_block, identity=identity, image=img_name, facepp_mark=mark_info)
                print('Successfully! dir: %s/%s, file: %s/%s' % (i, i_dir_list_len, j, img_names_len))


if __name__ == '__main__':
    detect()

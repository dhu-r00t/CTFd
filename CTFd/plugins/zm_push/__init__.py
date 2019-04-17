# -*- coding: utf-8 -*-``

import requests
import json
import os
import time

ZM_CONFIG = {}


def PushFirstBloodMessage(username, challenge):
    global ZM_CONFIG
    message = {
        "ctf_message": "[恭喜] {} 首先解出{}".format(username, challenge),
        "token": ZM_CONFIG["token"]
    }
    message = json.dumps(message)
    requests.post(ZM_CONFIG["url"], data=message)


def PushNoticeMessage(title, content):
    global ZM_CONFIG
    message = {
        "ctf_message": "[公告] {}\n{}".format(title, content),
        "token": ZM_CONFIG["token"]
    }
    message = json.dumps(message)
    requests.post(ZM_CONFIG["url"], data=message)


def load(app):
    global ZM_CONFIG
    config_file = open(os.path.dirname(__file__) + '/config.db', 'r')
    ZM_CONFIG = json.loads(config_file.read())
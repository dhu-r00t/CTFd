# -*- coding: utf-8 -*-``

import requests
import json
import os
import time

ZM_CONFIG = {}


def PushFirstBloodMessage(username, challenge):
    global ZM_CONFIG
    
    if not 'token' in ZM_CONFIG:
        return
    
    message = {
        "ctf_message": "[恭喜] {} 首先解出{}".format(username, challenge),
        "token": ZM_CONFIG["token"]
    }
    message = json.dumps(message)
    requests.post(ZM_CONFIG["url"], data=message)


def PushNoticeMessage(title, content):
    global ZM_CONFIG
    
    if not 'token' in ZM_CONFIG:
        return
    
    message = {
        "ctf_message": "[公告] {}\n{}".format(title, content),
        "token": ZM_CONFIG["token"]
    }
    message = json.dumps(message)
    requests.post(ZM_CONFIG["url"], data=message)


def load(app):
    global ZM_CONFIG
    try:
        with open(os.path.dirname(__file__) + '/config.db', 'r') as config_file:
            ZM_CONFIG = json.load(config_file)
    except (IOError, ValueError), e:
        pass # TODO: Log?


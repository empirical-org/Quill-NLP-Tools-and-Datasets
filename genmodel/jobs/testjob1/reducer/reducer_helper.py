#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import sleep
import json

def get_reduction(data):
    sleep(5)
    # look at the first character
    return (json.loads(data)['data'][0],)

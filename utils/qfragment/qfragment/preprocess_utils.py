#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""Preprocess sentences and reduce them."""
import re

def remove_double_commas(sent_str):
    return re.sub('\s*,[\s,]*', ', ', sent_str)

def remove_leading_noise(sent_str):
    return sent_str.lstrip(' ,')


#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""Generate a model capable of detecting subject-verb agreement errors"""
from flask import request, \
     render_template, flash, Flask
from flask import jsonify
import sys
sys.path.insert(0, 'sva')
from subject_verb_agreement import get_vector   


app = Flask(__name__)
app.secret_key = 'dddxasdasd' # needed for message flashing

@app.route('/sva/vector')
def sva_vector():
    s = request.args.get('s', '')
    if s:
        s = get_vector(s)
    return jsonify(s) 


@app.route('/')
def index():
    return "Hello"

if __name__ == '__main__':
    app.run(port=10200, host= '0.0.0.0', debug=True)

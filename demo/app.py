import json
from flask import Flask, render_template

app = application = Flask(__name__, static_url_path='/static')


@app.route("/")
def matches():

    return render_template("index.html")
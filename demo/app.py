import json
from flask import Flask, render_template

app = application = Flask(__name__, static_url_path='/static')

JSON_FILES = {"junkfood": "tree.json",
              "trucks": "selfdrivingtrucks_because.json"}


@app.route("/")
def index():

    return render_template("index.html")


@app.route("/viz/<dataset>")
def viz(dataset):

    if dataset not in JSON_FILES:
        return "Unknown dataset"

    return render_template("viz.html", input_file=JSON_FILES[dataset])
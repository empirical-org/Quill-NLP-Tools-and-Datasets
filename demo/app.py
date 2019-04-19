import json
from flask import Flask, render_template

app = application = Flask(__name__, static_url_path='/static')

topic_file = "demo/static/topics.json"

@app.route("/")
def matches():

    with open(topic_file) as i:
        topics = json.load(i)

    topics = [str(topic[0]) + ": " + topic[1] for topic in topics]

    return render_template("index.html", topics=topics)
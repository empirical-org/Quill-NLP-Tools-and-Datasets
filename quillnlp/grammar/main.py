from flask import Flask
from .pipeline import GrammarPipeline

app == Flask(__name__)

pipeline = GrammarPipeline()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return "This is Quill's grammar engine"
    else:
        sentence = request.form["sentence"]
        prompt = request.form["prompt"]
        return pipeline.check(sentence, prompt)

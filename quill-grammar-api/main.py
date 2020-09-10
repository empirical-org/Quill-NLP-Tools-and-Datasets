from flask import Flask, request
from grammar.pipeline import GrammarPipeline

app = Flask(__name__)

pipeline = GrammarPipeline()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return "This is Quill's grammar engine"
    else:
        sentence = request.form["sentence"]
        prompt = request.form["prompt"]
        errors = pipeline.check(sentence, prompt)
        if len(errors) > 0:
            errors.sort(reverse=True)
            error = errors[0]

            return {"text": error.text,
                    "type": error.type,
                    "index": error.index,
                    "model": error.model}

        return {"text": sentence,
                "type": None,
                "index": None,
                "model": None}


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080)

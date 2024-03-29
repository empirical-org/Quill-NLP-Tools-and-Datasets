import os
import yaml

from quillgrammar.grammar.pipeline import GrammarPipeline

from spell.serving import BasePredictor

MODEL_PATH = "model/model-best"

class GrammarPredictor(BasePredictor):

    def __init__(self):
        config_file = "quillgrammar/grammar_config_test.yaml"
        with open(config_file) as i:
            config = yaml.load(i, Loader=yaml.FullLoader)

        self.model = GrammarPipeline(MODEL_PATH, config)

    def predict(self, payload):

        sentence = payload["sentence"]
        prompt = payload["prompt"]
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

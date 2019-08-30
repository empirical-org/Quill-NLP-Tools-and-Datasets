from overrides import overrides
import numpy as np

from allennlp.common.util import JsonDict
from allennlp.data import Instance
from allennlp.predictors.predictor import Predictor


@Predictor.register('topic_classifier')
class TopicPredictor(Predictor):
    """Predictor wrapper for the Basic Topic Classifier"""
    @overrides
    def predict_json(self, json_dict: JsonDict) -> JsonDict:
        text = json_dict['text']
        instance = self._dataset_reader.text_to_instance(text=text)
        print("I", instance)
        output = self.predict_instance(instance)

        probs = output["probs"]
        max_prob_index = np.argmax(probs)

        label = self._model.vocab.get_token_from_index(max_prob_index, namespace="labels")

        return {"output": output, "label": label}

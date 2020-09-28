import os
from transformers import AlbertTokenizer, AutoModelWithLMHead, pipeline


synonyms = {
    "am": ["'m"],
    "are": ["'re"],
    "is": ["'s"],
    "have": ["'ve"],
    "will": ["'ll", "wo"],
    "would": ["'d"],
    "had": ["'d"],
    "wo": ["will"],
    "ca": ["can"],
    "'m": ["am"],
    "'re": ["re"],
    "'s": ["is"],
    "'ve": ["have"],
    "'ll": ["will"],
    "'d": ["would", "had"],
    "can": ["ca"],
}


class BertPredictor(object):
    """Interface for constructing custom predictors."""

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.pipeline = pipeline('fill-mask', model=model, tokenizer=tokenizer, topk=100)

    def correct_instance(self, instance):

        sentence = instance["sentence"]
        for target in instance["targets"]:

            token = target["token"]
            start = target["start"]
            alternative_forms = set(target["alternatives"])
            for f in target["alternatives"]:
                if f in synonyms:
                    alternative_forms.update(synonyms[f])

            masked_sentence = sentence[:start] + self.tokenizer.mask_token + sentence[start+len(token):]
            predictions = self.pipeline(masked_sentence)

            print(masked_sentence)
            for prediction in predictions:
                print("P", prediction)

            for prediction in predictions:
                predicted_token = self.pipeline.tokenizer.convert_ids_to_tokens(prediction["token"])
                predicted_token = predicted_token.replace("▁", "")  # for Albert tokenizer

                # If the token itself is ranked highest in the list of predictions,
                # then it is likely correct.
                if predicted_token.lower() == token.lower():
                    break

                # If a synonym of the token is ranked highest in the list of predictions,
                # then it is likely correct.
                elif token.lower() in synonyms and predicted_token in synonyms[token.lower()]:
                    break

                # If an alternative form is ranked highest in the list of predictions,
                # then the token is likely an error.
                elif predicted_token in alternative_forms:
                    correct_sentence = masked_sentence.replace(self.pipeline.tokenizer.mask_token,
                                                               predicted_token)
                    return {"correct": correct_sentence,
                            "original_token": token,
                            "start": start,
                            "predicted_token": predicted_token,
                            "error_type": target["error_type"]}

        return {"correct": sentence,
                "error": None}

    def predict(self, instances, **kwargs):
        """Performs custom prediction.

        Instances are the decoded values from the request. They have already
        been deserialized from JSON.

        Args:
            instances: A list of prediction input instances.
            **kwargs: A dictionary of keyword args provided as additional
                fields on the predict request body.

        Returns:
            A list of outputs containing the prediction results. This list must
            be JSON serializable.
        """
        return [self.correct_instance(instance) for instance in instances]

    @classmethod
    def from_path(cls, model_dir):
        """Creates an instance of Predictor using the given path.

        Loading of the predictor should be done in this method.

        Args:
            model_dir: The local directory that contains the exported model
                file along with any additional files uploaded when creating the
                version resource.

        Returns:
            An instance implementing this Predictor class.
        """

        model = AutoModelWithLMHead.from_pretrained(os.path.join(model_dir, "model"))
        tokenizer = AlbertTokenizer.from_pretrained(os.path.join(model_dir, "tokenizer"))

        return cls(model, tokenizer)

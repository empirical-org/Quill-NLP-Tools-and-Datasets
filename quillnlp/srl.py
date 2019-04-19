from allennlp.predictors.predictor import Predictor


def perform_srl(responses, prompt):
    """ Perform semantic role labeling on a list of responses, given a prompt."""

    predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/srl-model-2018.05.25.tar.gz")

    sentences = [{"sentence": prompt + " " + response} for response in responses]
    output = predictor.predict_batch_json(sentences)

    full_output = [{"sentence": prompt + response,
                    "response": response,
                    "srl": srl} for (response, srl) in zip(responses, output)]

    return full_output

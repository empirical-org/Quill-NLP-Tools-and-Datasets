import ndjson
from tqdm import tqdm
import plac
from sklearn.metrics import classification_report
from allennlp.models.archival import load_archive
from allennlp.predictors import Predictor
from quillnlp.models.basic_topic_classifier import BasicTopicClassifier
from quillnlp.dataset_readers.quill_responses import QuillResponsesDatasetReader
from quillnlp.predictors.topic import TopicPredictor


def main(test_file, model):

    with open(test_file) as i:
        inputs = ndjson.load(i)

    archive = load_archive(model)
    predictor = Predictor.from_archive(archive, 'topic_classifier')

    correct = 0
    predicted = []
    gold = []
    for input in tqdm(inputs):
        result = predictor.predict_json(input)
        predicted.append(result["label"])
        gold.append(input["label"])
        if result["label"] == input["label"]:
            correct += 1

    accuracy = correct/len(inputs)
    print(correct, "/", len(inputs), "=", accuracy)

    print(classification_report(gold, predicted))

if __name__ == "__main__":
    plac.call(main)

import csv
import yaml

from tqdm import tqdm
from sklearn.metrics import classification_report, precision_recall_fscore_support
from sklearn.preprocessing import MultiLabelBinarizer

from quillgrammar.grammar.pipeline import GrammarPipeline
from quillnlp.spelling.bing import correct_sentence_with_bing

csv_file = "quillgrammar/combined_turk_data.csv"
config_file = "tests/config_current.yaml"


def test_grammar_pipeline():

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    data = []
    with open(csv_file) as i:
        reader = csv.reader(i)
        for row in reader:
            sentence, prompt, _ = row
            data.append((sentence, prompt))

    with open("combined_turk_output_20201013_bing.tsv", "w") as o:
        csv_writer = csv.writer(o, delimiter="\t")

        for (sentence, prompt) in tqdm(data, desc="Predicting errors"):

            sentence = correct_sentence_with_bing(sentence)

            errors = pipeline.check(sentence, prompt)
            predicted_error = None
            if len(errors) > 0:
                predicted_error = errors[0]

            if predicted_error is None:
                csv_writer.writerow([sentence, "", "", ""])
            else:
                csv_writer.writerow([sentence, predicted_error.type,
                                    predicted_error.index, predicted_error.text])


test_grammar_pipeline()

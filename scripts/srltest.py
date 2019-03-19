from allennlp.predictors.predictor import Predictor
import json
from tqdm import tqdm
import re


def perform_srl():

    predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/srl-model-2018.05.25.tar.gz")
    sentence_start = "Schools should not allow junk food to be sold on campus "

    sentences = []
    with open("sentences.txt") as i:
      for line in i:
        line = line.strip()
        sentence = sentence_start + line
        sentences.append(sentence)

    # TODO: Prediction is much more efficient if we feed the sentences as a batch.
    output = []
    for sentence in tqdm(sentences):
        x = predictor.predict(sentence)
        output.append(x)

    with open("output.json", "w") as o:
        json.dump(output, o)


def parse_srl(f):
    all_sentences = []
    with open(f) as i:
        d = json.load(i)
        for sent in d:
            sentence_info = []
            sentence_info.append([" ".join(sent["words"][11:])])
            for verb in sent["verbs"]:
                verb_string = verb["verb"]
                arg0_string = " "
                arg1_string = " "
                arg2_string = " "

                arg0 = re.search("\[ARG0: (.*?)\]", verb["description"])
                if arg0:
                    arg0_string = arg0.group(1)
                arg1 = re.search("\[ARG1: (.*?)\]", verb["description"])
                if arg1:
                    arg1_string = arg1.group(1)

                arg2 = re.search("\[ARG2: (.*?)\]", verb["description"])
                if arg2:
                    arg2_string = arg2.group(1)

                sentence_info.append([verb_string, arg0_string, arg1_string, arg2_string])

            all_sentences.append(sentence_info)

    for sentence in all_sentences:
        flat_list = [i for l in sentence for i in l]
        print("\t".join(flat_list))


perform_srl()
parse_srl("output.json")

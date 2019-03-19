#from allennlp.predictors.predictor import Predictor
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

    modal_verbs = set(["will", "shall", "may", "might", "can", "could", "must", "ought to",
                       "should", "would", "used to", "need"])

    aux_verbs = set(["do", "does"])

    all_sentences = []
    with open(f) as i:
        d = json.load(i)
        for sent in d:
            sentence_info = {"sentence": " ".join(sent["words"][11:]),
                             "meta": [],
                             "verbs": []}

            auxiliary = None
            for verb in sent["verbs"]:
                verb_string = verb["verb"].lower()

                if verb_string in modal_verbs:
                    sentence_info["meta"].append("modal")
                    auxiliary = verb_string

                elif verb_string in aux_verbs:
                    sentence_info["meta"].append("auxiliary")
                    auxiliary = verb_string

                else:
                    arg0_string = "-"
                    arg1_string = "-"
                    arg2_string = "-"

                    arg0 = re.search("\[ARG0: (.*?)\]", verb["description"])
                    if arg0:
                        arg0_string = arg0.group(1)
                    arg1 = re.search("\[ARG1: (.*?)\]", verb["description"])
                    if arg1:
                        arg1_string = arg1.group(1)

                    arg2 = re.search("\[ARG2: (.*?)\]", verb["description"])
                    if arg2:
                        arg2_string = arg2.group(1)

                    if auxiliary is not None:
                        verb_string += f" ({auxiliary})"
                        auxiliary = None

                    sentence_info["verbs"].append([verb_string, arg0_string, arg1_string, arg2_string])

            all_sentences.append(sentence_info)

    for sentence in all_sentences:
        output_list = [sentence["sentence"], " ".join(sentence["meta"][1:])]  # strip the first "meta" label: main clause
        for verb in sentence["verbs"]:
            for item in verb:
                output_list.append(item)

        print("\t".join(output_list))


#perform_srl()
parse_srl("data/srl_output.json")

from allennlp.predictors.predictor import Predictor
import json
from tqdm import tqdm
import re
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline
from collections import defaultdict


def perform_srl(f, sentence_start):

    predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/srl-model-2018.05.25.tar.gz")

    sentences, responses = [], []
    with open(f) as i:
      for line in i:
        line = line.strip()
        sentence = sentence_start + line
        responses.append(line)
        sentences.append({"sentence": sentence})

    output = predictor.predict_batch_json(sentences)

    full_output = [{"sentence": sentence_start + response,
                    "response": response,
                    "srl": srl} for (response, srl) in zip(responses, output)]

    return full_output


def group_by_main_verb(sentences):

    groups = defaultdict(list)
    for sentence in sentences:
        if len(sentence["verbs"]) > 3:
            main_verb = sentence["verbs"][3][0]
            groups[main_verb].append(sentence)
        else:
            groups["-"].append(sentence)

    return groups


def cluster(list_of_texts):
    pipeline = Pipeline([
        ("vect", CountVectorizer()),
        ("tfidf", TfidfTransformer()),
        ("clust", KMeans(n_clusters=3))
    ])

    try:
        clusters = pipeline.fit_predict(list_of_texts)
    except ValueError:
        clusters = list(range(len(list_of_texts)))
    return clusters


def identify_argument(verb, argument_number):
    arg0 = re.search(f"\[ARG{argument_number}: (.*?)\]", verb["description"])
    if arg0:
        return arg0.group(1)
    return "-"


def parse_srl_output(srl_output_list):

    modal_verbs = set(["will", "shall", "may", "might", "can", "could", "must", "ought to",
                       "should", "would", "used to", "need"])

    aux_verbs = set(["do", "does"])

    all_sentences = []
    for sent in srl_output_list:
        sentence_info = {"sentence": sent["sentence"],
                         "response": sent["response"],
                         "meta": [],
                         "verbs": []}

        auxiliary = None
        for verb in sent["srl"]["verbs"]:
            verb_string = verb["verb"].lower()

            if verb_string in modal_verbs:
                sentence_info["meta"].append("modal")
                auxiliary = verb_string

            elif verb_string in aux_verbs:
                sentence_info["meta"].append("auxiliary")
                auxiliary = verb_string

            else:
                arg0_string = identify_argument(verb, 0)
                arg1_string = identify_argument(verb, 1)
                arg2_string = identify_argument(verb, 2)

                if auxiliary is not None:
                    verb_string += f" ({auxiliary})"
                    auxiliary = None

                sentence_info["verbs"].append([verb_string, arg0_string, arg1_string, arg2_string])

        all_sentences.append(sentence_info)

    main_verb_groups = group_by_main_verb(all_sentences)
    for main_verb in main_verb_groups:
        texts = []
        for sentence in main_verb_groups[main_verb]:
            if len(sentence["verbs"]) > 3:
                texts.append(" ".join(sentence["verbs"][3]))
            else:
                texts.append("")

        text_clusters = cluster(texts)

        print("--")
        print(main_verb)
        for (sentence, c) in zip(main_verb_groups[main_verb], text_clusters):
            print(c, sentence["response"])


    """
    for sentence in all_sentences:
        output_list = [sentence["response"], " ".join(sentence["meta"][1:])]  # strip the first "meta" label: main clause
        for verb in sentence["verbs"][3:]:
            for item in verb:
                output_list.append(item)

        print("\t".join(output_list))
    """

sentence_start = "Schools should not allow junk food to be sold on campus "

srl_out = perform_srl("scripts/data/sentences.txt", sentence_start)
parse_srl_output(srl_out)

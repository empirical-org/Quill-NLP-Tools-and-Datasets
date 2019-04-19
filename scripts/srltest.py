import json
from quillnlp.utils import detokenize
from quillnlp.preprocess import lemmatize
from quillnlp.cluster import cluster
import re
from collections import defaultdict
from quillnlp.topics import find_topics, get_topics_in_document, print_topics


def group_by_main_verb(sentences):

    groups = defaultdict(list)
    for sentence in sentences:
        if len(sentence["verbs"]) > 3:
            main_verb = sentence["verbs"][3][0].split("(")[0]  # verbs are strings like "allow (should)"
            groups[main_verb].append(sentence)
        else:
            groups["-"].append(sentence)

    return groups


def identify_argument(verb, argument_number):
    arg0 = re.search(f"\[ARG{argument_number}: (.*?)\]", verb["description"])
    if arg0:
        return arg0.group(1)
    return "-"


def parse_srl_output(srl_output_list, topic_model, dictionary):

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
                arg0_string = detokenize(identify_argument(verb, 0))
                arg1_string = detokenize(identify_argument(verb, 1))
                arg2_string = detokenize(identify_argument(verb, 2))

                if auxiliary is not None:
                    verb_string += f" ({auxiliary})"
                    auxiliary = None

                sentence_info["verbs"].append([verb_string, arg0_string, arg1_string, arg2_string])

        all_sentences.append(sentence_info)

    main_verb_groups = group_by_main_verb(all_sentences)
    for main_verb in main_verb_groups:
        print("--")
        print(main_verb)

        for sentence in main_verb_groups[main_verb]:
            if len(sentence["verbs"]) > 3:
                text = " ".join(sentence["verbs"][3])
                lemmas = lemmatize(text)
                topics = get_topics_in_document(lemmas, dictionary, topic_model)
                topics.sort(key=lambda x: x[1], reverse=True)
                print(sentence["response"], topics[0])

        """
        texts = []
        for sentence in main_verb_groups[main_verb]:
            if len(sentence["verbs"]) > 3:
                texts.append(" ".join(sentence["verbs"][3]))
            else:
                texts.append("")

        
        text_clusters = cluster(texts)

        print("--")
        print(main_verb)

        clusters_and_sentences = list(zip(text_clusters, main_verb_groups[main_verb]))
        clusters_and_sentences.sort(key=lambda x:x[0])

        for (c, sentence) in clusters_and_sentences:
            print(c, sentence["response"])
        """


    """
    for sentence in all_sentences:
        output_list = [sentence["response"], " ".join(sentence["meta"][1:])]  # strip the first "meta" label: main clause
        for verb in sentence["verbs"][3:]:
            for item in verb:
                output_list.append(item)

        print("\t".join(output_list))
    """


prompt = "Schools should not allow junk food to be sold on campus"
f = "scripts/data/sentences.txt"

responses = []
with open(f) as i:
    for line in i:
        line = line.strip()
        responses.append(line)

"""
srl_out = perform_srl(responses, prompt)
with open("srl_out.json", "w") as o:
    json.dump(srl_out, o)
"""

topic_model, dictionary = find_topics([lemmatize(r) for r in responses], num_topics=5)

with open("srl_out.json", "r") as i:
    srl_out = json.load(i)
parse_srl_output(srl_out, topic_model, dictionary)
print_topics(topic_model)

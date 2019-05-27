import json
import spacy
from quillnlp.utils import detokenize
from quillnlp.preprocess import lemmatize, postag
from quillnlp.cluster import cluster
import re
from collections import defaultdict
from quillnlp.topics import find_topics, get_topics_in_document, print_topics

en = spacy.load("en")


def group_by_main_verb(sentences):

    groups = {"-": {"-": []}}
    for sentence in sentences:
        if len(sentence["verbs"]) > 3:
            main_verb = sentence["verbs"][3][0].split("(")[0].strip()  # verbs are strings like "allow (should)"
            main_verb_arg0 = sentence["verbs"][3][1].lower()
            if main_verb_arg0 not in groups:
                groups[main_verb_arg0] = {}
            if main_verb not in groups[main_verb_arg0]:
                groups[main_verb_arg0][main_verb] = []
            groups[main_verb_arg0][main_verb].append(sentence)
        else:
            groups["-"]["-"].append(sentence)

    #print(json.dumps(groups, indent=4))
    #input()
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

    output = {"name": prompt,
              "children": []}

    grouped_responses = group_by_main_verb(all_sentences)
    for main_subj in grouped_responses:
        print("--")
        print(main_subj)

        main_subject_branch = {"name": main_subj,
                               "children": []}

        for main_verb in grouped_responses[main_subj]:
            print("-", main_verb)
            topic_dictionary = defaultdict(list)
            main_verb_branch = {"name": main_verb,
                                "children": []}
            for sentence in grouped_responses[main_subj][main_verb]:
                if len(sentence["verbs"]) > 3:
                    argument_strings = []
                    for verb_frame in sentence["verbs"][3:]:
                        argument_strings += verb_frame[1:]
                    text = " ".join(argument_strings)

                    lemmas = lemmatize(text)
                    topics = get_topics_in_document(lemmas, dictionary, topic_model)
                    topics.sort(key=lambda x: x[1], reverse=True)
                    print(sentence["response"], topics[0])
                    best_topic = topics[0][0]
                    topic_dictionary[best_topic].append(sentence["response"])

            for topic in topic_dictionary:
                topic_branch = {"name": f"topic{topic}",
                                "children": []}

                for response in topic_dictionary[topic]:
                    topic_branch["children"].append({"name": response,
                                                    "value": 1})

                main_verb_branch["children"].append(topic_branch)

            main_subject_branch["children"].append(main_verb_branch)

        output["children"].append(main_subject_branch)

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

    # This is the output for the Google doc
    for sentence in all_sentences:
        output_list = [sentence["response"], " ".join(sentence["meta"][1:])]  # strip the first "meta" label: main clause
        for verb in sentence["verbs"][3:]:
            for item in verb:
                output_list.append(item)

        print("\t".join(output_list))

    # This is the output for the visualization tree.
    with open("tree.json", "w") as o:
        json.dump(output, o)

    topics = list(topic_model.print_topics())
    with open("topics.json", "w") as o:
        json.dump(topics, o)


prompt = "Schools should not allow junk food to be sold on campus"
f = "scripts/data/sentences.txt"

responses = []
with open(f) as i:
    for line in i:
        line = line.strip()
        responses.append(line)

topic_model, dictionary = find_topics([lemmatize(r) for r in responses], num_topics=5)

with open("srl_out.json", "r") as i:
    srl_out = json.load(i)

# correct sentences
for x in srl_out:
    x["sentence"] = x["sentence"].replace(prompt, prompt + " ")

parse_srl_output(srl_out, topic_model, dictionary)
print_topics(topic_model)

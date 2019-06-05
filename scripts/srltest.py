import json
import spacy
from collections import defaultdict

from allennlp.models.archival import load_archive
from allennlp.predictors.predictor import Predictor

from quillnlp.utils import detokenize
from quillnlp.models.basic_topic_classifier import BasicTopicClassifier
from quillnlp.dataset_readers.quill_responses import QuillResponsesDatasetReader
from quillnlp.predictors.topic import TopicPredictor

coref_predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/coref-model-2018.02.05.tar.gz")
en = spacy.load("en")

VERB_MAP = {"s": "be",
            "is": "be",
            "ca": "can",
            "wo": "will"}

SUBJECTS_TO_IGNORE = set(["I", "some", "some people"])

#PROMPT = "Schools should not allow junk food to be sold on campus"
#CLASSIFIER_FILE = "models/junkfood_but_topic_classifier_glove.tar.gz"
#INPUT_FILE = "scripts/data/sentences.txt"
#SRL_OUTPUT_FILE = "srl_out.json"
#NUMBER_OF_VERBS_IN_PROMPT = 3

PROMPT = "The United States is investing in self-driving trucks because"
CLASSIFIER_FILE = None
INPUT_FILE = "data/raw/selfdrivingtrucks_because.tsv"
SRL_OUTPUT_FILE = "scripts/data/selfdrivingtrucks_because_srl.json"
NUMBER_OF_VERBS_IN_PROMPT = 3


OUTPUT_VISUALIZATION_FILE = "selfdrivingtrucks_because.json"
OUTPUT_TSV_FILE = "selfdrivingtrucks_because.tsv"

MODAL_VERBS = set(["will", "shall", "may", "might", "can", "could", "must", "ought to",
                   "should", "would", "used to", "need"])
AUX_VERBS = set(["do", "does"])


def group_by_arg0_and_verb(sentences):
    """
    Groups the sentences by their main verb and its arg0. This is needed to produce the
    clustered data for the D3 visualization.
    :param sentences:
    :return: a dictionary of the form {arg0: {main_verb: [sentence1, sentence2, ...]}}
    """

    groups = {"-": {"-": []}}
    for sentence in sentences:
        if len(sentence["verbs"]) > NUMBER_OF_VERBS_IN_PROMPT:
            main_verb = sentence["verbs"][NUMBER_OF_VERBS_IN_PROMPT][0].split("(")[0].strip()  # verbs are strings like "allow (should)"
            main_verb_arg0 = sentence["verbs"][NUMBER_OF_VERBS_IN_PROMPT][2].lower()
            if main_verb_arg0 not in groups:
                groups[main_verb_arg0] = {}
            if main_verb not in groups[main_verb_arg0]:
                groups[main_verb_arg0][main_verb] = []
            groups[main_verb_arg0][main_verb].append(sentence)
        else:
            groups["-"]["-"].append(sentence)

    return groups


def identify_argument(verb, argument_number, words):
    """
    Identifies a given argument number of a verb. Returns its string and start+end
    indexes. This allows easier integration of the semantic role labelling and
    coreference results.
    """
    indexes = []
    arg_tokens = []

    print(words)
    tags_words = list(zip(verb["tags"], words))
    for idx, (tag, word) in enumerate(tags_words):
        if tag.endswith(f"ARG{argument_number}"):
            arg_tokens.append(word)
            indexes.append(idx)

    if len(indexes) > 0:
        start_end_indexes = [indexes[0], indexes[-1]]
        arg_string = detokenize(" ".join(arg_tokens))

        return arg_string, start_end_indexes
    else:
        return "-", []

    return "-"


def get_coreference_dictionary(sentence):
    """
    Takes a sentence a returns a dictionary where word indices are mapped to their
    antecedent token
    :param sentence:
    :return: a coreferent dictionary, e.g. {"13-13": "Schools"}
    """
    prediction = coref_predictor.predict(document=sentence)

    corefs = {}
    print(sentence)
    print(prediction["clusters"])
    for cluster in prediction["clusters"]:
        antecedent_token_start = cluster[0][0]
        antecedent_token_end = cluster[0][1]
        antecedent_token = prediction["document"][antecedent_token_start: antecedent_token_end + 1]
        for coreferent in cluster[1:]:
            coreferent_token_start = coreferent[0]
            coreferent_token_end = coreferent[1]
            coreferent_token = prediction["document"][coreferent_token_start:coreferent_token_end + 1]
            print(coreferent_token, "=>", antecedent_token)
            coreferent_token_location = str(coreferent_token_start) + "-" + str(coreferent_token_end)
            corefs[coreferent_token_location] = detokenize(" ".join(antecedent_token))
    return corefs


def create_visualization_data(all_sentences, output_file):
    """
    Creates a json file with the data used by the D3 visualization.
    :param all_sentences: the output of our SRL + coreference analysis
    :param output_file: the json file where we will dump the results
    :return:
    """

    # Load the topic classifier we will use for assigning the topics
    if CLASSIFIER_FILE:
        archive = load_archive(CLASSIFIER_FILE)
        classifier = Predictor.from_archive(archive, 'topic_classifier')
    else:
        classifier = None

    # Initialize the json object with the prompt as root.
    output = {"name": PROMPT, "children": []}

    # Group the responses by arg0 and main verb.
    grouped_responses = group_by_arg0_and_verb(all_sentences)

    for main_subj in grouped_responses:
        main_subject_branch = {"name": main_subj, "children": []}

        for main_verb in grouped_responses[main_subj]:
            main_verb_branch = {"name": main_verb, "children": []}

            if classifier:
                # Group the responses by topic
                topic_dictionary = defaultdict(list)
                for sentence in grouped_responses[main_subj][main_verb]:
                    result = classifier.predict_json({"text": sentence["response"]})
                    topic = result["label"]
                    topic_dictionary[topic].append(sentence["response"])

                # Create the topic subtree for the verb
                for topic in topic_dictionary:
                    topic_branch = {"name": f"Topic: {topic}", "children": []}

                    for response in topic_dictionary[topic]:
                        topic_branch["children"].append({"name": PROMPT + " " + response, "value": 1})

                    main_verb_branch["children"].append(topic_branch)
            else:
                main_verb_branch["children"] = [{"name": PROMPT + " " + r["response"], "value": 1} for r in
                                                grouped_responses[main_subj][main_verb]]

            # Add all responses for this verb to the tree
            if len(main_verb_branch["children"]) > 0:
                main_subject_branch["children"].append(main_verb_branch)

        # Exclude all responses where there is only one response (e.g. one subject).
        # The goal here is to show the more frequent items to help people parse it.
        if len(main_subject_branch["children"]) > 1:
            output["children"].append(main_subject_branch)

    # Add the number of items to each node and sort the children alphabetically
    total = 0
    for verb in output["children"]:
        verb_total = 0
        for subject in verb["children"]:
            subject_total = 0
            if classifier:
                for topic in subject["children"]:
                    topic["name"] = f"{topic['name']} ({len(topic['children'])})"
                    subject_total += len(topic["children"])
            else:
                subject_total = len(subject["children"])
            subject["name"] = f"{subject['name']} ({subject_total})"
            subject["children"] = sorted(subject["children"], key=lambda x: x["name"])
            verb_total += subject_total
        verb["name"] = f"{verb['name']} ({verb_total})"
        verb["children"] = sorted(verb["children"], key=lambda x: x["name"])
        total += verb_total
    output["name"] = f"{output['name']} ({total})"
    output["children"] = sorted(output["children"], key=lambda x: x["name"])

    with open(output_file, "w") as o:
        json.dump(output, o, sort_keys=True)


def read_srl_output(srl_output_file):
    """
    Reads the output from the AllenNLP Semantic Role Labelling model.
    :param srl_output_file:
    :return:
    """
    with open(srl_output_file) as i:
        srl_out = json.load(i)

    return srl_out


def write_output(all_sentences, output_file):
    """
    Writes tab-separated output that can be imported in a Google Spreadsheet.
    :param all_sentences:
    :param output_file:
    :return:
    """

    with open(output_file, "w") as o:
        columns = ["response", "verb construction", "main verb", "extracted arg0", "intended arg0", "arg1", "arg2"]
        o.write("\t".join(columns) + "\n")
        for sentence in all_sentences:
            output_list = [sentence["response"], " ".join(sentence["meta"][1:])]  # strip the first "meta" label: main clause
            for verb in sentence["verbs"][NUMBER_OF_VERBS_IN_PROMPT:]:
                for item in verb:
                    output_list.append(item)

            o.write("\t".join(output_list) + "\n")


def main():

    # Read AllenNLP's SRL output.
    srl_out = read_srl_output(SRL_OUTPUT_FILE)

    sentences = []
    for sent in srl_out:
        sentence_info = {"sentence": sent["sentence"],
                         "response": sent["response"],
                         "meta": [],
                         "verbs": []}

        # Perform coreference resolution on the full sentence
        corefs = get_coreference_dictionary(sent["sentence"])

        # For each of the verbs in the sentence, preprocess the verb and identify its arguments.
        auxiliary = None
        for verb in sent["srl"]["verbs"]:

            # Preprocess the verb using a few simple rules, e.g. ca => can, etc.
            verb_string = verb["verb"].lower()
            verb_string = VERB_MAP.get(verb_string, verb_string)

            # If the verb is a modal, add this information to the metadata and
            # add the verb as an auxiliary to the next main verb.
            if verb_string in MODAL_VERBS:
                sentence_info["meta"].append("modal")
                auxiliary = verb_string

            # If the verb is an auxiliary, add this information to the metadata and
            # add the verb as an auxiliary to the next main verb.
            elif verb_string in AUX_VERBS:
                sentence_info["meta"].append("auxiliary")
                auxiliary = verb_string

            else:
                # Identify the arguments and their indices
                arg0_string, arg0_indices = identify_argument(verb, 0, sent["srl"]["words"])
                arg1_string, arg1_indices = identify_argument(verb, 1, sent["srl"]["words"])
                arg2_string, arg2_indices = identify_argument(verb, 2, sent["srl"]["words"])

                # If arg0 is in the coreference dictionary, identify its antecedent (the "implied subject").
                # If not, take the arg0 itself as "implied subject".
                arg0_location = "-".join([str(x) for x in arg0_indices])
                if arg0_location in corefs:
                    arg0_antecedent = corefs[arg0_location]
                else:
                    arg0_antecedent = arg0_string
                print(corefs)
                print("SA", arg0_string, arg0_antecedent)
                print(arg0_location)

                # Add the auxiliary to the verb string.
                if auxiliary is not None:
                    verb_string += f" ({auxiliary})"
                    auxiliary = None

                # Add the verb information to the sentence information.
                # Exclude constructions like "I think", "I guess", etc. on the basis of a
                # list of subjects we want to ignore.
                if arg0_string not in SUBJECTS_TO_IGNORE:
                    sentence_info["verbs"].append([verb_string, arg0_string, arg0_antecedent, arg1_string, arg2_string])

        sentences.append(sentence_info)

    create_visualization_data(sentences, OUTPUT_VISUALIZATION_FILE)
    write_output(sentences, OUTPUT_TSV_FILE)


if __name__ == "__main__":
    main()

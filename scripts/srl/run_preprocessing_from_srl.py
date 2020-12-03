import csv
import json

import click
from scipy import spatial
from sklearn.cluster import KMeans
from tqdm import tqdm

from quillgrammar.grammar.error import Error
from quillnlp.preprocessing.checks import SoResponseStartsWithThatCheck, SentenceEndsInQuestionMarkCheck, \
    MultipleSentencesCheck, ProfanityCheck, perform_check
from quillnlp.preprocessing.coref import get_coreference_dictionary
from quillnlp.preprocessing.srl import *
from quillgrammar.grammar.checks.rules import ResponseStartsWithVerbCheck

import torch

from transformers.tokenization_bert import BertTokenizer
from transformers.modeling_bert import BertModel

from quillopinion.opinioncheck import OpinionCheck


def get_sentence_embedding(model, tokenizer, sentence):
    input_ids = torch.tensor(tokenizer.encode(sentence)).unsqueeze(0)  # Batch size 1
    with torch.no_grad():
        outputs = model(input_ids)
        last_hidden_states = outputs[0]  # The last hidden-state is the first element of the output tuple
        sentence_embedding = last_hidden_states[0, 0, :].cpu().numpy()

    return sentence_embedding


VERB_MAP = {"s": "be",
            "is": "be",
            "'s": "be",
            "are": "be",
            "ca": "can",
            "wo": "will",
            "has": "have"}

SUBJECTS_TO_IGNORE = set(["I", "some", "some people"])

MODAL_VERBS = set(["will", "shall", "may", "might", "can", "could", "must", "ought",
                   "should", "would", "used to", "need"])

AUX_VERBS = set(["be", "do", "does"])


def create_visualization_data(prompt, all_sentences, num_verbs_prompt, output_file):
    """
    Creates a json file with the data used by the D3 visualization.
    :param all_sentences: the output of our SRL + coreference analysis
    :param output_file: the json file where we will dump the results
    :return:
    """

    # Load the topic classifier we will use for assigning the topics

    # Initialize the json object with the prompt as root.
    output = {"name": prompt, "children": []}

    # Group the responses by arg0 and main verb.
    grouped_responses = group_by_arg0_and_verb(all_sentences, num_verbs_prompt)

    for main_subj in grouped_responses:
        main_subject_branch = {"name": main_subj, "children": []}

        for main_verb in grouped_responses[main_subj]:
            main_verb_branch = {"name": main_verb, "children": []}

            main_verb_branch["children"] = [{"name": prompt + " " + r["response"], "value": 1} for r in
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


def write_output(all_sentences, num_verbs_prompt, output_file):
    """
    Writes tab-separated output that can be imported in a Google Spreadsheet.
    :param all_sentences:
    :param output_file:
    :return:
    """

    with open(output_file, "w") as csvfile:
        columns = ["response", "opinion", "starts with verb",
                   "so response starts with that", "ends in question mark",
                   "profanity", "multiple sentences",
                   "cluster", "similarity", "modal", "auxiliary",
                   "main verb", "extracted arg0", "intended arg0", "arg1", "arg2"]
        csvwriter = csv.writer(csvfile, delimiter="\t")
        csvwriter.writerow(columns)
        for sentence in all_sentences:
            output_list = [sentence["response"], sentence["opinion"],
                           sentence["starts with verb"],
                           sentence["so response starts with that"],
                           sentence["ends in question mark"],
                           sentence["profanity"],
                           sentence["multiple sentences"],
                           sentence["cluster"],
                           sentence["similarity"], sentence["modal"],
                           sentence["auxiliary"]]
            for verb in sentence["verbs"]:
                for item in verb:
                    output_list.append(item)

            csvwriter.writerow(output_list)




@click.command()
@click.argument('srl_file')
def preprocess(srl_file):

    # 1. Read the SRL output from the SRL file.
    with open(srl_file) as i:
        srl_out = json.load(i)

    # 2. Get the prompt from the SRL output and determine the number of verbs in the prompt.
    prompt = get_prompt_from_srl_output(srl_out[0])
    num_verbs_prompt = get_number_of_verbs_in_prompt(prompt, srl_out[0])

    sentences = []

    # Initialize BERT
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased')
    model.eval()

    # Get BERT embeddings
    embeddings = [get_sentence_embedding(model, tokenizer, s["response"]) for s in tqdm(srl_out)]

    # Cluster embeddings
    NUM_CLUSTERS = 10
    clusterer = KMeans(n_clusters=NUM_CLUSTERS)
    clusters = clusterer.fit_predict(embeddings)

    # Get similarities to cluster centers
    similarities = []
    for item_idx, cluster in enumerate(clusters):
        cluster_center = clusterer.cluster_centers_[cluster]
        embedding = embeddings[item_idx]
        similarity = 1 - spatial.distance.cosine(embedding, cluster_center)
        similarities.append(similarity)

    # Additional check
    opinion_check = OpinionCheck()
    verb_check = ResponseStartsWithVerbCheck()
    so_response_starts_with_that_check = SoResponseStartsWithThatCheck()
    ends_in_question_mark_check = SentenceEndsInQuestionMarkCheck()
    multiple_sentences_check = MultipleSentencesCheck()
    profanity_check = ProfanityCheck()

    # 3. For every sentence:
    for (sent, cluster, similarity) in zip(srl_out, clusters, similarities):

        sentence_info = {"sentence": sent["sentence"],
                         "response": sent["response"],
                         "opinion": perform_check(opinion_check, sent["sentence"], prompt, ""),
                         "starts with verb": perform_check(verb_check, sent["sentence"], prompt, ""),
                         "so response starts with that": perform_check(so_response_starts_with_that_check,
                                                                       sent["sentence"], prompt, ""),
                         "ends in question mark": perform_check(ends_in_question_mark_check,
                                                                sent["sentence"], prompt, ""),
                         "profanity": perform_check(profanity_check, sent["sentence"], prompt, ""),
                         "multiple sentences": perform_check(multiple_sentences_check, sent["sentence"], prompt, ""),
                         "cluster": cluster,
                         "similarity": similarity,
                         "modal": "-",
                         "auxiliary": "-",
                         "verbs": []}

        # 3.1 Perform coreference resolution on the full sentence
        corefs = get_coreference_dictionary(sent["sentence"])

        # 3.2 For each of the verbs in the sentence, preprocess the verb and identify its arguments.
        auxiliary = None
        for verb_idx, verb in enumerate(sent["srl"]["verbs"]):

            # Skip verbs in the prompt
            if verb_idx < num_verbs_prompt:
                continue

            # Only look at the first main verb (be is also considered a main verb)
            elif verb_idx > num_verbs_prompt + 1:
                continue

            # 3.2.1 Preprocess the verb using a few simple rules, e.g. ca => can, etc.
            verb_string = verb["verb"].lower()
            verb_string = VERB_MAP.get(verb_string, verb_string)

            # 3.2.2 If the verb is a modal, add this information to the metadata and
            # add the verb as an auxiliary to the next main verb.
            # if not verb_idx < num_verbs_prompt and verb_string in MODAL_VERBS:
            #    sentence_info["modal"] = "yes"
            #    auxiliary = verb_string

            # Modal verbs can also be identified as ARGM-MOD
            modal = None
            if "ARGM-MOD" in verb["description"]:
                auxiliary_candidates = re.findall(r"ARGM-MOD: (\w+)", verb["description"])
                if auxiliary_candidates:
                    sentence_info["modal"] = "yes"
                    verb_string = f"{verb_string} ({auxiliary_candidates[0]})"
                    modal = auxiliary_candidates[0]

            # 3.2.4 If the verb is not a modal or auxiliary, identify the arguments in the sentence
            arg0_string, arg0_indices = identify_argument(verb, 0, sent["srl"]["words"])
            arg1_string, arg1_indices = identify_argument(verb, 1, sent["srl"]["words"])
            arg2_string, arg2_indices = identify_argument(verb, 2, sent["srl"]["words"])

            # If arg0 is in the coreference dictionary, identify its antecedent (the "implied subject").
            # If not, take the arg0 itself as "implied subject".
            arg0_location = "-".join([str(x) for x in arg0_indices])
            if arg0_location in corefs:
                arg0_antecedent = corefs[arg0_location]
            elif arg0_string != "-":
                arg0_antecedent = arg0_string
            else:  # These are cases where the subject is "-", as in copula verbs
                arg0_antecedent = arg1_string
                arg0_string = arg1_string
                arg1_string = "-"

            # Add the verb information to the sentence information.
            # Exclude constructions like "I think", "I guess", etc. on the basis of a
            # list of subjects we want to ignore.

            if len(sentence_info["verbs"]) > 0 and \
                    sentence_info["verbs"][-1][0] in AUX_VERBS and \
                    sentence_info["verbs"][-1][1] == "-":
                verb_string = f"{verb_string} ({sentence_info['verbs'][-1][0]})"
                sentence_info["auxiliary"] = "yes"
                sentence_info["verbs"][-1] = [verb_string, arg0_string, arg0_antecedent, arg1_string, arg2_string]

            # If the modal of the current verb is the previous verb,
            # remove the previous verb.
            elif len(sentence_info["verbs"]) > 0 and \
                    modal is not None and \
                    sentence_info["verbs"][-1][0] == modal:

                sentence_info["modal"] = "yes"
                sentence_info["verbs"][-1] = [verb_string, arg0_string, arg0_antecedent, arg1_string, arg2_string]

            elif arg0_string not in SUBJECTS_TO_IGNORE:
                sentence_info["verbs"].append([verb_string, arg0_string, arg0_antecedent, arg1_string, arg2_string])

            if "could be saved" in sent["sentence"]:
                print(sent["sentence"])
                print(sent["srl"])
                print(sentence_info["verbs"])
                print(verb)
                print(verb_idx, num_verbs_prompt)
                input()

        sentences.append(sentence_info)

    output_visualization_file = srl_file.replace(".json", "_viz.json")
    create_visualization_data(prompt, sentences, num_verbs_prompt, output_visualization_file)

    print(sentences)
    output_tsv_file = srl_file.replace(".json", ".tsv")
    write_output(sentences, num_verbs_prompt, output_tsv_file)


if __name__ == "__main__":
    preprocess()

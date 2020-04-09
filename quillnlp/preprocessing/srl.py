import re
import torch
import pandas as pd

from typing import Dict, List, Tuple
from tqdm import tqdm

from scipy import spatial
from sklearn.cluster import KMeans
from allennlp.predictors.predictor import Predictor
from transformers.tokenization_bert import BertTokenizer
from transformers.modeling_bert import BertModel

from quillnlp.utils import detokenize, tokenize
from quillnlp.preprocessing.coref import get_coreference_dictionary


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

AUX_VERBS = set(["do", "does"])


def perform_srl(responses, prompt=None):
    """ Perform semantic role labeling on a list of responses, given a prompt.

    Args:
        responses: a list of responses (or full sentences if prompt = None)
        prompt: the prompt that should be added as a prefix to the responses

    Returns: the output of the AllenNLP SRL model

    """

    predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/srl-model-2018.05.25.tar.gz")
    #predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/openie-model.2020.03.26.tar.gz")
    #predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/bert-base-srl-2020.02.10.tar.gz")
    if prompt:
        sentences = [{"sentence": prompt + " " + response} for response in responses]
    else:
        sentences = [{"sentence": response} for response in responses]
    output = predictor.predict_batch_json(sentences)

    full_output = [{"sentence": prompt + " " + response if prompt else response,
                    "response": response,
                    "srl": srl} for (response, srl) in zip(responses, output)]

    return full_output


def group_by_arg0_and_verb(sentences: List[Dict], number_of_verbs_in_prompt: int) -> Dict:
    """
    Groups the sentences by their main Verb and its arg0. This is needed to produce
    the clustered data for the D3 visualization.

    Args:
        sentences: a list of sentence outputs from AllenNLP's SRL model
        number_of_verbs_in_prompt: the number of verbs in the prompt (these verbs will
            not be considered in the grouping process)

    Returns: a dictionary of the form {arg0: {main_verb: [sentence1, sentence2, ...]}

    """

    groups = {"-": {"-": []}}
    for sentence in sentences:
        if len(sentence["verbs"]) > number_of_verbs_in_prompt:
            # verbs are strings like "allow (should)"
            main_verb = sentence["verbs"][number_of_verbs_in_prompt][0].split("(")[0].strip()
            main_verb_arg0 = sentence["verbs"][number_of_verbs_in_prompt][2].lower()
            if main_verb_arg0 not in groups:
                groups[main_verb_arg0] = {}
            if main_verb not in groups[main_verb_arg0]:
                groups[main_verb_arg0][main_verb] = []
            groups[main_verb_arg0][main_verb].append(sentence)
        else:
            groups["-"]["-"].append(sentence)

    return groups


def identify_argument(verb: Dict, argument_number: int, words: List[str]) -> Tuple[str, List[int]]:
    """
    Identify an argument of a verb on the basis of its number. Returns its string and
    start+end indexes. This allows easier integration of the semantic role labelling
    and coreference results.

    Args:
        verb: the output of AllenNLP's SRL model for this verb
        argument_number: the number of the argument we want to identify
        words: the list of tokens in this sentence

    Returns: a tuple consisting of the argument string and a list of its indexes

    """
    indexes = []
    arg_tokens = []

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

    return "-", []


def get_prompt_from_srl_output(srl_output: Dict) -> str:
    """
    Get the prompt from the SRL output of our perform_srl script.

    Args:
        srl_output: the SRL output of our perform SRL script for a single sentence

    Returns: the prompt of the sentence

    """
    full_sentence = srl_output["sentence"]
    response = srl_output["response"]

    prompt = re.sub(response, "", full_sentence).strip()
    return prompt


def get_number_of_verbs_in_prompt(prompt, srl_output: Dict) -> int:
    """
    Finds the number of verbs in a prompt, given the output of the AllenNLP
    SRL model. This relies on the spaCy tokenizer, which is also used by
    AllenNLP. When there are differences in tokenization, this function may
    give incorrect results

    Args:
        srl_output: the json output of the AllenNLP SRL model

    Returns: the number of verbs in a prompt
    """
    num_verbs = 0
    prompt_tokens = tokenize(prompt)
    for verb in srl_output["srl"]["verbs"]:
        verb_location = verb["tags"].index("B-V")
        if verb_location < len(prompt_tokens):
            num_verbs += 1

    return num_verbs


def get_sentence_embedding(model, tokenizer, sentence):
    input_ids = torch.tensor(tokenizer.encode(sentence)).unsqueeze(0)  # Batch size 1
    with torch.no_grad():
        outputs = model(input_ids)
        last_hidden_states = outputs[0]  # The last hidden-state is the first element of the output tuple
        sentence_embedding = last_hidden_states[0, 0, :].cpu().numpy()

    return sentence_embedding


def process_srl_results(srl_results, num_clusters=10):

    # Initialize the results
    columns = ["response", "cluster", "similarity", "modal", "auxiliary",
               "main verb", "extracted arg0", "intended arg0", "arg1", "arg2"]
    results = [columns]

    # Get the prompt from the SRL output and determine the number of verbs in the prompt.
    prompt = get_prompt_from_srl_output(srl_results[0])
    num_verbs_prompt = get_number_of_verbs_in_prompt(prompt, srl_results[0])

    # Initialize BERT
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased')
    model.eval()

    # Get BERT embeddings
    embeddings = [get_sentence_embedding(model, tokenizer, s["response"]) for s in tqdm(srl_results)]

    # Cluster embeddings
    clusterer = KMeans(n_clusters=num_clusters)
    clusters = clusterer.fit_predict(embeddings)

    # Get similarities to cluster centers
    similarities = []
    for item_idx, cluster in enumerate(clusters):
        cluster_center = clusterer.cluster_centers_[cluster]
        embedding = embeddings[item_idx]
        similarity = 1 - spatial.distance.cosine(embedding, cluster_center)
        similarities.append(similarity)

    # For every sentence:
    for (sent, cluster, similarity) in zip(srl_results, clusters, similarities):
        sentence_info = {"sentence": sent["sentence"],
                         "response": sent["response"],
                         "cluster": cluster,
                         "similarity": similarity,
                         "modal": "-",
                         "auxiliary": "-",
                         "verbs": []}

        # 1 Perform coreference resolution on the full sentence
        corefs = get_coreference_dictionary(sent["sentence"])

        # 2 For each of the verbs in the sentence, preprocess the verb and identify its arguments.
        auxiliary = None
        for verb_idx, verb in enumerate(sent["srl"]["verbs"]):

            # 2.1 Preprocess the verb using a few simple rules, e.g. ca => can, etc.
            verb_string = verb["verb"].lower()
            verb_string = VERB_MAP.get(verb_string, verb_string)

            # 2.2 If the verb is a modal, add this information to the metadata and
            # add the verb as an auxiliary to the next main verb.
            if not verb_idx < num_verbs_prompt and verb_string in MODAL_VERBS:
                sentence_info["modal"] = "yes"
                auxiliary = verb_string

            # 2.3 If the verb is an auxiliary, add this information to the metadata and
            # add the verb as an auxiliary to the next main verb.
            elif not verb_idx < num_verbs_prompt and verb_string in AUX_VERBS:
                sentence_info["auxiliary"] = "yes"
                auxiliary = verb_string

            else:
                # 2.4 If the verb is not a modal or auxiliary, identify the arguments in the sentence
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

                # Add the auxiliary to the verb string.
                if auxiliary is not None:
                    verb_string += f" ({auxiliary})"
                    auxiliary = None

                # Add the verb information to the sentence information.
                # Exclude constructions like "I think", "I guess", etc. on the basis of a
                # list of subjects we want to ignore.
                if arg0_string not in SUBJECTS_TO_IGNORE:
                    sentence_info["verbs"].append([verb_string, arg0_string, arg0_antecedent, arg1_string, arg2_string])

        # Add the relevant information to the results
        output_list = [sentence_info["response"], sentence_info["cluster"],
                       sentence_info["similarity"], sentence_info["modal"],
                       sentence_info["auxiliary"]]
        for verb in sentence_info["verbs"][num_verbs_prompt:]:
            for item in verb:
                output_list.append(item)

        results.append(output_list)

    return results

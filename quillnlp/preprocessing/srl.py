import re
from typing import Dict, List, Tuple

from quillnlp.utils import detokenize, tokenize

from allennlp.predictors.predictor import Predictor


def perform_srl(responses, prompt=None):
    """ Perform semantic role labeling on a list of responses, given a prompt.

    Args:
        responses: a list of responses (or full sentences if prompt = None)
        prompt: the prompt that should be added as a prefix to the responses

    Returns: the output of the AllenNLP SRL model

    """

    predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/srl-model-2018.05.25.tar.gz")

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

import re
import csv
import yaml

from tqdm import tqdm

from quillgrammar.grammar.constants import GrammarError
from quillgrammar.grammar.pipeline import GrammarPipeline
from quillnlp.spelling.bing import correct_sentence_with_bing

csv_file = "quillgrammar/data/new_turk_data.csv"
#csv_file = "../../data/quill/grammer_response_dump_generic_2020_07_06.csv"
config_file = "grammar_config_test.yaml"


def read_csv_file(f):
    data = []
    with open(f) as i:
        reader = csv.reader(i)
        for row in reader:
            sentence, prompt, *other = row

            # Some prompts in the file are not complete. Correct those.
            if not (prompt.strip().endswith("so") or
                    prompt.strip().endswith("because") or
                    prompt.strip().endswith("but")):

                if sentence.startswith(prompt.strip() + " so"):
                    prompt = prompt + " so"
                elif sentence.startswith(prompt.strip() + " but"):
                    prompt = prompt + " but"
                elif sentence.startswith(prompt.strip() + ", so"):
                    prompt = prompt + ", so"
                elif sentence.startswith(prompt.strip() + ", but"):
                    prompt = prompt + ", but"
                elif sentence.startswith(prompt.strip() + " because"):
                    prompt = prompt + " because"

            if sentence.startswith(prompt):
                data.append((sentence, prompt))
            else:
                data.append((sentence, ""))
    return data

def read_txt_file(f):
    
    data = []
    with open(f) as i:
        for line in i:
            sentence = line.strip()
            prompt = re.match(".*?(because|, but|, so)", sentence)
            prompt = prompt.group(0) if prompt else ""
            data.append((sentence, prompt))

    return data


grouping = {
    GrammarError.PASSIVE_WITH_INCORRECT_BE.value: "Passive been error",
    GrammarError.PASSIVE_PERFECT_WITHOUT_HAVE.value: "Passive been error"
}

grammar_path = "/home/yves/projects/grammar-api/quillgrammar/models/current/"

def test_grammar_pipeline():

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(grammar_path, config)

    #data = read_csv_file(csv_file)
    data = read_txt_file(csv_file)

    with open("new_turk_data_output.tsv", "w") as o:
        csv_writer = csv.writer(o, delimiter="\t")

        for (original_sentence, prompt) in tqdm(data, desc="Predicting errors"):

            sentence, bing_response, bing_output = correct_sentence_with_bing(original_sentence)

            bing_correction = sentence != original_sentence

            try:
                errors_before_bing = pipeline.check(original_sentence, prompt)
            except IndexError:
                errors_before_bing = []

            try:
                errors_after_bing = pipeline.check(sentence, prompt)
            except IndexError:
                errors_after_bing = []

            grammar_correction_before_bing = len(errors_before_bing) > 0
            grammar_correction_after_bing = len(errors_after_bing) > 0

            grammar_output_before_bing = ""
            grammar_error_type_before_bing = ""
            if len(errors_before_bing) > 0:
                grammar_output_before_bing = f"{errors_before_bing[0].text} ({errors_before_bing[0].index})"
                grammar_error_type_before_bing = grouping.get(errors_before_bing[0].type,
                                                              errors_before_bing[0].type)

            grammar_output_after_bing = ""
            grammar_error_type_after_bing = ""
            if len(errors_after_bing) > 0:
                grammar_output_after_bing = f"{errors_after_bing[0].text} ({errors_after_bing[0].index})"
                grammar_error_type_after_bing = grouping.get(errors_after_bing[0].type,
                                                             errors_after_bing[0].type)

            csv_writer.writerow([original_sentence, bing_correction,
                                 bing_response, bing_output, sentence, grammar_correction_after_bing,
                                 grammar_error_type_after_bing, grammar_output_after_bing,
                                 original_sentence, grammar_correction_before_bing, grammar_error_type_before_bing,
                                 grammar_output_before_bing
                                 ])


test_grammar_pipeline()

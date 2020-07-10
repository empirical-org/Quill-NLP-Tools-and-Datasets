import csv
import re

from tqdm import tqdm

from quillnlp.grammar.grammarcheck import GrammarError, SpaCyGrammarChecker

CORRECT_LABEL = "Correct"

input_file = "data/raw/Comprehension Responses - Full Set June 2020 - Sheet1.csv"
input_file = "data/raw/grammar_response_dump_connect_2020_06_29.csv"
input_file = "comprehension_sentences_bing.tsv"
output_file = "comprehension_errors_bing.tsv"

print("Initializing GrammarChecker")
checker = SpaCyGrammarChecker(["models/spacy_sva_xl", "models/spacy_grammar",  "models/spacy_3p"])

with open(input_file) as csvfile, open(output_file, "w") as csv_out:
    reader = csv.reader(csvfile)
    writer = csv.writer(csv_out, delimiter="\t")
    for row in tqdm(reader):
        sentence = row[0]

        errors = checker.check(sentence)

        prompts = re.findall("^.*(because|, but|, so)", sentence)
        if len(prompts) > 0:
            prompt = re.findall("^.*(because|, but|, so)", sentence)[0]
            errors_outside_prompt = [e for e in errors if e.index > len(prompt)]
        else:
            errors_outside_prompt = errors

        writer.writerow([sentence, str(errors_outside_prompt)])

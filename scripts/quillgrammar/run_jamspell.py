import time
import difflib
import random
import spacy
import re
import csv
import wordfreq

from tqdm import tqdm

#import jamspell
import jamspellpro

nlp = spacy.load("en_core_web_sm")

#input_file = "quillgrammar/data/new_turk_data.txt"
#input_file = "test.txt"
input_file = './validated_spelling_corpus.txt'

#corrector = jamspell.TSpellCorrector()
#corrector.LoadLangModel('quillgrammar/models/spelling/en.bin')

#corrector = jamspellpro.TSpellCorrector()
#corrector.LoadLangModel('quillgrammar/models/spelling/model_en_big')

corrector = jamspellpro.TSpellCorrector()
corrector.LoadLangModel('quillgrammar/models/spelling/model_en_med')

passages = {
    "Alison Bechdel’s memoir has been challenged in certain communities": "tests/data/passages/bechdel.txt",
    "Eastern Michigan University cut women's tennis and softball": "tests/data/passages/titleix.txt",
    "Methane from cow burps harms the environment": "tests/data/passages/eatingmeat.txt",
    "Plastic bag reduction laws are beneficial": "tests/data/passages/plasticbags.txt",
    "Schools should not allow junk food to be sold on campus": "tests/data/passages/junkfood.txt",
    "A surge barrier in New York City could harm the local ecosystem": "tests/data/passages/surgebarriers.txt"
}

def get_passage_tokens():

    passage_tokens = {}
    for passage in passages:
        with open(passages[passage]) as i:
            lines = i.readlines()
        text = " ".join([l.strip() for l in lines])
        doc = nlp(text)
        passage_tokens[passage] = set([t.text.lower() for t in doc]) | \
                                  set(["but", "so", "because"]) | \
                                  set(wordfreq.top_n_list("en", 10000))

    return passage_tokens

passage_tokens = get_passage_tokens()

random.seed(1)

with open(input_file) as i:
    lines = i.readlines()

#random.shuffle(lines)

corrected = 0
total = 0
different = 0

def tokenize(sentence):
    doc = nlp(sentence)
    tokens = []
    for token in doc:
        if token.i > 1 and re.match("[a-zA-Z]", token.text) and not doc[token.i-1].whitespace_:
            tokens[-1] = tokens[-1] + token.text_with_ws
        else:
            tokens.append(token.text_with_ws)

    return tokens




start = time.time()
with open("validated_spelling_corpus_jamspell_med.csv", "w") as o:

    writer = csv.writer(o, delimiter='\t')

    for line in tqdm(lines):
        total += 1

        whitelist = []
        for passage in passage_tokens:
            if line.startswith(passage):
                whitelist = passage_tokens[passage]

        #assert whitelist is not None

        input_sentence = line.strip()
        output_sentence = corrector.FixFragment(input_sentence)

        input_tokens = tokenize(input_sentence)
        output_tokens = tokenize(output_sentence)

        #output_sentence_big = corrector_pro_big.FixFragment(input_sentence)
        #output_sentence_med = corrector_pro_medium.FixFragment(input_sentence)

        """
        if input_sentence != output_sentence_big:
            different += 1
            print("Input:")
            print(input_sentence)
            print("Medium:")
            print(output_sentence_big)
            print("")
            diff = difflib.SequenceMatcher(None, input_sentence, output_sentence_big)
            for tag, i1, i2, j1, j2 in diff.get_opcodes():
                print('{:7}   a[{}:{}] --> b[{}:{}] {!r:>8} --> {!r}'.format(tag, i1, i2, j1, j2, input_sentence[i1:i2], output_sentence_big[j1:j2]))
            input()
        """

        def add_correction(input_token, output_token, sentence, corrections):
            if input_token.strip().lower() not in whitelist:
                sentence += output_token
                corrections.extend([input_token.strip(), output_token.strip()])
            else:
                sentence += input_token
            return sentence, corrections


        whitelisted = False
        corrections = []


        if input_sentence != output_sentence:

            corrected_sentence = ""

            to_correct = True
            #print(list(difflib.ndiff(input_tokens, output_tokens)))
            input_token, output_token = "", ""
            for token in difflib.ndiff(input_tokens, output_tokens):
                if token.startswith(" "):
                    if input_token:
                        corrected_sentence, corrections = add_correction(input_token, output_token, corrected_sentence, corrections)
                    corrected_sentence += token[2:]
                    input_token, output_token = "", ""
                elif token.startswith("-"):
                    input_token += token[2:]
                elif token.startswith("+"):
                    output_token += token[2:]

            if input_token:
                corrected_sentence, corrections = add_correction(input_token, output_token, corrected_sentence, corrections)

            if input_sentence != corrected_sentence:
                corrected += 1

                #print(input_sentence)
                #print(corrected_sentence)
                #print(corrections)

            writer.writerow([corrected_sentence] + corrections)
        else:
            writer.writerow([output_sentence] + corrections)



end = time.time()
total_time = end-start

print(f"{corrected}/{total}={corrected/total*100}% sentences corrected")
print(f"{different}/{total}={different/total*100}% sentences different")
print(f"{total}/{total_time}={total/total_time} sentences/second")

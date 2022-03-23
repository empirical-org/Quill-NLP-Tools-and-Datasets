import re
import jamspell
import difflib
import csv
import en_core_web_sm
import wordfreq

from tqdm import tqdm

from quillnlp.spelling.bing import correct_sentence_with_bing


f = "test.bea.noise.m2"

corrector = jamspell.TSpellCorrector()
corrector.LoadLangModel('quillgrammar/models/spelling/en.bin')

#corrector = jamspellpro.TSpellCorrector()
#corrector.LoadLangModel('quillgrammar/models/spelling/model_en_small')


nlp = en_core_web_sm.load()

whitelist = set(wordfreq.top_n_list("en", 1000))


def tokenize(sentence):
    doc = nlp(sentence)
    tokens = []
    for token in doc:
        if token.i > 1 and re.match("[a-zA-Z]", token.text) and not doc[token.i-1].whitespace_:
            tokens[-1] = tokens[-1] + token.text_with_ws
        else:
            tokens.append(token.text_with_ws)

    return tokens


def detokenize(s):
    s = re.sub(" ([.,?:\)!;])", "\\1", s)
    s = re.sub(" '(s|d|ll|m|re)", "'\\1", s)
    s = s.replace("( ", "(")
    s = s.replace(" n't", "n't")
    s = s.replace(" - ", "-")
    return s


def add_correction(input_token, output_token, sentence, corrections):
    if input_token.strip().lower() not in whitelist:
        sentence += output_token
        corrections.append(f"{input_token.strip()} -> {output_token.strip()}")
    else:
        sentence += input_token
    return sentence, corrections


def correct_with_jamspell(input_sentence, whitelist=None):
    output_sentence = corrector.FixFragment(input_sentence)

    if whitelist is not None:
        input_tokens = tokenize(input_sentence)
        output_tokens = tokenize(output_sentence)

        corrections = []
        corrected_sentence = ""

        to_correct = True
        input_token, output_token = "", ""
        for token in difflib.ndiff(input_tokens, output_tokens):
            if token.startswith(" "):
                if input_token:
                    corrected_sentence, corrections = add_correction(input_token, output_token, corrected_sentence,
                                                                     corrections)
                corrected_sentence += token[2:]
                input_token, output_token = "", ""
            elif token.startswith("-"):
                input_token += token[2:]
            elif token.startswith("+"):
                output_token += token[2:]

        if input_token:
            corrected_sentence, corrections = add_correction(input_token, output_token, corrected_sentence, corrections)

        output_sentence = corrected_sentence

    return output_sentence, corrections



with open(f) as i:
    full_input = "".join([line for line in i])

instances = []
for sentence in full_input.split("\n\n"):
    sentence = sentence.split("\n")
    if len(sentence) > 1:
        text = sentence[0]
        corrections = sentence[1:]
        instance = []

        if text.startswith("S "):
            text = text.strip()
            text = text[2:]
            instance.append(text)

        for correction in corrections:
            if correction.startswith("A "):
                correction = correction[2:]
                correction = correction.split("|||")
                corrected_word = correction[2]
                error_start = int(correction[0].split()[0])
                error_end = int(correction[0].split()[1])
                input_word = " ".join(text.split()[error_start:error_end])
                instance.append((error_start, error_end, input_word, corrected_word))

        instances.append(instance)


outputfile = "bea_spellcheck.csv"

correct = 0
total = 0
with open(outputfile, "w") as o:
    writer = csv.writer(o, delimiter="\t")

    for instance in tqdm(instances):
        sentence = instance[0]
        gold_sentence = sentence.split()
        corrections = instance[1:]

        corrections.reverse()
        for correction in corrections:
            gold_sentence = gold_sentence[:correction[0]] + \
                            [correction[3]] + \
                            gold_sentence[correction[1]:]

        detokenized_sentence = detokenize(sentence)
        detokenized_gold_sentence = detokenize(" ".join(gold_sentence))

        corrected_sentence, corrections = correct_with_jamspell(detokenized_sentence, [])
        #corrected_sentence, response, output = correct_sentence_with_bing(detokenized_sentence)
        #print(instance)
        #print(sentence)
        #print(corrected_sentence)

        if corrected_sentence.strip() == detokenized_gold_sentence.strip():
            #print("CORRECT")
            correct += 1
        #else:
            #print(instance)
            #print(corrected_sentence)
            #print(detokenized_gold_sentence)
            #print(list(difflib.ndiff(corrected_sentence.split(),
            #                         detokenized_gold_sentence.split())))

        total += 1
        writer.writerow([detokenized_sentence,
                         detokenized_gold_sentence,
                         "; ".join(corrections),
                         corrected_sentence])
#                         str(response),
#                         str(output)])

print(correct)
print(total)
print(correct/total)

import re
import csv

f = "test.bea.noise.m2"
output_file = "bea_spellcheck_bing.csv"

def detokenize(s):
    s = re.sub(" ([.,?:\)!;])", "\\1", s)
    s = re.sub(" '(s|d|ll|m|re)", "'\\1", s)
    s = s.replace("( ", "(")
    s = s.replace(" n't", "n't")
    s = s.replace(" - ", "-")
    return s


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

print("All sentences:", len(instances))
selected_instances = [x for x in instances if len(x) == 2]
print("Sentences with one error:", len([x for x in instances if len(x) == 2]))


with open(output_file) as i:
    reader = csv.reader(i, delimiter="\t")
    spellcheck_output = [line for line in reader]


total = 0
correct = 0

for spell_input, spell_output in zip(instances, spellcheck_output):
    spell_sentence_input = detokenize(spell_input[0])
    spell_sentence_output = spell_output[0]
    assert spell_sentence_input == spell_sentence_output

    gold_sentence = spell_input[0].split()
    corrections = spell_input[1:]

    if len(corrections) == 1:

        corrections.reverse()
        for correction in corrections:
            gold_sentence = gold_sentence[:correction[0]] + \
                            [correction[3]] + \
                            gold_sentence[correction[1]:]

        detokenized_gold_sentence = detokenize(" ".join(gold_sentence))

        total += 1
        if detokenized_gold_sentence.strip() == spell_output[2].strip():
            correct += 1


print("Accuracy:", correct, "/", total, correct/total)
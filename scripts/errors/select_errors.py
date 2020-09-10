import ndjson
import random

from tqdm import tqdm

from quillnlp.grammar.constants import GrammarError


def select_its_vs_its(lines):
    data = []
    correct = 0

    for line in tqdm(lines):
        sentence = line["orig_sentence"]
        if " its " in sentence or "Its" in sentence or "It's" in sentence or " it's" in sentence:
            if "entities" in line and len(line["entities"]) == 1:
                line["entities"] = [e for e in line["entities"] if e[2] == "ITS"]
                if len(line["entities"]) > 0:
                    for entity in line["entities"]:
                        start = entity[0]
                        end = entity[1]
                        span = line["synth_sentence"][start:end]

                        entity[2] = GrammarError.ITS_IT_S.value
                    data.append([line["synth_sentence"], {"entities": line["entities"], "original": line["orig_sentence"]}])
            elif correct < 60000:
                line["entities"] = []
                correct += 1
                data.append([line["orig_sentence"], {"entities": line["entities"]}])
    return data


def select_plural_vs_possessive(lines):
    data = []

    for line in tqdm(lines):
        if "entities" in line:
            line["entities"] = [e for e in line["entities"] if e[2] == "POSSESSIVE"]
            if len(line["entities"]) > 0:
                for entity in line["entities"]:
                    entity[2] = GrammarError.PLURAL_POSSESSIVE.value

                if "-'s" not in line["synth_sentence"]:
                    line["synth_sentence"] = line["synth_sentence"].replace("'S", "'s")
                    data.append([line["synth_sentence"], {"entities": line["entities"], "original": line["orig_sentence"]}])
    return data[:100000]


f = "notw_its.ndjson"
#f = "notw_plural.ndjson"

with open(f) as i:
    lines = ndjson.load(i)
random.shuffle(lines)

#data = select_plural_vs_possessive(lines)
data = select_its_vs_its(lines)

with open("Its_vs_it_s.ndjson", "w") as o:
    ndjson.dump(data, o)


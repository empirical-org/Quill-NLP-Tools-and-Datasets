import random
from pathlib import Path
import spacy
import json
import ndjson
from functools import partial
from quillnlp.grammar import corpus
from tqdm import tqdm

from spacy.util import minibatch, compounding
from spacy.gold import biluo_tags_from_offsets
from sklearn.metrics import f1_score, classification_report


# TODO: Woman/Women also capitalized


nlp = spacy.load("en")


def get_data_from_file(f, num):
    with open(f) as i:
        lines = list(set([line.strip() for line in i if len(line.strip()) > 10]))

    random.shuffle(lines)
    return lines[:num]


TEST_SIZE = 5000
DEV_SIZE = 5000
ERROR_RATIO = 0.5

files = ["subtitles.json", "wikipedia_100000.json"]

VERB_AGREEMENT_ERROR_TYPE = "VERB"
WOMAN_WOMEN_ERROR_TYPE = "WOMAN"
THEN_THAN_ERROR_TYPE = "THEN"
CHILD_CHILDREN_ERROR_TYPE = "CHILD"
IT_S_ITS_ERROR_TYPE = "ITS"
PLURAL_POSSESSIVE_ERROR_TYPE = "POSSESSIVE"
ADV_ERROR_TYPE = "ADV"

replacement_functions = {"POS": partial(corpus.replace_possessive_by_plural, PLURAL_POSSESSIVE_ERROR_TYPE),
                         "NNS": partial(corpus.replace_plural_by_possessive, PLURAL_POSSESSIVE_ERROR_TYPE),
                         "VBZ": partial(corpus.replace_verb_form, "VBZ", "VB", VERB_AGREEMENT_ERROR_TYPE),
                         "VBP": partial(corpus.replace_verb_form, "VBP", "VBZ", VERB_AGREEMENT_ERROR_TYPE),
                         "VB": partial(corpus.replace_verb_form, "VB", "VBZ", VERB_AGREEMENT_ERROR_TYPE),
                         "AUX": partial(corpus.replace_verb_form, "VB", "VBZ", VERB_AGREEMENT_ERROR_TYPE),
                         "MD": partial(corpus.replace_verb_form, "VB", "VBZ", VERB_AGREEMENT_ERROR_TYPE),
                         "do": partial(corpus.replace_verb_form, "VB", "VBZ", VERB_AGREEMENT_ERROR_TYPE),
                         "ADV": partial(corpus.replace_adverb_by_adjective, ADV_ERROR_TYPE),
                         "woman": partial(corpus.replace_word, "woman", "women", WOMAN_WOMEN_ERROR_TYPE),
                         "women": partial(corpus.replace_word, "women", "woman", WOMAN_WOMEN_ERROR_TYPE),
                         "then": partial(corpus.replace_word, "then", "than", THEN_THAN_ERROR_TYPE),
                         "than": partial(corpus.replace_word, "than", "then", THEN_THAN_ERROR_TYPE),
                         "child": partial(corpus.replace_word, "child", "children", CHILD_CHILDREN_ERROR_TYPE),
                         "children": partial(corpus.replace_word, "children", "child", CHILD_CHILDREN_ERROR_TYPE),
                         "its": partial(corpus.replace_word, "its", "it's", IT_S_ITS_ERROR_TYPE),
                         "it's": partial(corpus.replace_bigram, ["it", "'s"], "its", IT_S_ITS_ERROR_TYPE)
                         }


train_data = []
for f in files:
    with open(f) as i:
        sentences = json.load(i)

    for error_type in sentences:
        for sentence in tqdm(sentences[error_type][:50000], desc=error_type):
            if random.random() < ERROR_RATIO:
                doc = nlp(sentence)
                sentence_with_error, entities = replacement_functions[error_type](doc)
                train_data.append((error_type, sentence, sentence_with_error, {"entities": entities}))
            else:
                train_data.append((error_type, sentence, sentence, {"entities": []}))


filtered_train_data = []
seen_sentences = set()
for (error_type, sentence, sentence_with_error, entities) in train_data:
    if sentence_with_error not in seen_sentences:
        filtered_train_data.append((error_type, sentence, sentence_with_error, entities))
        seen_sentences.add(sentence_with_error)

train_data = filtered_train_data

random.shuffle(train_data)
TEST_DATA = train_data[-TEST_SIZE:]
DEV_DATA = train_data[-(TEST_SIZE + DEV_SIZE):-TEST_SIZE]
TRAIN_DATA = train_data[:len(train_data) - TEST_SIZE - DEV_SIZE]

train_set = set([x[0] for x in train_data])
test_set = set([x[0] for x in TEST_DATA])
intersection = train_set & test_set
if len(intersection) > 0:
    print("Test sentences in training set:", len(intersection))

for x in intersection:
    print(x, len(x))

print("Train:", len(train_data))
print("Dev:", len(DEV_DATA))
print("Test:", len(TEST_DATA))

test_sentences = []
for error_type, original_sentence, new_sentence, entities in TEST_DATA:
    test_sentences.append({"error_type": error_type,
                           "original": original_sentence,
                           "new": new_sentence,
                           "errors": entities["entities"]})

with open("test_grammar_validated.ndjson", "w") as o:
    ndjson.dump(test_sentences, o)


for _, _, sentence, entities in train_data:
    doc = nlp(sentence)
    tags = biluo_tags_from_offsets(doc, entities["entities"])
    if "" in tags:
        print(sentence)
        print(entities)
        print([t for t in doc])
        print(tags)


def evaluate(data, model, verbose=False):

    predicted_tags = []
    correct_tags = []
    labels = set()
    with open("grammar_results_spacy.txt", "w") as o:
        for (_, _, sentence, entities) in data:
            doc = model(sentence)

            sentence_pred = []
            for t in doc:
                predicted_tag = t.ent_type_ if t.ent_type_ else "O"
                sentence_pred.append(predicted_tag)

            biluo_tags = biluo_tags_from_offsets(doc, entities["entities"])
            sentence_cor = [t.split("-")[-1] for t in biluo_tags]

            predicted_tags.extend(sentence_pred)
            correct_tags.extend(sentence_cor)

            labels.update([l for l in sentence_pred + sentence_cor if l != "O"])

            if verbose:
                o.write(sentence + "\n")
                o.write(str(sentence_cor) + "\n")
                o.write(str(sentence_pred) + "\n")

    f = f1_score(correct_tags, predicted_tags, average="micro")
    if verbose:
        print(classification_report(correct_tags, predicted_tags, labels=list(labels)))

    return f


def main(model=None, output_dir=None, n_iter=100):
    """Load the model, set up the pipeline and train the entity recognizer."""
    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank("en")  # create blank Language class
        print("Created blank 'en' model")

    # create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner, last=True)
    # otherwise, get it so we can add labels
    else:
        ner = nlp.get_pipe("ner")

    # add labels
    for _, _, _, annotations in train_data:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]

    patience = 2
    history = []
    no_improvement = 0

    disabled = nlp.disable_pipes(*other_pipes)

    # reset and initialize the weights randomly – but only if we're
    # training a new model
    if model is None:
        nlp.begin_training()
    for itn in range(n_iter):
        random.shuffle(train_data)
        losses = {}
        # batch up the examples using spaCy's minibatch
        batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))
        for batch in batches:
            _, _, texts, annotations = zip(*batch)
            nlp.update(
                texts,  # batch of texts
                annotations,  # batch of annotations
                drop=0.5,  # dropout - make it harder to memorise data
                losses=losses,
            )
        print("Losses", losses)

        dev_f = evaluate(DEV_DATA, nlp)
        print("Dev F:", dev_f)

        if len(history) == 0 or dev_f > max(history):
            if output_dir is not None:
                output_dir = Path(output_dir)
                if not output_dir.exists():
                    output_dir.mkdir()
                disabled.restore()
                nlp.to_disk(output_dir)
                print("Saved model to", output_dir)

                disabled = nlp.disable_pipes(*other_pipes)

            no_improvement = 0
        else:
            no_improvement += 1

        history.append(dev_f)

        if no_improvement == patience:
            print("Stop training")
            break

    # test the saved model
    print("Loading from", output_dir)
    nlp = spacy.load(output_dir)

    f = evaluate(TEST_DATA, nlp, verbose=True)
    print("Test F:", f)


if __name__ == "__main__":
    main(model="en", output_dir="/tmp/grammar/")

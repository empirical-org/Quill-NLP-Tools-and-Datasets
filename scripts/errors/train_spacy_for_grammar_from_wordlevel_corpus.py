import random
from pathlib import Path
import spacy
import json
import ndjson
from collections import Counter
from functools import partial
from quillnlp.grammar import corpus
from tqdm import tqdm

from spacy.util import minibatch, compounding
from spacy.gold import biluo_tags_from_offsets
from sklearn.metrics import f1_score, classification_report

TEST_SIZE = 5000
DEV_SIZE = 5000

nlp = spacy.load("en")

files = ["wiki_errors.ndjson", "subtitles.ndjson", "notw.ndjson"]

train_data = []
for f in files:
    with open(f) as i:
        train_data += ndjson.load(i)[:7200000]

seen_sentences = set()
filtered_train_data = []
for sentence in train_data:
    if "synth_sentence" in sentence and sentence["synth_sentence"] not in seen_sentences:
        filtered_train_data.append((sentence["synth_sentence"], {"entities": sentence["entities"]}))
        seen_sentences.update([sentence["synth_sentence"]])
    elif "orig_sentence" in sentence and sentence["orig_sentence"] not in seen_sentences:
        filtered_train_data.append((sentence["orig_sentence"], {"entities": []}))
        seen_sentences.update([sentence["orig_sentence"]])

train_data = filtered_train_data
random.shuffle(train_data)

TEST_DATA = train_data[-TEST_SIZE:]
DEV_DATA = train_data[-(TEST_SIZE + DEV_SIZE):-TEST_SIZE]
TRAIN_DATA = train_data[:len(train_data) - TEST_SIZE - DEV_SIZE]
TRAIN_DATA = TRAIN_DATA[:20000000]

train_set = set([x[0] for x in TRAIN_DATA])
test_set = set([x[0] for x in TEST_DATA])
intersection = train_set & test_set
if len(intersection) > 0:
    print("Test sentences in training set:", len(intersection))

for x in intersection:
    print(x, len(x))

print("Train:", len(TRAIN_DATA))
print("Dev:", len(DEV_DATA))
print("Test:", len(TEST_DATA))

error_counter = Counter()
for item in TRAIN_DATA:
    error_counter.update([e[2] for e in item[1]["entities"]])

print(error_counter)

def evaluate(data, model, verbose=False):

    predicted_tags = []
    correct_tags = []
    labels = set()
    with open("grammar_results_spacy2.txt", "w") as o:
        for (sentence, entities) in data:
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

    print("Adding labels")
    # add labels
    for _, annotations in train_data:
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
        print(f"Epoch {itn}")
        random.shuffle(TRAIN_DATA)
        losses = {}
        # batch up the examples using spaCy's minibatch
        batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
        total = 0
        for batch in batches:
            texts, annotations = zip(*batch)
            total += len(texts)
            try:
                nlp.update(
                    texts,  # batch of texts
                    annotations,  # batch of annotations
                    drop=0.5,  # dropout - make it harder to memorise data
                    losses=losses,
                )
            except:
                continue
            percentage = int(total/len(TRAIN_DATA)*100)
            print(f"{percentage}", end="\r")
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
    main(model="en", output_dir="/tmp/grammar20M/")

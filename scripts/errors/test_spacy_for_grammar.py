import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding
from spacy.tokens import Span
from spacy.gold import biluo_tags_from_offsets
from sklearn.metrics import f1_score, classification_report

# TODO: Woman/Women also capitalized


nlp = spacy.load("en")


def get_data_from_file(f, num):
    with open(f) as i:
        lines = list(set([line.strip() for line in i if len(line.strip()) > 10]))

    random.shuffle(lines)
    return lines[:num]


TEST_SIZE = 2000
DEV_SIZE = 2000

num_sentences = 20000
woman_sentences = get_data_from_file("woman_women.txt", num_sentences)
women_sentences = get_data_from_file("women_woman.txt", num_sentences)
its_sentences = get_data_from_file("its_it_s_shuffled_100000.txt", num_sentences)
it_s_sentences = get_data_from_file("it_s_its_shuffled_100000.txt", num_sentences)
then_sentences = get_data_from_file("then_shuffled_100000.txt", num_sentences)
than_sentences = get_data_from_file("than_shuffled_100000.txt", num_sentences)

lines = list(set(woman_sentences + women_sentences + its_sentences + it_s_sentences +
                 then_sentences + than_sentences))
random.shuffle(lines)

replacements = {"its": "it's", "Its": "It's",
                "It": "Its", "it": "its",
                "then": "than", "Then": "Than",
                "than": "then", "Than": "Then"}

TRAIN_DATA = []
for line in lines:
    if random.random() < 0.5:
        doc = nlp(line)
        token_strings = set([t.text for t in doc])
        new_tokens = []
        entities = []
        skip_token = False
        for token in doc:
            if skip_token:
                skip_token = False
            elif len(entities) > 0:  # we only make one correction per sentence
                new_tokens.append(token.text_with_ws)
            elif token.text.lower() == "woman":
                new_tokens.append("women" + token.whitespace_)
                entities.append((token.idx, token.idx + len(token.text), "WOMAN"))
            elif token.text.lower() == "women":
                new_tokens.append("woman" + token.whitespace_)
                entities.append((token.idx, token.idx + len(token.text), "WOMAN"))

            elif token.text == "then" or token.text == "Then":
                new_tokens.append(replacements[token.text] + token.whitespace_)
                entities.append((token.idx, token.idx + len(token.text), "THEN"))
            elif token.text == "than" or token.text == "Than":
                new_tokens.append(replacements[token.text] + token.whitespace_)
                entities.append((token.idx, token.idx + len(token.text), "THEN"))

            elif token.text == "its" or token.text == "Its":
                new_tokens.append(replacements[token.text] + token.whitespace_)
                entities.append((token.idx, token.idx + len("it's"), "ITS"))
            elif token.i < len(doc)-1 and (token.text == "it" or token.text == "It") and doc[token.i+1].text == "'s":
                new_tokens.append(replacements[token.text] + doc[token.i+1].whitespace_)
                entities.append((token.idx, token.idx + len("its"), "ITS"))
                skip_token = True
            else:
                new_tokens.append(token.text_with_ws)

        TRAIN_DATA.append(("".join(new_tokens), {"entities": entities}))
    else:
        TRAIN_DATA.append((line, {"entities": []}))

TEST_DATA = TRAIN_DATA[-TEST_SIZE:]
DEV_DATA = TRAIN_DATA[-(TEST_SIZE+DEV_SIZE):-TEST_SIZE]
TRAIN_DATA = TRAIN_DATA[:len(TRAIN_DATA)-TEST_SIZE-DEV_SIZE]

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


def evaluate(data, model, verbose=False):

    predicted_tags = []
    correct_tags = []
    labels = set()
    with open("grammar_results_spacy.txt", "w") as o:
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

    # add labels
    for _, annotations in TRAIN_DATA:
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
        random.shuffle(TRAIN_DATA)
        losses = {}
        # batch up the examples using spaCy's minibatch
        batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
        for batch in batches:
            texts, annotations = zip(*batch)
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

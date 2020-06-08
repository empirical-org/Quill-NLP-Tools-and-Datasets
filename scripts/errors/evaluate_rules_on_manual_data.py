import spacy
from quillnlp.grammar.grammarcheck import GrammarError, SpaCyGrammarChecker
from sklearn.metrics import classification_report
from sklearn.preprocessing import MultiLabelBinarizer

CORRECT_LABEL = "Correct"

files = {
    GrammarError.INCORRECT_IRREGULAR_PAST_TENSE.value: {
        "positive": "data/validated/verb_errors/incorrect-irregular-past-tense-positive.txt",
        "negative": "data/validated/verb_errors/incorrect-irregular-past-tense-negative.txt"
    },
    GrammarError.SVA_COLLECTIVE_NOUN.value: {
        "positive": "data/validated/verb_errors/subject-verb-agreement-with-collective-noun-positive.txt",
        "negative": "data/validated/verb_errors/subject-verb-agreement-with-collective-noun-negative.txt"
    },
    GrammarError.MAN_MEN.value: {
        "positive": "data/validated/verb_errors/man-men-positive.txt",
        "negative": "data/validated/verb_errors/man-men-negative.txt"
    },
    GrammarError.WOMAN_WOMEN.value: {
        "positive": "data/validated/verb_errors/woman-women-positive.txt",
        "negative": "data/validated/verb_errors/woman-women-negative.txt"
    },
    GrammarError.CAPITALIZATION.value: {
        "positive": "data/validated/verb_errors/capitalization-positive.txt",
        "negative": "data/validated/verb_errors/capitalization-negative.txt"
    },
    GrammarError.REPEATED_WORD.value: {
        "positive": "data/validated/verb_errors/repeated-word-positive.txt",
        "negative": "data/validated/verb_errors/repeated-word-negative.txt"
    },
    GrammarError.QUESTION_MARK.value: {
        "positive": "data/validated/verb_errors/question-mark-positive.txt",
        "negative": "data/validated/verb_errors/question-mark-negative.txt"
    },
    GrammarError.PLURAL_POSSESSIVE.value: {
        "positive": "data/validated/verb_errors/plural-vs-possessive-positive.txt",
        "negative": "data/validated/verb_errors/plural-vs-possessive-negative.txt"
    },
    GrammarError.COMMAS_IN_NUMBERS.value: {
        "positive": "data/validated/verb_errors/commas-in-numbers-positive.txt",
        "negative": "data/validated/verb_errors/commas-in-numbers-negative.txt"
    },
    GrammarError.YES_NO_COMMA.value: {
        "positive": "data/validated/verb_errors/commas-after-yes-no-positive.txt",
        "negative": "data/validated/verb_errors/commas-after-yes-no-negative.txt"
    },
    GrammarError.SINGULAR_PLURAL.value: {
        "positive": "data/validated/verb_errors/singular-plural-noun-positive.txt",
        "negative": "data/validated/verb_errors/singular-plural-noun-negative.txt"
    },
    GrammarError.INCORRECT_PARTICIPLE.value: {
        "positive": "data/validated/verb_errors/incorrect-participle-positive.txt",
        "negative": "data/validated/verb_errors/incorrect-participle-negative.txt"
    },
    GrammarError.PASSIVE_WITH_INCORRECT_PARTICIPLE.value: {
        "positive": "data/validated/verb_errors/passive-with-incorrect-participle-positive.txt",
        "negative": "data/validated/verb_errors/passive-with-incorrect-participle-negative.txt"
    },
    GrammarError.THAN_THEN.value: {
        "positive": "data/validated/verb_errors/than-then-positive.txt",
        "negative": "data/validated/verb_errors/than-then-negative.txt"
    },
    GrammarError.PERFECT_TENSE_WITHOUT_HAVE.value: {
        "positive": "data/validated/verb_errors/perfect-without-have-positive.txt",
        "negative": "data/validated/verb_errors/perfect-without-have-negative.txt"
    },
    GrammarError.VERB_SIMPLE_PAST_INSTEAD_OF_PAST_PERFECT.value: {
        "positive": "data/validated/verb_errors/simple-past-instead-of-past-perfect-positive.txt",
        "negative": "data/validated/verb_errors/simple-past-instead-of-past-perfect-negative.txt"
    },
    GrammarError.PERFECT_TENSE_WITH_SIMPLE_PAST.value: {
        "positive": "data/validated/verb_errors/past-tense-instead-of-participle-positive.txt",
        "negative": "data/validated/verb_errors/past-tense-instead-of-participle-negative.txt"
    },
    GrammarError.PERFECT_PROGRESSIVE_WITHOUT_HAVE.value: {
        "positive": "data/validated/verb_errors/perfect-progressive-without-have-positive.txt",
        "negative": "data/validated/verb_errors/perfect-progressive-without-have-negative.txt"
    },
    GrammarError.PERFECT_PROGRESSIVE_WITH_INCORRECT_BE_WITHOUT_HAVE.value: {
        "positive": "data/validated/verb_errors/perfect-progressive-with-incorrect-be-and-without-have-positive.txt",
        "negative": "data/validated/verb_errors/perfect-progressive-with-incorrect-be-and-without-have-negative.txt"
    },
    GrammarError.PASSIVE_PERFECT_WITHOUT_HAVE.value: {
        "positive": "data/validated/verb_errors/passive-perfect-without-have-positive.txt",
        "negative": "data/validated/verb_errors/passive-perfect-without-have-negative.txt"
    },
    GrammarError.PASSIVE_PERFECT_WITH_INCORRECT_PARTICIPLE.value: {
        "positive": "data/validated/verb_errors/passive-perfect-with-incorrect-participle-positive.txt",
        "negative": "data/validated/verb_errors/passive-perfect-with-incorrect-participle-negative.txt"
    },
    GrammarError.PASSIVE_WITHOUT_BE.value: {
        "positive": "data/validated/verb_errors/passive-without-be-positive.txt",
        "negative": "data/validated/verb_errors/passive-without-be-negative.txt"
    },
    GrammarError.PASSIVE_WITH_INCORRECT_BE.value: {
        "positive": "data/validated/verb_errors/passive-with-incorrect-be-positive.txt",
        "negative": "data/validated/verb_errors/passive-with-incorrect-be-negative.txt"
    },
    GrammarError.PASSIVE_INCORRECT_PAST_TENSE_AS_PARTICIPLE.value: {
        "positive": "data/validated/verb_errors/passive-with-simple-past-instead-of-participle-positive.txt",
        "negative": "data/validated/verb_errors/passive-with-simple-past-instead-of-participle-negative.txt"
    },
    GrammarError.SVA_SIMPLE_NOUN.value: {
        "positive": "data/validated/verb_errors/subject-verb-agreement-with-simple-noun-positive.txt",
        "negative": "data/validated/verb_errors/subject-verb-agreement-with-simple-noun-negative.txt"
    },
    GrammarError.SVA_PRONOUN.value: {
        "positive": "data/validated/verb_errors/subject-verb-agreement-with-pronoun-positive.txt",
        "negative": "data/validated/verb_errors/subject-verb-agreement-with-pronoun-negative.txt"
    }
}


def evaluate(checker, error_label, verbose=False):

    predicted_labels = []
    correct_labels = []

    f_pos = files[error_label]["positive"]
    f_neg = files[error_label]["negative"]

    with open(f_pos) as i:
        positive_sentences = [line.strip() for line in i]

    with open(f_neg) as i:
        negative_sentences = [line.strip() for line in i]

    tp, tn, fp, fn = 0, 0, 0, 0
    for sentence in positive_sentences:
        correct_labels.append([error_label])
        errors = checker.check(sentence)
        error_types = set([e.type for e in errors])
        if len(error_types) > 0:
            predicted_labels.append(list(error_types))
        else:
            predicted_labels.append([CORRECT_LABEL])

        if error_label in error_types:
            tp += 1
        else:
            fn += 1

        if verbose:
            print("\t".join([sentence, error_label, str(set(errors))]) + "\n")

    for sentence in negative_sentences:
        correct_labels.append([CORRECT_LABEL])
        errors = checker.check(sentence)
        error_types = set([e.type for e in errors])
        if len(error_types) > 0:
            predicted_labels.append(list(error_types))
        else:
            predicted_labels.append([CORRECT_LABEL])

        if error_label in error_types:
            fp += 1
        else:
            tn += 1

        if verbose:
            print("\t".join([sentence, CORRECT_LABEL, str(set(errors))]) + "\n")

    print(error_label)
    print("True positives:", tp)
    print("False positives:", fp)
    print("Accuracy:", (tp + tn)/(len(positive_sentences + negative_sentences)))
    return predicted_labels, correct_labels


checker = SpaCyGrammarChecker(["models/spacy_grammar", "models/spacy_grammar_verbs2/"])

global_predicted_labels = []
global_correct_labels = []
for error_label in files:
#for error_label in [GrammarError.CAPITALIZATION.value]:
    new_predicted_labels, new_correct_labels = evaluate(checker, error_label, verbose=True)
    global_predicted_labels.extend(new_predicted_labels)
    global_correct_labels.extend(new_correct_labels)


mlb = MultiLabelBinarizer()
global_correct_labels_binary = mlb.fit_transform(global_correct_labels)
global_predicted_labels_binary = mlb.transform(global_predicted_labels)

print(classification_report(global_correct_labels_binary,
                            global_predicted_labels_binary, target_names=mlb.classes_))

confusion_matrix = {}
for label in mlb.classes_:
    confusion_matrix[label] = {}
    for other_label in mlb.classes_:
        confusion_matrix[label][other_label] = 0


for correct_labels, predicted_labels in zip(global_correct_labels, global_predicted_labels):
    for predicted_label in predicted_labels:
        if predicted_label in confusion_matrix:
            if predicted_label in correct_labels:
                confusion_matrix[predicted_label][predicted_label] += 1
            else:
                for correct_label in correct_labels:
                    confusion_matrix[predicted_label][correct_label] += 1

    for correct_label in correct_labels:
        if correct_label not in predicted_labels and correct_label in confusion_matrix:
            for predicted_label in predicted_labels:
                if predicted_label in confusion_matrix:
                    confusion_matrix[predicted_label][correct_label] += 1

print(mlb.classes_)
print("P| C->" + "\t" + "\t".join(mlb.classes_))
for p in mlb.classes_:
    print(p + "\t" + "\t".join([str(confusion_matrix[p][c]) for c in mlb.classes_]))

import spacy
import csv
from tqdm import tqdm

from enum import Enum

nlp = spacy.load('en_core_web_sm')

class Dependency(Enum):
    SUBJECT = "nsubj"
    PASS_SUBJECT = "nsubjpass"
    DIRECT_OBJECT = "dobj"
    CLAUSAL_SUBJECT = "csubj"
    PASS_AUXILIARY = "auxpass"
    COMPOUND = "compound"
    AUX = "aux"
    ROOT = "ROOT"
    CONJUNCTION = "conj"
    DETERMINER = "det"
    ADVERBIAL_CLAUSE = "advcl"
    ATTRIBUTE = "attr"
    CCOMP = "ccomp"
    EXPLETIVE = "expl"

CLAUSE_MARKERS = set(['conj', 'advcl', 'ccomp', 'parataxis'])
# CLAUSE_MARKERS = set(['ccomp', 'conj', 'parataxis'])

COORDINATING_CONJUNCTIONS = set(['for', 'and', 'nor', 'but', 'or', 'yet', 'so'])
SUBORDINATING_CONJUNCTIONS = set(['after', 'although', 'as', 'because', 'before', 'though', 'if', 'since', 'while', 'unless', 'why', 'until', 'when', 'whenever', 'where', 'whereas', 'wherever', 'whether', 'that', 'to'])
QUESTION_WORDS = set(['what', 'which', 'who', 'where', 'why', 'when', 'how', 'whose'])
FINITE_VERB_TAGS = set(['VBP', 'VBZ', 'VBD', 'MD'])

test_sentences = [
    ('I told you to stay.', 1),
    ('I told him he should stay.', 1),
    ('I told him he should stay, because it was already dark outside.', 2),
    ('The NCAA believes it undermines education', 1)
]

def identify_prompt(sentence):
    split_so = sentence.split(', so ')
    if len(split_so) > 1:
        return split_so[0] + ', so'

    split_but = sentence.split(', but ')
    if len(split_but) > 1:
        return split_but[0] + ', but'

    split_because = sentence.split(' because ')
    if len(split_because) > 1:
        return split_because[0] + ' because'

    print('Could not identify prompt:')
    print(sentence)
    return ''


def get_all_heads(doc, token, heads_so_far=[]):

    if token.head == token:
        return []
    elif token.dep_ in CLAUSE_MARKERS:
        return [token]

    return heads_so_far + [token.head] + get_all_heads(doc, token.head, heads_so_far)


def get_previous_token(clause, doc):
    return doc[clause[0].i-1] if clause[0].i > 0 else None


def subject_in_tokens(tokens):
    dependencies = [t.dep_ for t in tokens]
    return Dependency.SUBJECT.value in dependencies or \
            Dependency.PASS_SUBJECT.value in dependencies or \
            Dependency.CLAUSAL_SUBJECT.value in dependencies

def get_first_word_token(tokens):
    for token in tokens:
        if not token.pos_ == 'PUNCT':
            return token

    return None


def is_mother_of_dependent_clause(independent_clause_token, dependent_clause_tokens, doc):
    for token in dependent_clause_tokens:
        if independent_clause_token in get_all_heads(doc, token):
            return True

    return False


def is_finite(verb):
    verb_phrase = list(verb.lefts) + [verb]
    for verb in verb_phrase:
        if verb.tag_ in FINITE_VERB_TAGS:
            return True

    return False


def is_subordinate_question(doc, children):
    first_clause_word = get_first_word_token(children)
    if first_clause_word.i > 0:
        word_before_clause = doc[first_clause_word.i-1]
    else:
        return False

    if word_before_clause.pos_ != 'PUNCT' and first_clause_word.text.lower() in QUESTION_WORDS:
        return True

    return False

def is_preceded_by_punctuation(token, doc):
    return token.i > 0 and doc[token.i-1].pos_ == 'PUNCT'


def get_clauses(sentence, verbose=True):
    doc = nlp(sentence)

    deps = [t.dep_ for t in doc]
    # if not 'ccomp' in deps:
    #     return {}

    sentence = []

    for token in doc:
        print(token, token.pos_, token.dep_, token.head)
        if token.dep_ == 'ROOT' or (token.dep_ in CLAUSE_MARKERS and (token.pos_ == 'VERB' or token.pos_ == 'AUX')):
            children = [t for t in doc if token in get_all_heads(doc, t) or t == token]
            # print(children)

            previous_token = get_previous_token(children, doc)
            # if len(sentence) > 0:
            #     x = is_mother_of_dependent_clause(token, sentence[-1]['tokens'], doc)
            #     print(token, x)

            # 'mark': A marker (mark) is the word introducing a clause subordinate to another clause.
            if children[0].text.lower() in SUBORDINATING_CONJUNCTIONS:  # and children[0].dep_ == 'mark':
                clause = {
                    'clause_type': 'dependent',
                    'tokens': children,
                    'head': token
                }
                sentence.append(clause)
            elif previous_token is None:
                clause = {
                    'clause_type': 'independent/1',
                    'tokens': children
                }
                sentence.append(clause)
            elif previous_token.text.lower() in COORDINATING_CONJUNCTIONS:
                if subject_in_tokens(children):
                    clause = {
                        'clause_type': 'independent/2',
                        'tokens': children
                    }
                    sentence.append(clause)
                elif len(sentence) > 0:
                    sentence[-1]['tokens'].extend(children)

                    # put the tokens in the right order, because sentence-final
                    # punctuation may already be a child of the previous clause
                    sentence[-1]['tokens'] = sorted(sentence[-1]['tokens'], key=lambda x:x.i)

            # A run-on is a clause without coordinating conjunction that follows an independent
            # clause and that has a subject.
            elif len(sentence) > 0 and not (sentence[-1]['clause_type'] == 'dependent' and sentence[-1]['head'].head.i < sentence[-1]['head'].i):

                # Exclude clausal complements like 'He says that you like to swim',
                # which begin with SCONJ.
                # Exclude subordinate questions like 'He told me what I should do'.
                # Exclude infinitival complements like 'I told him you should stay',
                # which have an infinitive as a main verb.
                # But we do keep 'I went home, I read a book', which are also CCOMP
                first_clause_word = get_first_word_token(children)
                if first_clause_word and subject_in_tokens(children) and \
                        not first_clause_word.pos_ == 'SCONJ' and not is_subordinate_question(doc, children) and \
                        is_finite(token) and (children[0].pos_ == 'PUNCT' or is_preceded_by_punctuation(children[0], doc)):
                    clause = {
                        'clause_type': 'run-on',
                        'tokens': children
                    }
                    sentence.append(clause)
                else:
                    sentence[-1]['tokens'].extend(children)
                    sentence[-1]['tokens'] = sorted(sentence[-1]['tokens'], key=lambda x:x.i)
            else:
                clause = {
                    'clause_type': 'independent/3',
                    'tokens': children
                }
                sentence.append(clause)
            #print(children, get_previous_token(children, doc))

    return sentence


def preceded_by_punctuation(tokens, doc):
    if tokens[0].pos_ == 'PUNCT' and not tokens[0].text == ';':
        return True
    elif tokens[0].i > 0 and doc[tokens[0].i-1].pos_ == 'PUNCT' and not doc[tokens[0].i-1].text == ';':
        return True
    return False




def get_clauses2(sentence, verbose=True):
    doc = nlp(sentence)

    deps = [t.dep_ for t in doc]
    # if not 'ccomp' in deps:
    #     return {}

    sentence = []

    for token in doc:
        # print(token, token.pos_, token.dep_, token.head)
        if token.dep_ == 'ROOT' or (token.dep_ in CLAUSE_MARKERS and (token.pos_ == 'VERB' or token.pos_ == 'AUX')):
            children = [t for t in doc if token in get_all_heads(doc, t) or t == token]
            # print(children)
            sentence.append({
                'clause_type': None,
                'tokens': children,
                'head': token,
            })


    new_sentence = []
    for clause in sentence:

        previous_token = get_previous_token(clause['tokens'], doc)
        first_word_token = get_first_word_token(clause['tokens'])

        if clause['tokens'][0].dep_ == 'mark' and len(new_sentence) > 0:
            new_sentence[-1]['tokens'].extend(clause['tokens'])
        elif clause['tokens'][0].dep_ == 'mark':
            clause['clause_type'] = 'dependent'
            new_sentence.append(clause)
        elif not is_finite(clause['head'].head) and len(new_sentence) > 0:
            new_sentence[-1]['tokens'].extend(clause['tokens'])
        elif not is_finite(clause['head']) and len(new_sentence) > 0:
            new_sentence[-1]['tokens'].extend(clause['tokens'])
        elif len(new_sentence) == 0:
            clause['clause_type'] = 'independent'
            new_sentence.append(clause)
        elif len(new_sentence) == 1 and new_sentence[0]['clause_type'] == 'dependent':
            clause['clause_type'] = 'independent'
            new_sentence.append(clause)
        elif first_word_token and first_word_token.text.lower() in COORDINATING_CONJUNCTIONS:
            clause['clause_type'] = 'independent'
            new_sentence.append(clause)
        elif previous_token and previous_token.text.lower() in COORDINATING_CONJUNCTIONS:
            clause['clause_type'] = 'independent'
            new_sentence.append(clause)
        elif not first_word_token.pos_ == 'SCONJ' and not is_subordinate_question(doc, clause['tokens']):
            clause['clause_type'] = 'run-on'
            new_sentence.append(clause)
        else:
            new_sentence.append(clause)

    return new_sentence


def evaluate():
    evaluation_file = 'data/validated/run_on_sentences.tsv'

    correct = 0
    total = 0
    false_positives = 0
    false_negatives = 0

    with open(evaluation_file) as i:
        reader = csv.reader(i, delimiter='\t')
        for line in reader:
            prompt, entry, num = line
            # sentence = ' '.join([prompt, entry])
            sentence = entry[0].upper() + entry[1:]

            print('--'*20)
            print(sentence)

            num_run_ons = int(num)
            clauses = get_clauses2(sentence)
            predicted_run_ons = [c for c in clauses if c['clause_type'] == 'run-on']
            num_predicted_run_ons = len(predicted_run_ons)

            if num_predicted_run_ons == num_run_ons:
                correct += num_run_ons
            elif num_predicted_run_ons > num_run_ons:
                false_positives += (num_predicted_run_ons-num_run_ons)
            elif num_predicted_run_ons < num_run_ons:
                false_negatives += (num_run_ons-num_predicted_run_ons)

            print(sentence)
            print('Correct:', num)
            print('Predicted:', num_predicted_run_ons)
            for c in clauses:
                print(c)
            total +=1
            # input()

    precision = correct/(correct+false_positives) if (correct+false_positives) > 0 else 0
    recall = correct/(correct+false_negatives) if (correct+false_negatives) > 0 else 0
    fscore = 2*precision*recall/(precision+recall) if (precision+recall) > 0 else 0

    print('Precision:', precision)
    print('Recall:', recall)
    print('F1-score:', fscore)


def run(test_file, output_file):

    data = []
    with open(test_file) as i:
        reader = csv.reader(i, delimiter=',')
        for line in reader:
            if len(line) > 1 and len(line[0].strip()) > 0 and len(line[1].strip()) > 0:
                prompt = line[0]
                entry = line[1]
                sentence = ' '.join([prompt, entry])
                data.append((sentence, prompt, entry))

    with open(output_file, 'w') as o:
        writer = csv.writer(o, delimiter='\t')
        for sentence, prompt, entry in tqdm(data):

            clauses = get_clauses2(sentence)

            output = [prompt, entry, len(clauses)]  # + [clause['clause_type'] + ':' + ' '.join([t.text for t in clause['tokens']]) for clause in clauses]
            writer.writerow(output)


if __name__ == '__main__':
    # evaluate()
    run('/home/yves/projects/grammar-api3/grammar-api/quill_responses_202209_automl.csv',
        '/home/yves/projects/grammar-api3/grammar-api/cquill_responses_202209_automl_clauses.tsv')
    # sentence = "It didn't last long, this temporary solution ran dry again after only two months because majority of the water was absorbed into the ground."
    # clauses = get_clauses(sentence, verbose=True)
    # print(sentence)
    # for c in clauses:
    #     print(c)
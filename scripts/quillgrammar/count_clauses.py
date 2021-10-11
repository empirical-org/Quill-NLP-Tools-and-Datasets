import spacy
import csv
from tqdm import tqdm

nlp = spacy.load('en_core_web_sm')

clause_markers = set(['conj', 'advcl', 'relcl', 'ccomp'])

test_sentences = [
    ('He came home, took a shower and immediately went to bed.', 3),
    ('He ate a pizza and drank a bottle of wine.', 2),
    ('He ate a pizza and a burrito.', 1),
    ('I told you to stay.', 1),
    ('I told him he should stay.', 2),
    ('I told him he should stay, because it was already dark outside.', 3),
    ('The NCAA believes it undermines education', 2)
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
    elif token.dep_ in clause_markers:
        return [token]

    return heads_so_far + [token.head] + get_all_heads(doc, token.head, heads_so_far)


def count_clauses(sentence):
    doc = nlp(sentence)

    clauses = []
    for token in doc:
        print(token, token.dep_)
        if token.dep_ == 'ROOT' or (token.dep_ in clause_markers and token.pos_ == 'VERB'):
            children = [t for t in doc if token in get_all_heads(doc, t) or t == token]
            clauses.append(children)

    return clauses


for sentence, num in test_sentences:
    clauses = count_clauses(sentence)
    assert num == len(clauses)


test_file = 'data/raw/Student_Data_Grammar_Engine_Eval_Grammar_Output_20210906 - Set 09.15.21.a.csv'
output_file = 'data/raw/Student_Data_Grammar_Engine_Eval_Grammar_Output_20210906 - Set 09.15.21.a_clauses.csv'


data = []
with open(test_file) as i:
    reader = csv.reader(i, delimiter=',')
    for line in reader:
        if len(line) == 2:
            data.append(line)
        elif len(line) == 1:
            data.append((line[0], identify_prompt(line[0])))
        elif len(line[9]) > 0:
            data.append((line[9], line[8]))


with open(output_file, 'w') as o:
    writer = csv.writer(o, delimiter='\t')
    for sentence, prompt in tqdm(data):
        entry = sentence.replace(prompt, '')

        clauses = count_clauses(sentence)

        # if len(clauses) > 2:
        #     print(sentence)
        #     print(entry)
        #     print(clauses)    
        #     print(len(clauses))    
        #     input()

        output = [sentence, prompt, entry, len(clauses)] + [' '.join([t.text for t in clause]) for clause in clauses]
        writer.writerow(output)

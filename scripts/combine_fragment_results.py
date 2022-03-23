import csv

fragment_map = {
    'no_fragment': 'No fragment',
    'fragment': 'Fragment',
    'fragment_no_subject': '1.2 Missing Subject', 
    'fragment_no_verb': '3.1. Fragment - Subject + Object -  Missing Verb in Between',
    'fragment_no_aux': '1.4 Missing verb, missing subject and verb, or missing auxiliary',
    'fragment_no_object': '3.2. Missing object for a transitive verb',
    'fragment_prepositional_phrase': '2.1. Missing subject and verb - Prepositional Phrase',
    'fragment_adverbial_clause': '2.2. Missing subject and verb - Dependent Clause',
    'fragment_relative_clause': '3.3. Missing subject and verb - Relative Clause',
    'fragment_infinitive_phrase': '3.5. Missing verb, or missing subject and verb - Infinitive Phrases',
    'fragment_noun_phrase': '1.1 Missing verb, or missing subject and verb - All Noun Phrases',
    'fragment_verb_phrase': '1.3 Missing verb, missing subject and verb, or missing subject and auxiliary - Participial phrase, gerund phrase, or progressive tense verb'
}

inputfile_2classes = '/home/yves/projects/grammar-api/comprehension_full_sentences_fragments_2c.tsv'
inputfile_fine = '/home/yves/projects/grammar-api/comprehension_full_sentences_fragments_fine.tsv'
outputfile = '/home/yves/projects/grammar-api/comprehension_full_sentences_fragments_all.tsv'

def read_file(filename):
    with open(filename) as i:
        data = []
        reader = csv.reader(i, delimiter='\t')
        for line in reader:
            data.append(line)

    return data


data_2classes = read_file(inputfile_2classes)
data_fine = read_file(inputfile_fine)

print(len(data_2classes))
print(len(data_fine))

assert len(data_2classes) == len(data_fine)

with open(outputfile, 'w') as o:
    writer = csv.writer(o, delimiter='\t')
    for item_2c, item_fine in zip(data_2classes, data_fine):
        sentence_2c, prompt_2c, response_2c, label_2c = item_2c
        sentence_fine, prompt_fine, response_fine, label_fine = item_fine

        assert response_2c == response_fine

        writer.writerow([sentence_2c, prompt_2c, response_2c, label_2c, label_fine, fragment_map[label_fine]])


"""Generate different types of fragments"""
import spacy
nlp = spacy.load('en') # takes a while, handle possible error first

# Constants
ORIGINAL_SENTENCES_PATH = 'original_sentences'
SENTENCES_WITH_SUBORDINATING_CONJUCTIONS_PATH = \
  'original_sentences/subordinateConjunctionSentences.txt'
NEW_SUBCONJ_SENTENCES_PATH = 'fragments/subordinating_conj.txt'


# There are 7 coordinating conj. if a conj. is not coordinating it's
# subordinating
LIST_OF_COORDINATING_CONJUNCTIONS = ['for', 'and', 'nor', 'or', 'but', 'yet',
                                     'so'
                                    ]


def generate_participle_phrase_fragments():
    pass



def generate_subordinate_clause_fragment():
    """
    - A subordinate clause contains a subordinate conjunction, a subject, and a
      verb. Because this type of clause does not express a complete thought, it
      cannot stand alone as a complete sentence.
    - *Flooring the accelerator, Juan wove through the heavy traffic. **As his
      ex-girlfriend Gigi chased him down the interstate.***
    """
    with open(SENTENCES_WITH_SUBORDINATING_CONJUCTIONS_PATH, 'r') as sentences:
        # find subordinate clause
        new_sub_clause_file = open(NEW_SUBCONJ_SENTENCES_PATH, 'w+')
        batch_size = 1000
        current_batch_size = 0
        num_batches = 0
        batch = ''
        for sentence in sentences:
            subordinate_clause = ''
            for clause in sentence.split(','):
                doc = nlp(clause)
                first_word_of_clause = doc[0]
                if (repr(first_word_of_clause) not in
                        LIST_OF_COORDINATING_CONJUNCTIONS and
                        first_word_of_clause.pos_ in ['ADP', 'SCONJ', 'CONJ']):
                    if doc[-1].pos_ != 'PUNCT':
                        subordinate_clause = \
                        '{}.\n'.format(clause)
                    else:
                        subordinate_clause = '{}\n'.format(clause)
             
            batch += subordinate_clause
            current_batch_size += 1


            if current_batch_size >= batch_size:
                current_batch_size = 0
                num_batches += 1
                print('writing batch...')
                new_sub_clause_file.write(batch)
        new_sub_clause_file.close()


def main():
    """Regenerate entire corpus"""
    generate_subordinate_clause_fragment()

if __name__ == '__main__':
    main()

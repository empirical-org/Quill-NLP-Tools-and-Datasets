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
    """
     - A participle phrase usually begins with an ing or ed word. In the case of
       irregular verbs, an irregular past participle, like burnt or spoken, will
       begin the phrase.
     - *Aunt Olivia always wears a motorcycle helmet. **Worrying that a meteor or
     chunk of space debris will conk her on the head.***
    """

    # add present or past participle to start of fragment
    # [Dying, burnt, famished, bruised, wounded, fuming, worrying, soaring, delighted]
    #
    # add a prepositional phrase or subordinate clause (except a subordinate
    # clause starting with a relative pronoun) or clause starting with a
    # coordinating conj.  [at the thought of him, that she could be so callous,
    # by the metal handle, to see his little puppy, like a dog, so much he was
    # sick, until his was dead, for he was a happy man, where the flesh was
    # pinched, because she was so beautiful, as a sailor back from sea,  
    #  - prepositional phrases are a preposition combined with a noun, pronoun,
    #  gerund, or clause
    #  - 
    #




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

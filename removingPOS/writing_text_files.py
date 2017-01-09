'''
Create a new branch
CODE IS GOING TO BE CHANGED NOW: I want everything to output the following -
For each newly created file start creating final text files:
First file output: original list of POS || updated list POS || word removed
Second file output to help people understand: Original sentence: , Word removed: , Updated sentence: , POS original,POS removed words, POS updated

'''

import pickle
from nlpSpacy import *
from noun_remove import noun_removal
from verb_remove import verb_removal
from noun_verb_remove import noun_verb_removal

def load(filename):
    with open(filename, "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break

# items = load('./updatedSentences/nounSentences/nounRemoval.p')
# lst = []
# for i in items:
#     lst.append(i)
# print("At this point i should already have a list: ")
# print(len(lst))
# for tup in lst:
#     print(tup)


def make_updated_sentence(s,match_found,removal_type):
    sentence_wo_noun = delete_words_string(s,match_found)
    if (removal_type == "noun_verb"):
        return sentence_wo_noun
    else:
        return sentence_wo_noun[0].upper() + sentence_wo_noun[1:]

#NOUN:
def noun_textfile():
    with open('./updatedSentences/nounSentences/errorSentences.txt','w') as error_n, \
         open('./updatedSentences/nounSentences/detailedRemoval.txt','w') as details_removal, \
         open('./updatedSentences/nounSentences/nounRemoval.p','wb') as tuple_write, \
         open('./originalSentences/testingFile.txt','r') as f:
            for line in f:
                line = line.rstrip('\n')
                n_sentence_rem = noun_removal(line)
                if (n_sentence_rem[0] != "ERROR"):
                    noun_pos = n_sentence_rem[2][0]
                    pickle.dump((n_sentence_rem[0], #serialization
                                 n_sentence_rem[1],
                                 noun_pos),
                                tuple_write)
                    noun_found = make_str(noun_pos).rstrip('\n')
                    details_removal.write("Original Sentence: " + line + " ||| Word Removed: " + noun_found + " ||| Updated Sentence: " + make_updated_sentence(line,noun_found,"").rstrip('\n') + " ||| POS Original Sentence: " +  tup_list_to_string(n_sentence_rem[0]) + " ||| POS Word Removed: " + tup_list_to_string(noun_pos) + " ||| POS Updated Sentence: " + tup_list_to_string(n_sentence_rem[1]) + '\n')
                else:
                    error_n.write(line + ' ||| POS Original Sentence: ' + tup_list_to_string(n_sentence_rem[1]) + '\n')
# #verb
def verb_textfile():
    with open('./updatedSentences/verbSentences/errorSentences.txt','w') as error_v, \
         open('./updatedSentences/verbSentences/detailedRemoval.txt','w') as details_removal, \
         open('./updatedSentences/verbSentences/verbRemoval.p','wb') as tuple_write, \
         open('./originalSentences/testingFile.txt','r') as f:
            for line in f:
                line = line.rstrip('\n')
                v_sentence_rem = verb_removal(line) ###change the name of this variable
                if (v_sentence_rem[0] != "ERROR"):
                    pickle.dump(v_sentence_rem, tuple_write)
                    verb_pos = v_sentence_rem[2]
                    verb_found = make_str(verb_pos)
                    details_removal.write("Original Sentence: " + line + " ||| Word Removed: " + verb_found.rstrip('\n') + " ||| Updated Sentence: " + make_updated_sentence(line, verb_found,"").rstrip('\n') + " ||| POS Original Sentence: " +  tup_list_to_string(v_sentence_rem[0]) + " ||| POS Word Removed: " + tup_list_to_string(verb_pos) + " ||| POS Updated Sentence: " + tup_list_to_string(v_sentence_rem[1]) + '\n')
                else:
                    error_v.write(line + ' ||| POS Original Sentence: ' + tup_list_to_string(v_sentence_rem[1]) + '\n')
#
# # # THIS IS FOR NOUNS AND VERBS
def noun_verb_textfile():
    with open('./updatedSentences/nounverbSentences/errorSentences.txt','w') as error_v, \
         open('./updatedSentences/nounverbSentences/detailedRemoval.txt','w') as details_removal, \
         open('./updatedSentences/nounverbSentences/nounverbRemoval.p','wb') as tuple_write, \
         open('./originalSentences/testingFile.txt','r') as f:
                        for line in f:
                            line = line.rstrip('\n')
                            nv_sentence_rem = noun_verb_removal(line)
                            if (nv_sentence_rem[0] != "ERROR"):
                                noun_pos_list = nv_sentence_rem[2][0]
                                verb_pos_list = nv_sentence_rem[2][1]
                                pickle.dump((nv_sentence_rem[0],
                                             nv_sentence_rem[1],
                                             noun_pos_list
                                             + verb_pos_list),
                                            tuple_write)
                                noun_str = make_str(noun_pos_list).rstrip('\n')
                                verb_str = make_str(verb_pos_list).rstrip('\n')
                                remove_noun_line = make_updated_sentence(line, noun_str,"noun_verb")
                                remove_verb_line = make_updated_sentence(remove_noun_line, verb_str,"").rstrip('\n')
                                details_removal.write("Original Sentence: " + line + " ||| Words Removed: " + noun_str + ' ' + verb_str + " ||| Updated Sentence: " + remove_verb_line + " ||| POS Original Sentence: " +  tup_list_to_string(nv_sentence_rem[0]) + " ||| POS Word Removed: " + tup_list_to_string(noun_pos_list + verb_pos_list) + " ||| POS Updated Sentence: " + tup_list_to_string(nv_sentence_rem[1]) + '\n')
                            else:
                                error_v.write(line + ' ||| POS Original Sentence: ' + tup_list_to_string(nv_sentence_rem[1]) + '\n')

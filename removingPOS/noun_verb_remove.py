from nlpSpacy import *
from noun_remove import noun_removal
from verb_remove import verb_removal

def noun_verb_removal(st):
    tup_lst = pos_tup_list(st)
    remove_noun_st = noun_removal(st) #i think this order is fine because also recognizes 're as verb
    remove_verb_st = verb_removal(st)
    if remove_noun_st[0] != "ERROR" and remove_verb_st[0] != "ERROR":
        noun_removed = remove_noun_st[1]
        verb_removed = remove_verb_st[1]
        st = delete_words_string(st,noun_removed)
        st = delete_words_string(st,verb_removed)
        return (st[0].upper()+st[1:], remove_noun_st[2]+' '+remove_verb_st[2],tup_list_to_string(tup_lst))
    else:
        return ("ERROR", tup_list_to_string(tup_lst))

with open('./updatedSentences/nounverbSentences/testing.txt','w') as remov:
    with open('./originalSentences/nounverbScreening.txt','r') as file:
        for line in file:
            print(line)
            nv_sentence_rem = noun_verb_removal(line)
            if nv_sentence_rem[0] != "ERROR":
                remov.write(line.rstrip('\n') + ' ||| ' + nv_sentence_rem[2] + '\n' )

#
# # THIS IS FOR NOUNS AND VERBS
# with open('./updatedSentences//nounverbSentences/nounverbErrorSentences.txt','w') as error_nv:
#     with open('./updatedSentences/nounverbSentences/nounverbCompleteSentences.txt','w') as nv_complete:
#         with open('./updatedSentences/nounverbSentences/nounverbRemovedSentences.txt','w') as nv_remov:
#             with open('./updatedSentences/nounverbSentences/nounverbRemovedSentences.txt','w') as nv_remov_clean:
#                 with open('./originalSentences/nounverbScreening.txt','r') as fi:
#                     for line in fi:
#                         noun_verb_removed = noun_verb_removal(line)
#                         print(noun_verb_removed)
#                         if noun_verb_removed[0] != "ERROR":
#                             nv_complete.write(line)
#                             nv_remov.write(noun_verb_removed[0] + ' ||| ' + noun_verb_removed[1] + ' ||| ' + line)
#                             nv_remov_clean.write(noun_verb_removed[0])
#                         else:
#                             error_nv.write('ERROR ||| ' + line.rstrip('\n') + noun_verb_removed[1] +'\n')

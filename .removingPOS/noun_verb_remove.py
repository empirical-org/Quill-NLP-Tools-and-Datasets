'''
The main function in this file is called noun_verb_removal and it
removes the first noun or group of consecutive nouns and verb or group
of consecutive verbs in a string. A string in this function is a
complete and correct sentence. This means it contains all of the
necessary requirements that a sentence needs to be correct.

The function uses several helper function in order to remove nouns
and verbs. It mainly makes use of the two functions in noun_remove.py
and verb_remove.py, both functions are found in the same directory as
this function.

Args:
    st: A complete sentence.

Returns:
    A tuple with three inputs. The first input is a lst of st. The
    second input is a lst of st, but with noun and verb matches
    removed from the lst. The third inpust is all of the noun and
    verb matched in the same format as lst.
'''
from nlpSpacy import *
from noun_remove import noun_removal
from verb_remove import verb_removal

def noun_verb_removal(st):
    sentence_pos_list = pos_tup_list(st)
    st_wo_noun = noun_removal(st)
    st_wo_verb = verb_removal(st)
    if (st_wo_noun[0] != "ERROR" and
        st_wo_verb[0] != "ERROR"):
        upd_pos_list_noun = remove_POS_matches(sentence_pos_list,
                                               st_wo_noun[2][1],
                                               'noun')
        upd_pos_list_verb =  remove_POS_matches(upd_pos_list_noun,
                                                st_wo_verb[2],
                                                'verb')
        return (sentence_pos_list,
                upd_pos_list_verb,
                (st_wo_noun[2][0],
                 st_wo_verb[2]))
    else:
        return ("ERROR", sentence_pos_list)

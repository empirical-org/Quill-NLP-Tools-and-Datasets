'''
Comments go in here:
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

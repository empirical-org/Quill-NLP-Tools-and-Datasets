from nlpSpacy import *
from noun_remove import noun_removal
from verb_remove import verb_removal

def noun_verb_removal(st):
    complete_pos_list = pos_tup_list(st)
    remove_noun_st = noun_removal(st)
    remove_verb_st = verb_removal(st)
    if remove_noun_st[0] != "ERROR" and remove_verb_st[0] != "ERROR":
        updated_pos_list_noun = remove_POS_matches(complete_pos_list,remove_noun_st[2][1],'noun')
        updated_pos_list_verb =  remove_POS_matches(updated_pos_list_noun,remove_verb_st[2],'verb')
        return (complete_pos_list, updated_pos_list_verb, (remove_noun_st[2][0], remove_verb_st[2]))
    else:
        return ("ERROR", complete_pos_list)

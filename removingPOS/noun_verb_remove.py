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

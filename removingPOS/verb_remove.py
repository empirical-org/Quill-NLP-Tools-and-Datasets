'''                                                                    |
removes verbs from a sentence
'''

from nlpSpacy import *

def verb_removal(st):
    def verb_list_found(lst):
        #returns a list of words that are consecutive verbs
        for i in range(len(lst)):
            if (lst[i][2] == "VERB"):
                verb_tup_lst = [lst[i]]
                for p in range(i+1,len(lst)):
                    if (lst[p][2] == "VERB"):
                        verb_tup_lst.append(lst[p])
                    else:
                        return verb_tup_lst
        return []

    def remove_hypens_words(st):
        #returns a string with all the hypenated words removed
        def remove_duplicates(lst):
            #removes word duplicates in a list
            word_dict = {}
            for i in range(len(lst)):
                word = lst[i]
                if (word_dict.get(word) == None):
                    word_dict[word] = word
            return list(word_dict.keys())

        reg = re.compile(r'\w+\-\w+\-\w+|\w+.\-.\w+.\-.\w+|\w+\-\w+|\w+.\-.\w+')
        matches_lst = remove_duplicates(reg.findall(st))
        while matches_lst != []:
            word = matches_lst.pop()
            st = delete_words_string(st, word)
        return st

    def hypen_verb_removal(s):
        #removes verbs from sentences wuth hypens
        sentence_pos_list = pos_tup_list(s)
        wo_hypen_pos_list = pos_tup_list(remove_hypens_words(s))
        verb_list = verb_list_found(wo_hypen_pos_list)
        if (verb_list != []):
            upd_pos_list = remove_POS_matches(sentence_pos_list,
                                              verb_list,
                                              'verb')
            return (sentence_pos_list, upd_pos_list, verb_list)
        else:
            return ("ERROR", sentence_pos_list)


    def normal_verb_removal(s):
        #normal verb removal:
        sentence_pos_list = pos_tup_list(s)
        verb_list = verb_list_found(sentence_pos_list)
        if (verb_list != []):
            upd_pos_list = remove_POS_matches(sentence_pos_list,
                                              verb_list,
                                              'verb')
            return (sentence_pos_list, upd_pos_list, verb_list)
        else:
            return ("ERROR", sentence_pos_list)

    if (hypen_in_sentence(st) == False):
        return normal_verb_removal(st)
    else:
        return hypen_verb_removal(st)

from nlpSpacy import *

#removes verbs from a sentence
def verb_removal(st):
    #returns a list of words that are consecutive verbs
    def consec_verb_list(lst):
        for i in range(len(lst)):
            if lst[i][2] == "VERB":
                verb_tup_lst = [lst[i]]
                for p in range(i+1,len(lst)):
                    if lst[p][2] == "VERB":
                        verb_tup_lst.append(lst[p])
                    else:
                        return verb_tup_lst
        return []

    #returns a string with all the hypenated words removed
    def remove_hypens_words(st):
        #removes word duplicates in a list
        def remove_duplicates(lst):
            word_dict = {}
            for i in range(len(lst)):
                word = lst[i]
                if word_dict.get(word) == None:
                    word_dict[word] = word
            return list(word_dict.keys())

        regex = re.compile(r'\w+\-\w+\-\w+|\w+.\-.\w+.\-.\w+|\w+\-\w+|\w+.\-.\w+')
        matches_lst = remove_duplicates(regex.findall(st)) #this is essential
        while matches_lst != []:
            word = matches_lst.pop()
            st = delete_words_string(st,word)
        return st

    #removes verbs from sentences wuth hypens
    def hypen_verb_removal(s):
        complete_pos_list = pos_tup_list(s)
        wo_hypen_pos_list = pos_tup_list(remove_hypens_words(s))
        verb_list_found = consec_verb_list(wo_hypen_pos_list)
        if verb_list_found != []:
            updated_pos_list = remove_POS_matches(complete_pos_list, verb_list_found, 'verb')
            return (complete_pos_list, updated_pos_list, verb_list_found)
        else:
            return ("ERROR",complete_pos_list)

        #normal verb removal:
    def normal_verb_removal(s):
        complete_pos_list = pos_tup_list(s)
        verb_list_found = consec_verb_list(complete_pos_list)
        if verb_list_found != []:
            updated_pos_list = remove_POS_matches(complete_pos_list, verb_list_found, 'verb')
            return (complete_pos_list, updated_pos_list, verb_list_found)
        else:
            return ("ERROR",complete_pos_list)

    if hypen_in_sentence(st) == False:
        return normal_verb_removal(st)
    else:
        return hypen_verb_removal(st)

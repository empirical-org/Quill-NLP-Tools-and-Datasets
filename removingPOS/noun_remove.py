from nlpSpacy import *

def noun_removal(s):
    #this function assumes that there is a hypen in the string and returns the span of the first hypen match
    def hypen_match_range(s):
        regex = re.compile(r'\w+\-\w+\-\w+|\w+.\-.\w+.\-.\w+|\w+\-\w+|\w+.\-.\w+')
        check_found = regex.search(s)
        if check_found != None:
            return check_found.span()
        else:
            return None
    #returns true if the tuple is a noun
    def noun_bool(tup):
        word_pos = tup[2]
        word_dep = tup[1]
        if  word_pos == 'NOUN' or word_pos == 'PRON' or word_pos == 'PROPN' or word_dep == 'poss' or word_pos == 'NUM':
            return True
        else:
            return False

    #returns a list of the tuples that were removed that are of noun type
    def consec_noun_list(lst): #add case for numbers wehre noun before   ('On', 'prep', 'ADP') ('July', 'pobj', 'PROPN') ('21', 'nummod', 'NUM') ('the', 'det', 'DET')
        consec_lst = []
        indexes_lst = []
        for index in range(len(lst)):
            if noun_bool(lst[index]) == True:
                consec_lst.append(lst[index])
                indexes_lst.append(index)
                for i in range(index + 1, len(lst)):
                    if lst[i][0] == '.' and i != len(lst)-1: #making sure that the '.' found is not the period of the sentence
                        if noun_bool(lst[i+1]) == True:
                            consec_lst.append(lst[i])
                            indexes_lst.append(i)
                    elif lst[i][0][0] == "\'" and lst[i][2] != "VERB": #takes into account possesive nouns (Catherine's)
                        consec_lst.append(lst[i])
                        indexes_lst.append(i)
                    elif noun_bool(lst[i]) == True:
                        consec_lst.append(lst[i])
                        indexes_lst.append(i)
                    else:
                        return (consec_lst,indexes_lst)
        return []

    def normal_noun_removal(string): #here include hypen noun removal
        orig_sent_arr = pos_tup_list(string)
        noun_list_found = consec_noun_list(orig_sent_arr)
        if noun_list_found != []:
            noun = make_str(noun_list_found[0]) #just turn thing into string
            # print("This was the noun found: " + noun)
            sentence_wo_noun = delete_words_string(string,noun)
            return (sentence_wo_noun[0].upper()+sentence_wo_noun[1:],noun,tup_list_to_string(noun_list_found[0]),tup_list_to_string(orig_sent_arr))
        else:
            return ("ERROR",tup_list_to_string(orig_sent_arr))

    #removes nouns from a string that contains hypens
    def hypen_noun_removal(s):
        orig_tup = pos_tup_list(s)
        hypen_match_ran = hypen_match_range(s)
        substring = s[:hypen_match_ran[0]-1] #substring before the hypen word. The space before the hypen match is not included in substring
        token_pos_lst = pos_tup_list(substring)
        last_token = token_pos_lst[len(token_pos_lst)-1]
        if hypen_match_ran[0] > len(s)/2: #meaning the hypen is at the very end, noun must be before this
            return normal_noun_removal(s)
        elif last_token[2] != 'NOUN' and last_token[2] != 'PRON' and last_token[2] != 'PROPN' and last_token[2] != "PUNCT" and last_token[1] != 'case' and last_token[1] != 'poss':
            substring_rem = normal_noun_removal(substring) #finding any nouns before the hypenated word
            if substring_rem[0] != 'ERROR':
                noun_removed = substring_rem[1]
                sentence_noun_removed = delete_words_string(s, noun_removed)
                return (sentence_noun_removed[0].upper()+sentence_noun_removed[1:],noun_removed,substring_rem[2],substring_rem[3])
            else:
                return ('ERROR',tup_list_to_string(orig_tup))
        else:
            return ('ERROR',tup_list_to_string(orig_tup))

    if hypen_in_sentence(s) == False:
        return normal_noun_removal(s)
    else:
        return hypen_noun_removal(s)

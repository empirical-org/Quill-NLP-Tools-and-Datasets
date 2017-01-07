from nlpSpacy import *

def noun_removal(s):
    '''Removes the first noun or group of nouns in the string.

    Nouns are removed by looking at the part of speech (POS) of each word in
    the string and the word depency. Spacy is used throughout this code and
    must be downloaded.

    Args:
        s: A string that is a complete sentence.
    Returns:

    example:

    '''

    #Finds the exact beginning and ending position of a hypenated word in a string
    def hypen_match_range(s):
        regex = re.compile(r'\w+\-\w+\-\w+|\w+.\-.\w+.\-.\w+|\w+\-\w+|\w+.\-.\w+')
        check_found = regex.search(s)
        if check_found != None:
            return check_found.span()
        else:
            return None

    #Determines whether a tuple, with a word as the first input in tuple, is a noun
    def noun_bool(tup):
        word_pos = tup[2]
        word_dep = tup[1]
        if  word_pos == 'NOUN' or word_pos == 'PRON' or word_pos == 'PROPN' or word_dep == 'poss' or word_pos == 'NUM':
            return True
        else:
            return False

    #Returns a tuple where the first argument is a list of tuples that are nouns and
    #the second argument is a list of indexes of all the tuples found from the original
    #list
    def consec_noun_list(lst):
        consec_lst = []
        indexes_lst = []
        for index in range(len(lst)):
            if noun_bool(lst[index]) == True:
                consec_lst.append(lst[index])
                indexes_lst.append(index)
                for i in range(index + 1, len(lst)):
                    if lst[i][0] == '.' and i != len(lst)-1:
                        if noun_bool(lst[i+1]) == True:
                            consec_lst.append(lst[i])
                            indexes_lst.append(i)
                    elif lst[i][0][0] == "\'" and lst[i][2] != "VERB":
                        consec_lst.append(lst[i])
                        indexes_lst.append(i)
                    elif noun_bool(lst[i]) == True:
                        consec_lst.append(lst[i])
                        indexes_lst.append(i)
                    else:
                        return (consec_lst,indexes_lst)
        return []

    #Removes a noun or nouns from a string that is a sentence and contains no hypens
    def normal_noun_removal(string): #here include hypen noun removal
        complete_pos_list = pos_tup_list(string)
        noun_match = consec_noun_list(complete_pos_list)
        if noun_match != []:
            updated_pos_list = remove_POS_matches(complete_pos_list,noun_match[1],"noun")
            return(complete_pos_list,updated_pos_list,noun_match)
            # return(complete_pos_list,updated_pos_list,noun_match[0])
        else:
            return ("ERROR",complete_pos_list)

    #removes nouns from a string that is a sentence and contains hypens
    def hypen_noun_removal(s):
        complete_pos_list = pos_tup_list(s)
        hypen_match_range = hypen_match_range(s)
        substring = s[:hypen_match_range[0]-1] #substring before the hypen word. The space before the hypen match is not included in substring
        substring_pos_list = pos_tup_list(substring)
        substring_last_word = substring_pos_list[len(substring_pos_list)-1]
        if hypen_match_range[0] > len(s)/2: #meaning the hypen is at the very end, noun must be before this
            return normal_noun_removal(s)
        elif noun_bool(substring_last_word[2]) == False and substring_last_word[2] != "PUNCT" and substring_last_word[1] != 'case':
            substring_noun_removal = normal_noun_removal(substring) #finding any nouns before the hypenated word
            if substring_noun_removal[0] != 'ERROR':
                updated_pos_list = remove_POS_matches(complete_pos_list, substring_noun_removal[2][1], "noun") #removed nouns matched
                return(complete_pos_list,updated_pos_list,substring_noun_removal[2][0])
            else:
                return ('ERROR',complete_pos_list)
        else:
            return ('ERROR',complete_pos_list)

    if hypen_in_sentence(s) == False:
        return normal_noun_removal(s)
    else:
        return hypen_noun_removal(s)

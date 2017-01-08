'''                                                                    
The main function in this file is called noun_removal and it removes
the first noun or group of nouns in a string. A string in this function
is a complete and correct sentence. This means it contains all of the
necessary requirements that a sentence needs to be correct.

The function uses several helper function in order to remove the first
noun or group of nouns. The function also relies on the library called
spacy, which you can learn more about here: https://spacy.io/. Nouns in
a sentence are removed by looking at the part of speech (pos) of each
word and by looking at the dependencies between words in a sentence. I
import all of the functions from a file called nlpSpacy in order to
keep this file clean and only noun focused. The functions in nlpSpacy
break down an arbitary string and provide very useful information to
remove a specific pos, in this file we only remove nouns.

Args:
    s: A string that is a complete sentence. I will refer to the string
    as a sentence below.
Returns:
    A tuple with three inputs:
    The first input is list of tuples describing all of the words in
    the sentence. Each tuple in this list contains the word,
    dependency, and pos for every word in the sentence, note that
    punctuation is also considered a word.
    The second input contains a similar list as the first input in the
    return statement, but it does not contain the first noun or group of
    nouns in the sentence.
    The third input is a tuple with two arguments. The first argument is
    a list of tuples that contain the noun or group of nouns found. The
    second argument is a list that contains the respective index for
    each noun found.
'''
from nlpSpacy import *

def noun_removal(s):
    def hypen_word_range(s):
        #Finds the exact beginning and ending position of a hypenated word in a string
        reg = re.compile(r'\w+\-\w+\-\w+|\w+.\-.\w+.\-.\w+|\w+\-\w+|\w+.\-.\w+')
        check_found = reg.search(s)
        if check_found != None:
            return check_found.span()
        else:
            return None

    def is_noun(tup):
        #Determines whether a tuple, with a word as the first input in tuple, is a noun
        word_pos = tup[2]
        word_dep = tup[1]
        if  (word_pos == 'NOUN' or
             word_pos == 'PRON' or
             word_pos == 'PROPN'or
             word_dep == 'poss' or
             word_pos == 'NUM'):
            return True
        else:
            return False

    def noun_list_found(lst):
        #Returns a tuple where the first argument is a list of tuples that are nouns and
        #the second argument is a list of indexes of all the tuples found from the original
        #list
        consec_lst = []
        indexes_lst = []
        for index in range(len(lst)):
            if (is_noun(lst[index])):
                consec_lst.append(lst[index])
                indexes_lst.append(index)
                for i in range(index + 1, len(lst)):
                    if (lst[i][0] == '.' and i != len(lst)-1):
                        if (is_noun(lst[i+1])):
                            consec_lst.append(lst[i])
                            indexes_lst.append(i)
                    elif (lst[i][0][0] == "\'" and lst[i][2] != "VERB"):
                        consec_lst.append(lst[i])
                        indexes_lst.append(i)
                    elif (is_noun(lst[i])):
                        consec_lst.append(lst[i])
                        indexes_lst.append(i)
                    else:
                        return (consec_lst,indexes_lst)
        return []

    def normal_noun_removal(string):
        #Removes a noun or nouns from a string that is a sentence and contains no hypens
        sentence_pos_lst = pos_tup_list(string)
        noun_match = noun_list_found(sentence_pos_lst)
        if (noun_match != []):
            upd_pos_list = remove_POS_matches(sentence_pos_lst,
                                                  noun_match[1],
                                                  "noun")
            return(sentence_pos_lst, upd_pos_list, noun_match)
        else:
            return ("ERROR", sentence_pos_lst)

    def hypen_noun_removal(s):
        #removes nouns from a string that is a sentence and contains hypens
        sentence_pos_lst = pos_tup_list(s)
        hypen_match_range = hypen_word_range(s)
        substring = s[:hypen_match_range[0]-1] #substring before the hypen word
        subs_pos_list = pos_tup_list(substring)
        subs_last_word = subs_pos_list[len(subs_pos_list)-1]
        if (hypen_match_range[0] > len(s)/2):
            return normal_noun_removal(s)
        elif (is_noun(subs_last_word[2]) == False and
              subs_last_word[2] != "PUNCT" and
              subs_last_word[1] != 'case'):
            subs_noun_removal = normal_noun_removal(substring)
            if (subs_noun_removal[0] != 'ERROR'):
                upd_pos_list = remove_POS_matches(sentence_pos_lst,
                                                  subs_noun_removal[2][1],
                                                  "noun")
                return(sentence_pos_lst,
                       upd_pos_list,
                       subs_noun_removal[2][0])
            else:
                return ('ERROR',sentence_pos_lst)
        else:
            return ('ERROR',sentence_pos_lst)

    if (hypen_in_sentence(s) == False):
        return normal_noun_removal(s)
    else:
        return hypen_noun_removal(s)

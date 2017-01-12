'''                                                                    |
The main function in this file is called verb_removal and it removes
the first verb or group of consecutive verbs in a string. A string in
this function is a complete and correct sentence. This means it contains
all of the necessary requirements that a sentence needs to be correct.

The function uses several helper function in order to remove the first
verb or first group of verbs. The function also relies on the library
called spacy, which you can learn more about here: https://spacy.io/.
Verbs are removed by looking at the part of speech (pos) of each
word and by looking at the dependencies between words in a sentence.

All of the helper functions in the main function are used to identify
the first verb or group of verbs in a sentence. If a sentence contains
hypenated words, then I remove all of the hypenated words from the
string and remove verbs from this updated string. Spacy seperates
hypenated words into three seperate words, including punctuation, and
it is best to remove hypenated words that might be incorrectly
classified by Spacy as verbs.

Args:
    st: A string that is a complete sentence.
Return:
    A tuple with three inputs:
    The first input is list of tuples describing all of the words,
    including punctuation marks, in a sentence. Each tuple in this
    list contains a word, its dependency, and its pos. The second input
    contains a similar list as the first input in the return statement,
    but it does not contain the verb match found in the sentence. The
    third input is lst of the verb match found.
'''
from nlpSpacy import *

def verb_removal(st):
    def verb_list_found(lst):
        #Returns a lst of tuples that describe the first verb or group
        #of verbs found
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
        #Returns a string with all the hypenated words removed
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
        #This function removes verbs from a sentence with hypens.
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
        #Removes verbs from strings without hypenated words.
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

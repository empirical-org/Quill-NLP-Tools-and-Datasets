'''
This file contains functions used heavily in the following files:
noun_remove.py, verb_remove.py, and noun_verb_remove.py. Please
note that most of the functions below rely on the library imported
called Spacy (https://spacy.io/). Also, in the functions below I will
refer to pos several times, it stands for part of speech. I will
explain each function in detail below:

pos_tup_list(s):
This function takes in a string and it returns a list
of tuples that describes each word and punctuation mark in the string.
Args:
    s: A string that is a complete sentence.
Returns:
    This function returns a list of tuples, where each tuples contains
    three inputs. Each word and punctuation mark in s is given its
    own tuple. The first input in the tuple is the word or punctuation
    mark, the second input is the word dependency, and the third input
    is the pos of the word or punctuation mark.

-----------------------------------------------------------------------
For the following functions lst is a list of tuples. Each tuple has
three inputs. The first input is a word or punctuation mark, the second
input is the dependecy of the word, and the third input is the pos of
the word. The lst is usually a sentence or a group of words. For
example, the following sentence "My family went hiking" would be
represented as:
[('My', 'poss', 'ADJ'), ('family', 'nsubj', 'NOUN'),
('went', 'ROOT', 'VERB'), ('hiking', 'advcl', 'NOUN'),
('.', 'punct', 'PUNCT')]
-----------------------------------------------------------------------

tup_list_to_string(lst):
This function turns a list of tuples directly into a list.
Args:
    lst: A list of tuples with three inputs.
Returns:
    The lst printed as a string, including the "[", "]" and all of the
    tuples as a string.

make_str(lst):
This function turns a list of tuples back into a sentence or group
of words.
Args:
    lst: A list of tuples with three inputs.
Returns:
    A string that is a complete sentence or a group of words.

delete_words_string(sentence,s):
This function delete a word from a string.
Args:
    sentence: A string that is a sentence.
    s: A word or words that need to be removed from sentence.
Returns:
    A string that contains the same words as sentence, but excludes
    the words in s.

hypen_in_sentence(s):
This function returns a true if there is a hypen in the string,
otherwise it returns false.
Args:
    s: A string
Returns:
    A boolean describing whether there is a hypen in the string

remove_POS_matches(ls_orig,ls_remove,removal_type):
This returns a lst that is very similar to ls_orig, but does not
contain the tuples in the lst ls_remove.
Args:
    ls_orig: This is in the same format as lst and is a complete
             sentence.
    ls_remove: This is in the same format as lst and it contains
               words that are nouns or verbs.
    removal_type: This specifies what kind of removal needs to be
                  done. Possible options are "noun" and "verb"
Returns:
    A lst that is an updated version of ls_orig because it does not
    contain tuples in ls_remove.
'''
import re
import spacy
nlp = spacy.load('en')

def pos_tup_list(s):
    processed = nlp(s)
    tup_list = []
    for token in processed:
        tup_list.append((str(token),token.dep_,token.pos_))
    return tup_list

def tup_list_to_string(lst):
    return ', '.join('(' + ', '.join(i) + ')' for i in lst)

def make_str(lst):
    s = ''
    for i in range(len(lst)):
        curr_word = lst[i][0]
        if (lst[i][2] != 'PUNCT' and
            lst[i][1] != "case" and
            lst[i-1][0] != '-' and
            lst[i][0] != '%'):
            s += ' ' + curr_word
        else:
            s += curr_word
    if s[0] == ' ':
        return s[1:]
    else:
        return s

def delete_words_string(sentence,s):
    def word_at_beginning(sentence,s):
        #Returns bool describing if matched word is in the beginning
        regex = re.compile(s)
        match_span = regex.search(sentence).span()
        if (match_span[0] == 0):
            return True
        else:
            return False
    regex1 = re.compile(s+"\'")
    if (regex1.search(sentence) != None):
        return sentence.replace(s,"")
    elif (word_at_beginning(sentence,s) == True):
        return sentence.replace(s+' ','')
    else:
        return sentence.replace(' '+s,'')

def hypen_in_sentence(s):
    regex = re.compile(r'\-')
    match_bool = regex.search(s)
    if (match_bool != None):
        return True
    else:
        return False

def remove_POS_matches(ls_orig,ls_remove,removal_type):
    upd_tup_lst = []
    if (removal_type == "noun"):
        for i in range(len(ls_orig)):
            if (i not in ls_remove):
                upd_tup_lst.append(ls_orig[i])
    else:
        index_ls_remove = 0
        for tup in ls_orig:
            if (index_ls_remove == len(ls_remove)):
                upd_tup_lst.append(tup)
            elif (tup == ls_remove[index_ls_remove]):
                index_ls_remove += 1
            else:
                upd_tup_lst.append(tup)
    return upd_tup_lst

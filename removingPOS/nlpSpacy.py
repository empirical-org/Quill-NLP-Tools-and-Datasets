import re
import spacy
nlp = spacy.load('en')

'''
Important Notes:
POS = Part of Speech

TO-DO:
For each newly created file start creating final text files:
First file output: original list of POS || updated list POS || word removed
Second file output to help people understand: Original sentence: , Word removed: , Updated sentence: , POS original,POS removed words, POS updated

Write to files and keep as type list instead of string:
Look into import pickle

Include comments in all of the python files. Use Google's python comment guidelines:
Review comments in noun_remove
Create comments for verb_remove
Create comments for noun_verb_remove

Random but important:
take into account ,, and "  "
have to go through and update any 're 's (etc.) that are actually verbs
'''

#turns string into a list of tuples, where each tuple contains a word, word depency, and word POS
def pos_tup_list(s):
    processed = nlp(s)
    tup_list = []
    for token in processed:
        tup_list.append((str(token),token.dep_,token.pos_))
    return tup_list

#changes a list of tuples to a string so that it can be printed
def tup_list_to_string(lst):
    return ', '.join('(' + ', '.join(i) + ')' for i in lst)

#turns a list of tuples into a sentence or words
def make_str(lst):
    s = ''
    for i in range(len(lst)):
        curr_word = lst[i][0]
        if lst[i][2] != 'PUNCT' and lst[i][1] != "case" and lst[i-1][0] != '-' and lst[i][0] != '%':
            s += ' ' + curr_word
        else:
            s += curr_word
    if s[0] == ' ':
        return s[1:]
    else:
        return s

#deletes a word from a sentence
def delete_words_string(sentence,s):
    #returns bool describing if matched word is in the beginning
    def word_at_beginning(sentence,s):
        regex = re.compile(s)
        match_span = regex.search(sentence).span()
        if match_span[0] == 0:
            return True
        else:
            return False

    regex1 = re.compile(s+"\'")
    if regex1.search(sentence) != None:
        return sentence.replace(s,"")
    elif word_at_beginning(sentence,s) == True:
        return sentence.replace(s+' ','')
    else:
        return sentence.replace(' '+s,'')

#returns true if a hypen is found in a sentence
def hypen_in_sentence(s):
    regex = re.compile(r'\-')
    match_bool = regex.search(s)
    if match_bool != None:
        return True
    else:
        return False

#this returns a list of tuples that are not in the second argument
def remove_tups_lst(ls_orig,ls_remove,removal_type):
    upd_tup_lst = []
    if removal_type == "noun":
        for i in range(len(ls_orig)):
            if i != ls_remove[0]:
                upd_tup_lst.append(ls_orig[i])
            else:
                ls_remove.pop(0)
    else:
        for tup in ls_orig:
            if tup not in ls_orig:
                upd_tup_lst.append(tup)
    return upd_tup_lst

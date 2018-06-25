'''
Most of the functions in this file write information to other files. The
functions make use of noun_remove.py, verb_remove.py, noun_verb_remove.py,
and conjunction_remove.py to remove nouns, verbs, or subordinate
conjunctions from sentences. Each function below reads textfile data
from the specified file located in the folder called orginalSentences
and processes each line. I will explain each function in detail below:

make_upd_sentence(s,match_found,removal_type):
This sentence removes any words from a string and outputs a string
that looks like a sentence, meaning the first character in the
string is capitalized and there is a period at the end.
Args:
    s: A string that is a sentence.
    match_found: A substring that needs to be removed from s.
    removal_type: This argument is only used by the function
                  noun_verb_textfile.
Return:
    This returns an updated string with the same words as s, but with
    words in match found removed.

For example, if the string is "My family loves hiking." and the string we
want to remove is "My family" then the function returns "Loves hiking."
-----------------------------------------------------------------------
* Refer to nlpSpacy.py to see what lst is. lst will be used here.
The functions below handle writing information to three seperate files.
Information is written to two textfile and a file ending in .p, which
uses pickle.
The textfile called detailedRemoval.txt is for a human to
understand how each line was line was processed. Each line in the
detailedRemoval.txt is in the following format:
Original sentence: | Word removed: | Updated sentence: |
POS lst for sentence | POS lst of removed words| POS lst of updated sentence
The information written into the file ending in .p uses serialization. For
each line I dump tuples into the file p. Each tuple has three inputs and
contains information for a sentence that was processed. The first argument
is the pos lst of the line being processed. The second input is a pos lst
of the original sentence, but with the pos matches removed. The third
input is a lst of the words that were removed.
The third file is called errorSentences.txt and contains the lst of
sentences that could not be processed.
-----------------------------------------------------------------------
The names of the functions below describe the kind of pos removal that
was done. All of the outputs for the functions below follow the format
described above.
'''
import pickle
from nlpSpacy import *
from noun_remove import noun_removal
from verb_remove import verb_removal
from noun_verb_remove import noun_verb_removal
from conjunction_remove import subordinate_removal

def make_upd_sentence(s,match_found,removal_type):
    sentence_wo_match = delete_words_string(s,match_found)
    if (removal_type == "noun_verb"):
        return sentence_wo_match
    else:
        return sentence_wo_match[0].upper() + sentence_wo_match[1:]

def noun_textfile():
    noun_dir = "./updatedSentences/nounSentences/"
    with open(noun_dir + "errorSentences.txt","w") as err, \
         open(noun_dir + "detailedRemoval.txt","w") as det, \
         open(noun_dir + "nounRemoval.p","wb") as tup_write, \
         open("./originalSentences/nounScreening.txt","r") as f:
            for line in f:
                line = line.rstrip("\n")
                line_wo_n = noun_removal(line)
                if (line_wo_n[0] != "ERROR"):
                    noun_pos = line_wo_n[2][0]
                    pickle.dump((line_wo_n[0], #serialization
                                 line_wo_n[1],
                                 noun_pos),
                                tup_write)
                    n_found = make_str(noun_pos).rstrip("\n")
                    det.write(line + " ||| "
                              + n_found + " ||| "
                              + make_upd_sentence(line,n_found,"").rstrip("\n") + " ||| "
                              + tup_list_to_string(line_wo_n[0]) + " ||| "
                              + tup_list_to_string(noun_pos) + " ||| "
                              + tup_list_to_string(line_wo_n[1]) + "\n")
                else:
                    err.write(line + ' ||| '
                              + tup_list_to_string(line_wo_n[1]) + "\n")

def verb_textfile():
    verb_dir = "./updatedSentences/verbSentences/"
    with open(verb_dir + "errorSentences.txt","w") as err, \
         open(verb_dir + "detailedRemoval.txt","w") as det, \
         open(verb_dir + "verbRemoval.p","wb") as tup_write, \
         open("./originalSentences/verbScreening.txt","r") as f:
            for line in f:
                line = line.rstrip("\n")
                line_wo_v = verb_removal(line)
                if (line_wo_v[0] != "ERROR"):
                    pickle.dump(line_wo_v, tup_write)
                    verb_pos = line_wo_v[2]
                    v_found = make_str(verb_pos)
                    det.write(line + " ||| "
                              + v_found.rstrip("\n") + " ||| "
                              + make_upd_sentence(line, v_found,"").rstrip("\n") + " ||| "
                              + tup_list_to_string(line_wo_v[0]) + " ||| "
                              + tup_list_to_string(verb_pos) + " ||| "
                              + tup_list_to_string(line_wo_v[1]) + "\n")
                else:
                    err.write(line + " ||| "
                              + tup_list_to_string(line_wo_v[1]) + "\n")

def noun_verb_textfile():
    nv_dir = "./updatedSentences/nounverbSentences/"
    with open(nv_dir + "errorSentences.txt","w") as err, \
         open(nv_dir + "detailedRemoval.txt","w") as det, \
         open(nv_dir + "nounverbRemoval.p","wb") as tup_write, \
         open("./originalSentences/nounverbScreening.txt","r") as f:
            for line in f:
                line = line.rstrip("\n")
                line_wo_nv = noun_verb_removal(line)
                if (line_wo_nv[0] != "ERROR"):
                    n_pos_lst = line_wo_nv[2][0]
                    v_pos_lst = line_wo_nv[2][1]
                    pickle.dump((line_wo_nv[0],
                                 line_wo_nv[1],
                                 n_pos_lst
                                 + v_pos_lst),
                                tup_write)
                    noun_str = make_str(n_pos_lst).rstrip("\n")
                    verb_str = make_str(v_pos_lst).rstrip("\n")
                    rem_noun = make_upd_sentence(line, noun_str,"noun_verb")
                    remove_verb = make_upd_sentence(rem_noun, verb_str,"")
                    det.write(line + " ||| "
                              + noun_str + ' ' + verb_str + " ||| "
                              + remove_verb.rstrip("\n") + " ||| "
                              + tup_list_to_string(line_wo_nv[0]) + " ||| "
                              + tup_list_to_string(n_pos_lst + v_pos_lst) + " ||| "
                              + tup_list_to_string(line_wo_nv[1]) + "\n")
                else:
                    err.write(line + " ||| "
                              + tup_list_to_string(line_wo_nv[1]) + "\n")

def subordinate_textfile():
    sub_dir = "./updatedSentences/conjunctionSentences/"
    with open(sub_dir + "errorSentences.txt","w") as err, \
         open(sub_dir + "detailedRemoval.txt","w") as det, \
         open(sub_dir + "conjunctionRemoval.p","wb") as tup_write, \
         open("./originalSentences/subScreening.txt","r") as f:
            for line in f:
                line = line.rstrip("\n")
                line_wo_sub = subordinate_removal(line)
                if (line_wo_sub != "ERROR"):
                    pickle.dump(line_wo_sub, tup_write)
                    sub_conj_lst = line_wo_sub[2]
                    sub_found = make_str(sub_conj_lst)
                    det.write(line + " ||| "
                              + sub_found + " ||| "
                              + line.replace(sub_found,"") + " ||| "
                              + tup_list_to_string(line_wo_sub[0]) + " ||| "
                              + tup_list_to_string(sub_conj_lst) + " ||| "
                              + tup_list_to_string(line_wo_sub[1]) + "\n")
                else:
                    err.write(line + " ||| "
                              + tup_list_to_string(line_wo_sub[1]) + "\n")

#Here I am calling the functions written above.
noun_textfile()
verb_textfile()
noun_verb_textfile()
subordinate_textfile()

'''
Most of the functions in this file write information to other files. The
functions make use of noun_remove.py, verb_remove.py, noun_verb_remove.py,
and ____________ to remove nouns, verbs, or subordinate conjunctions from
sentences. Each function reads textfile data from the specified file
located in the folder called orginalSentences and processes each line. I
will explain each function in detail below:

make_upd_sentence(s,match_found,removal_type):
This function takes in a string and a list of tuples. It updates the
string by removing any words that are in the list of tuples. For
example, if thestring is "My family loves hiking." and the list of
tuples is [('family', 'nsubj', 'NOUN'), ('went', 'ROOT', 'VERB')] then
it returns "My hiking."
Args:
    s: A string that is a sentence.
    match_found: An lst of words to remove. Check the comments on
                 nlpSpacy.py to see what an lst is.
    removal_type: This is the kind of removal that needs to be made and
                  represents the pos of words found in match_found.
                  Possible words are "noun", and "verb".
Return:
    This returns an updated string with the same words as s, but with
    words in match found removed.
-----------------------------------------------------------------------
* Refer to nlpSpacy.py to see what lst is. lst will be used here.
The functions below handle writing information to two seperate files.
Information is writtten to a textfile and another file ending in .p,
which uses pickle. The textfile is for a person to understand how each
line is processed. Each line in the textfile is in the following format:
 Original sentence: | Word removed: | Updated sentence: |
 POS lst for sentence | POS lst of removed words| POS lit of updated sentence
The information written into the file ending in .p uses serialization.
Here I write tuples, with three inputs, directly to the file. Each tuple
contains information for a sentence that was processed. The first argument
is the pos lst of the line being processed. The second input is a pos lst
of the original sentence, but does not contain the speficied pos being
removed. The third input is a lst of the words that were removed. I use
serialization here so that others could easily reuse the final outputs
of the data.
-----------------------------------------------------------------------
noun_textfile():
This function reads from a texfile called nounScreening.txt in the folder
originalSentences. It processes each line and removes the first noun or
group of consecutive nouns found in the line. Each line is a complete
sentence. Once a sentence is processed, it writes information to two
seperate files.
Args: None
Return: Nothing is returned, instead nformation is written to other files.

verb_textfile():
This function reads from a texfile called verbScreening.txt in the folder
originalSentences. It processes each line and removes the first verb or
group of consecutive verbs found in the line. Each line is a complete
sentence. Once a sentence is processed, it writes information to two
seperate files.
Args: None
Return: Nothing is returned, instead nformation is written to other files.

noun_verb_textfile():
This function reads from a texfile called nounverbScreening.txt in the folder
originalSentences. It processes each line and removes the first noun or
group of consecutive nouns and the first verb or group of consecutive verbs
found in the line. Each line is a complete sentence. Once a sentence is
processed, it writes information to the two seperate files.
Args: None
Return: Nothing is returned, instead nformation is written to other files.
'''
import pickle
from nlpSpacy import *
from noun_remove import noun_removal
from verb_remove import verb_removal
from noun_verb_remove import noun_verb_removal
from conjunction_remove import subordinate_removal

def load(filename):
    with open(filename, "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break

# items = load('./updatedSentences/nounSentences/nounRemoval.p')
# lst = []
# for i in items:
#     lst.append(i)
# print("At this point i should already have a list: ")
# print(len(lst))
# for tup in lst:
#     print(tup)


def make_upd_sentence(s,match_found,removal_type):
    sentence_wo_noun = delete_words_string(s,match_found)
    if (removal_type == "noun_verb"):
        return sentence_wo_noun
    else:
        return sentence_wo_noun[0].upper() + sentence_wo_noun[1:]

def noun_textfile():
    noun_dir = "./updatedSentences/nounSentences/"
    with open(noun_dir + "errorSentences.txt","w") as err, \
         open(noun_dir + "./updatedSentences/nounSentences/detailedRemoval.txt","w") as det, \
         open(noun_dir + "./updatedSentences/nounSentences/nounRemoval.p","wb") as tup_write, \
         open("./originalSentences/testingFile.txt","r") as f:
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
         open("./originalSentences/testingFile.txt","r") as f:
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
         open("./originalSentences/testingFile.txt","r") as f:
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
         open(sub_dir + "nounverbRemoval.p","wb") as tup_write, \
         open("./originalSentences/testingFile.txt","r") as f:
            for line in f:
                line = line.rstrip("\n")
                line_wo_sub = subordinate_removal(line)
                if (line_wo_sub != "ERROR"):
                    pickle.dump(line_wo_sub, tup_write)
                    sub_conj_lst = line_wo_sub[2]
                    sub_found = make_str(sub_conj_lst)
                    det.write(line + " ||| "
                              + sub_found + " ||| "
                              + make_upd_sentence(line,sub_found,"") + " ||| "
                              + tup_list_to_string(line_wo_sub[0]) + " ||| "
                              + tup_list_to_string(sub_conj_lst) + " ||| "
                              + tup_list_to_string(line_wo_sub[1]) + "\n")
                else:
                    err.write(line + " ||| "
                              + tup_list_to_string(line_wo_sub[1]) + "\n")

'''
The main function in this file is subordinate_removal(s). This function
handles sentences that contain subordinate conjunctions and removes
parts of these sentences. The function removes the subordinate
conjunctions in the following ways:
- If a subordinate conjunction is in the beginning of a sentence,
then it removes that word and all of the words following it until a
comma is reached. For example, in the sentence "After we went to the
park, Billy went swimming." the string "After we went to the park,"
would be removed. If a sentence starts with a subordinate conjunction,
but there is no comma in the sentence, then we do not remove anything
from the sentence.
- If a subordinate conjunction is in the middle of a sentence, then
that word till the end of the string is removed. For example, in the
sentence "I think we should go hiking after the football game." the
words "after the football game" would be removed.
Args:
    s: A string that is a complete sentence.
Returns:
    A tuple with three inputs:
    The first input is list of tuples describing all of the words in
    the sentence. Each tuple in this list contains a word, which
    could also be a punctuation mark, a dependency, and a pos for the
    word. The second input contains a similar list as the first input,
    but it does not contain the subordinate conjunction substring match.
    The third input is list of tuples, similar to the list that was
    described earlier, that contains the subordinate conjunction matches
    found.
'''
import re
import spacy
nlp = spacy.load('en')
from nlpSpacy import pos_tup_list, remove_POS_matches

def subordinate_removal(s):
    def conjunct_lst_found(lst,type_find,conjunction):
        #this function returns a list of tuples that make up a
        #subordinate conjunction
        match_found = []
        if type_find == "Upper":
            match_found.append(lst[0])
            for i in range(1,len(lst)):
                word = lst[i][0]
                if (word != ","):
                    match_found.append(lst[i])
                else:
                    match_found.append(lst[i])
                    return match_found
        else:
            for i in range(0,len(lst)):
                word = lst[i][0]
                if word == conjunction:
                    match_found.append(lst[i])
                    for j in range(i+1,len(lst)-1):
                        match_found.append(lst[j])
                    return match_found

    def subordinate_remove(s):
        #this removes a subordinate conjunction from a string
        complete_pos_lst = pos_tup_list(s)
        conjunct_upper = re.compile('(After|Although|As|Because|Before|' \
                                    'If|Once|Since|Than|That|Though|' \
                                    'Unless|Until|When|Whenever|Where|' \
                                    'Whereas|Wherever|Whether|While|Why|' \
                                    'Even(?=\sif)|Even(?=\sthough)|' \
                                    'Provided(?=\sthat)|Rather(?=\sthan)|' \
                                    'So(?=\sthat))(?=\s)')
        conjunct_lower = re.compile('(?<=\s)(after|although|as|because|' \
                                    'before|if|once|since|than|that|though|' \
                                    'unless|until|when|whenever|where|' \
                                    'whereas|wherever|whether|while|why|' \
                                    'even(?=\sif)|even(?=\sthough)|' \
                                    'provided(?=\sthat)|rather(?=\sthan)|' \
                                    'so(?=\sthat))(?=\s)')
        match_upper = conjunct_upper.search(s)
        match_lower = conjunct_lower.search(s)
        if (match_upper != None and s.find(",") > -1):
            conjunc_found = conjunct_lst_found(complete_pos_lst,
                                               "Upper",
                                               "")
            upd_pos_list = remove_POS_matches(complete_pos_lst,
                                              conjunc_found,
                                              "")
            return (complete_pos_lst,upd_pos_list,conjunc_found)
        elif (match_lower != None):
            word_match = match_lower.group(0)
            conjunc_found = conjunct_lst_found(complete_pos_lst,
                                               "Lower",
                                               word_match)
            upd_pos_list = remove_POS_matches(complete_pos_lst,
                                              conjunc_found,
                                              "")
            return (complete_pos_lst,upd_pos_list,conjunc_found)
        else:
            return ("ERROR", complete_pos_lst)

    return subordinate_remove(s)

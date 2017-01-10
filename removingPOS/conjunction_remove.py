'''
-----------------------------------------------------------------------   |
update github with all of the changes you have made!!!
create a pull request with the branch you made and commited all changes
delete unnesessary folders from github


'''
import re
import spacy
nlp = spacy.load('en')
from nlpSpacy import pos_tup_list, remove_POS_matches

def subordinate_removal(s):
    def conjunct_lst_found(lst,type_find,conjunction):
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
        complete_pos_lst = pos_tup_list(s)
        conjunct_upper = re.compile('(After|Although|As|Because|Before|' \
                                    'If|Once|Since|Than|That|Though|' \
                                    'Unless|Until|When|Whenever|Where|' \
                                    'Whereas|Wherever|Whether|While|Why|' \
                                    'Even if|Even though|Provided that|' \
                                    'Rather than|So that|In order that)(?=\s)')
        conjunct_lower = re.compile('(?<=\s)(after|although|as|because|' \
                                    'before|if|once|since|than|that|though|' \
                                    'unless|until|when|whenever|where|' \
                                    'whereas|wherever|whether|while|why|' \
                                    'even if|even though|provided that|' \
                                    'rather than|so that|in order that)(?=\s)')
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

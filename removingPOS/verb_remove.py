from nlpSpacy import *

#removes verbs from a sentence
def verb_removal(st):
    #returns a list of words that are consecutive verbs
    def consec_verb_list(lst):
        for i in range(len(lst)):
            if lst[i][2] == "VERB":
                verb_tup_lst = [lst[i]]
                indexes_mached = [i]
                for p in range(i+1,len(lst)):
                    if lst[p][2] == "VERB":
                        verb_tup_lst.append(lst[p])
                        indexes_mached.append(p)
                    else:
                        return (verb_tup_lst,indexes_mached)
        return []

    #returns a string with all the hypenated words removed
    def remove_hypens_words(st):
        #removes word duplicates in a list
        def remove_duplicates(lst):
            word_dict = {}
            for i in range(len(lst)):
                word = lst[i]
                if word_dict.get(word) == None:
                    word_dict[word] = word
            return list(word_dict.keys())

        regex = re.compile(r'\w+\-\w+\-\w+|\w+.\-.\w+.\-.\w+|\w+\-\w+|\w+.\-.\w+')
        matches_lst = remove_duplicates(regex.findall(st)) #this is essential
        while matches_lst != []:
            word = matches_lst.pop()
            st = delete_words_string(st,word)
        return st

    def hypen_verb_removal(s):
        tup_sent_arr = pos_tup_list(s)
        st_wo_hypen_words = remove_hypens_words(s)
        tup_upd_st = pos_tup_list(st_wo_hypen_words)
        verb_list_found = consec_verb_list(tup_upd_st)
        if verb_list_found != []:
            verb = make_str(verb_list_found[0])
            sentence_wo_verb = delete_words_string(s,verb)
            return (sentence_wo_verb[0].upper()+sentence_wo_verb[1:],verb,tup_list_to_string(verb_list_found[0]),tup_list_to_string(tup_sent_arr))
        else:
            return ("ERROR",tup_list_to_string(tup_sent_arr))

    def normal_verb_removal(s):
        tup_sent_arr = pos_tup_list(s)
        verb_list_found = consec_verb_list(tup_sent_arr)
        if verb_list_found != []:
            verb = make_str(verb_list_found[0])
            sentence_wo_verb = delete_words_string(s,verb)
            return (sentence_wo_verb[0].upper()+sentence_wo_verb[1:],verb,tup_list_to_string(verb_list_found[0]),tup_list_to_string(tup_sent_arr))
        else:
            return ("ERROR",tup_list_to_string(tup_sent_arr))

    if hypen_in_sentence(st) == False:
        return normal_verb_removal(st)
    else:
        return hypen_verb_removal(st)

with open('./updatedSentences/verbSentences/testing.txt','w') as remov:
    with open('./originalSentences/verbScreening.txt','r') as file:
        for line in file:
            print(line)
            v_sentence_rem = verb_removal(line)
            if v_sentence_rem[0] != "ERROR":
                remov.write(line.rstrip('\n') + ' ||| ' + v_sentence_rem[2] + '\n' )
#

#THIS IS FOR VERBS
# with open('./updatedSentences/verbSentences/verbErrorSentences.txt','w') as error_v:
#     with open('./updatedSentences/verbSentences/verbCompleteSentences.txt','w') as v_complete:
#         with open('./updatedSentences/verbSentences/verbRemovedSentences.txt','w') as v_remov:
#             with open('./updatedSentences/verbSentences/verbRemovedClean.txt','w') as v_remov_clean:
#                 with open('./originalSentences/verbScreening.txt','r') as f:
#                     for line in f:
#                         v_sentence_rem = verb_removal(line)
#                         if v_sentence_rem[0] != "ERROR":
#                             v_complete.write(line)
#                             v_remov.write(v_sentence_rem[0] + ' ||| ' +  v_sentence_rem[1] + ' ||| ' + line)
#                             v_remov_clean.write(v_sentence_rem[0])
#                         else:
#                             error_v.write('ERROR ||| ' + line.rstrip('\n') + ' ||| ' + v_sentence_rem[1] + '\n')

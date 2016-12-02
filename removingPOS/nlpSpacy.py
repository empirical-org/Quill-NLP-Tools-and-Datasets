import unittest
import re
import spacy
nlp = spacy.load('en')

def consec_iden_ent_pos(lst,tup_index,f_check,s_check,t_check):
    for index in range(len(lst)):
        iden_tup = lst[index][tup_index]
        if iden_tup == f_check or iden_tup == s_check or iden_tup == t_check: #should i break somewhere here??
            consec_lst = [index]
            for i in range(index + 1, len(lst)):
                next_iden_found = lst[i][tup_index]
                if next_iden_found == f_check or next_iden_found == s_check or next_iden_found == t_check:
                    consec_lst.append(i)
                else:
                    return consec_lst
    return [] 

def dep_consec_iden(lst):
    reg = re.compile('.subj')
    for i in range(len(lst)):
        dep_tup = lst[i][2]
        reg_m = reg.match(dep_tup)
        if reg_m != None:
            return i
    return -1

def make_str(lst):
    s = ''
    f_str = lst[0][0]
    f_char = f_str[0]
    if f_char.islower():
        s += f_char.upper()
        s += f_str[1:]
    else:
        s += f_str
    for i in range (1,len(lst)):
        word = lst[i][0]
        if lst[i][3] != 'PUNCT' and lst[i][2] != "case":
            s += ' ' + word
        else:
            s += word
    return s

def delete_arr_elements(sent_lst,remove_lst):
    new_sent_list = []
    for i in range(len(sent_lst)):
        if i not in remove_lst:
            new_sent_list.append(sent_lst[i])
    return new_sent_list

def ent_noun_removal(s):
    processed = nlp(s)
    orig_sent_arr = []
    for token in processed:
        orig_sent_arr.append((str(token),token.ent_type_,token.dep_,token.pos_))
    consec_ent = consec_iden_ent_pos(orig_sent_arr,1,'PERSON','FACILITY','ORG')
    if consec_ent != []:
        upd_sent_arr = delete_arr_elements(orig_sent_arr, consec_ent)
        return make_str(upd_sent_arr)
    else:
        consec_dep = dep_consec_iden(orig_sent_arr)
        if consec_dep != -1:
            del orig_sent_arr[consec_dep]
            return make_str(orig_sent_arr)
        else:
            consec_pos = consec_iden_ent_pos(orig_sent_arr,3,'NOUN','PRON','PROPN')
            if consec_pos != []:
                upd_sent_arr = delete_arr_elements(orig_sent_arr, consec_pos)
                return make_str(upd_sent_arr)
            else:
                return "Sorry I can't check for this."

class removing_nouns(unittest.TestCase):
    def test(self):
        self.assertEqual(ent_noun_removal('Washington is my favorite place.'), 'Is my favorite place.')
        self.assertEqual(ent_noun_removal('I saw Catherine Yesenia and Karen walk the dog.'), 'I saw and Karen walk the dog.')
        self.assertEqual(ent_noun_removal('I saw Catherine Yesenia, and Karen walk the dog.'), 'I saw, and Karen walk the dog.')
        self.assertEqual(ent_noun_removal('I saw Catherine Washington and Karen walk the dog.'), 'I saw and Karen walk the dog.')
        self.assertEqual(ent_noun_removal('The cat loves pie.'), 'The loves pie.')
        self.assertEqual(ent_noun_removal('Kerry and Nando went hiking.'), 'And Nando went hiking.')
        self.assertEqual(ent_noun_removal('There are also research facilities operated through hospitals and private biotechnology companies.'), "There are also operated through hospitals and private biotechnology companies.")
        self.assertEqual(ent_noun_removal('He likes to eat.'), 'Likes to eat.')
        self.assertEqual(ent_noun_removal('Grand Teton National Park and the surrounding region host over 1000 species of vascular plants.'), 'And the surrounding region host over 1000 species of vascular plants.')
        self.assertEqual(ent_noun_removal('Of the primary schools, there are 162 regular, 14 special, 15 art, and 4 adult schools.'), 'Of the primary, there are 162 regular, 14 special, 15 art, and 4 adult schools.')
        self.assertEqual(ent_noun_removal('There is no extant literature in the English language in this era.'), 'There is no extant in the English language in this era.')
        self.assertEqual(ent_noun_removal("This fact, too, was widely criticized by the state's newspapers."), "This, too, was widely criticized by the state's newspapers.")
        self.assertEqual(ent_noun_removal("Within Black Moshannon State Park there is a State Park Natural Area protecting the bogs."), "Within there is a State Park Natural Area protecting the bogs.")
        self.assertEqual(ent_noun_removal("C Squadron, leading a brigade group, advanced towards Gambut on the morning of 23 November."), "C Squadron, leading a brigade group, advanced towards on the morning of 23 November.")
        self.assertEqual(ent_noun_removal("Let's go see the cake tree."), "Let go see the cake tree.") #but the output sentence is incorrect
        self.assertEqual(ent_noun_removal("There was also a death in neighboring Vermont."), "There was also a in neighboring Vermont.") #but the output sentence is incorrect

if __name__ == '__main__':
    unittest.main()

# ######### NEXT STEP: START WRITING TO TWO DIFFERENT FILES AND PRINT THINGS IN THE FORMAT DONALD WANTS
# #write to specific different files so can examine
# with open('./outSentences.txt','w') as f:
#     with open ('./sentences/fullSentencesNoun.txt','w') as noun:
#         with open ('./sentences/removedNoun.txt','w') as remov:
#             with open('./nounScreening.txt','r') as file:
#                 for line in file:
#                     processed_text = nlp(line)
#                     if subject_in_sentence(processed_text)[0] == True:
#                         noun.write(line)
#                         # do something here and remove noun function
#
#                     if subject_in_sentence(processed_text)[0] == False:
#                         f.write(line)
#
#
#


#
# def token_print(s):
#     pro = nlp(s)
#     for token in pro:
#         print(token,'\tent:',token.ent_type_,'\tdep:',token.dep_,'\tpos:',token.pos_)
#
# token_print("Dr. W. A. Claxton, chief of the Miami Department of Public Welfare, requested antitoxin, typhoid serum, and at least 200 tetanus serums.") #this sentence is coming up weird
# print("------------------------------------------------------")
# token_print("Alfred A. Loeb State Park, located on the banks of the Chetco, has three cabins and 48 camping sites.")
# print("------------------------------------------------------")
# token_print("Lt. Colonel Seth Reed and his family moved to the Erie area from Geneva, New York; they were Yankees from Uxbridge, Massachusetts.")

import csv

input_file = "quillgrammar/data/new_turk_data.txt"
jamspell_small_file = "jamspell_small.csv"
jamspell_medium_file = "jamspell_med.csv"
jamspell_big_file = "jamspell_big.csv"
jamspell_standard_file = "jamspell_standard.csv"
bing_file = "new_turk_data_bing.csv"

def get_corrections(f):
    corrected_sentences = []
    with open(f) as i:
        reader = csv.reader(i, delimiter="\t")
        for row in reader:
            corrected_sentences.append(row[0])
    return corrected_sentences


input_sentences = get_corrections(input_file)
jamspell_small_corrected = get_corrections(jamspell_small_file)
jamspell_medium_corrected = get_corrections(jamspell_medium_file)
jamspell_big_corrected = get_corrections(jamspell_big_file)
jamspell_standard_corrected = get_corrections(jamspell_standard_file)
bing_corrected = get_corrections(bing_file)

def compare(sentences1, sentences2, input_sentences):
    in_both_lists_same = 0
    in_both_lists_different = 0
    in_first_list_only = 0
    in_second_list_only = 0

    assert len(sentences1) == len(sentences2) == len(input_sentences)
    for sentence1, sentence2, input_sentence in zip(sentences1, sentences2, input_sentences):
        if sentence1 == sentence2 and sentence1 != input_sentence:
            in_both_lists_same += 1
        elif sentence2 == input_sentence and sentence1 != input_sentence:
            in_first_list_only += 1
        elif sentence1 == input_sentence and sentence2 != input_sentence:
            in_second_list_only += 1
        elif sentence1 != input_sentence and sentence2 != input_sentence and sentence1 != sentence2:
            in_both_lists_different += 1

    print("Caught by both, same correction:", in_both_lists_same)
    print("Caught by both, different correction", in_both_lists_different)
    print("Caught by first only:", in_first_list_only)
    print("Caught by second only:", in_second_list_only)

    
compare(jamspell_big_corrected, bing_corrected, input_sentences)
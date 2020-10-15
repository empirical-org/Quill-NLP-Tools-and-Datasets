import re

from quillopinion.opinioncheck import OpinionCheck


def test_opinioncheck1():
    sentence = "We need to eat less meat so climate change can hopefully be reduced."
    prompt = "We need to eat less meat so"

    check = OpinionCheck()
    feedback = check.check(sentence, prompt)

    assert len(feedback) == 1
    assert feedback[0].type == "Common Opinionated Phrases Keyword Check"
    assert feedback[0].start == 47
    assert feedback[0].end == 56


def test_opinioncheck2():
    sentence = "We need to end climate change so I'm thinking of eating less meat."
    prompt = "We need to end climate change so"

    check = OpinionCheck()
    feedback = check.check(sentence, prompt)

    assert len(feedback) == 1
    assert feedback[0].type == "First-person opinionated phrase keyword check"
    assert feedback[0].start == 33
    assert feedback[0].end == 45


def test_opinioncheck3():
    sentence = "We need to end climate change so you have to eat less meat."
    prompt = "We need to end climate change so"

    check = OpinionCheck()
    feedback = check.check(sentence, prompt)

    assert len(feedback) == 1
    assert feedback[0].type == "Second-Person Reference Keyword Check"
    assert feedback[0].start == 33
    assert feedback[0].end == 36


def test_opinioncheck4():
    sentence = "We need to end climate change so it would perhaps be better if people ate less meat."
    prompt = "We need to end climate change so"

    check = OpinionCheck()
    feedback = check.check(sentence, prompt)

    assert len(feedback) == 1
    assert feedback[0].type == "Using Perhaps"
    assert feedback[0].start == 42
    assert feedback[0].end == 49


def test_opinioncheck5():
    sentence = "We need to end climate change so all Americans should eat vegetables."
    prompt = "We need to end climate change so"

    check = OpinionCheck()
    feedback = check.check(sentence, prompt)

    assert len(feedback) == 1
    assert feedback[0].type == "Modal Check"
    assert feedback[0].start == 47
    assert feedback[0].end == 53


def test_opinioncheck6():
    sentence = "We need to end climate change because Barack Obama says all Americans should eat vegetables."
    prompt = "We need to end climate change because"

    check = OpinionCheck()
    feedback = check.check(sentence, prompt)

    assert len(feedback) == 0


def test_opinioncheck7():
    sentence = "We need to end climate change so all Americans ought to eat vegetables."
    prompt = "We need to end climate change so"

    check = OpinionCheck()
    feedback = check.check(sentence, prompt)

    assert len(feedback) == 1
    assert feedback[0].type == "Modal Check"
    assert feedback[0].start == 47
    assert feedback[0].end == 52


def test_opinioncheck8():
    sentence = "We need to end climate change because Barack Obama says all Americans ought to eat vegetables."
    prompt = "We need to end climate change because"

    check = OpinionCheck()
    feedback = check.check(sentence, prompt)

    assert len(feedback) == 0


def test_opinion_check_on_quill_data():
    input_file = "tests/data/opinion_sentences.txt"
    labeled_file = "tests/data/opinion_labeled.tsv"

    check = OpinionCheck()

    sentences = []
    with open(input_file) as i:
        for line in i:
            line = line.strip()
            sentences.append(line)

    opinion_labels = {}
    with open(labeled_file) as i:
        for line in i:
            line = line.strip().split("\t")
            if len(line) == 2:
                sentence, label = line

                opinion_labels[sentence] = label

    print("Labeled opinions:", len(list(opinion_labels.keys())))

    opinions = 0
    with open("opinion_output.tsv", "w") as o:
        for sentence in sentences:
            prompt = re.match(".*(because|, but|, so)", sentence)
            if prompt:
                prompt = prompt.group(0)
            else:
                prompt = ""

            feedback = check.check(sentence, prompt)
            if feedback:
                opinions += 1
                o.write(sentence + "\t" + ",".join([str(opinion) for opinion in feedback]) + "\n")
            else:
                o.write(sentence + "\t\n")

            if sentence in opinion_labels and not feedback:
                print("False negative (missed opinion):\t", sentence)
            if sentence not in opinion_labels and feedback:
                print("False positive (incorrectly identified as an opinion):\t", sentence)

    print(f"Opinions: {opinions}/{len(sentences)} = {opinions/len(sentences)}%")




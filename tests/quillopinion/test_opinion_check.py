import re

from quillopinion.opinioncheck import OpinionCheck


def test_opinioncheck1():
    sentence = "We need to eat less meat so climate change can hopefully be reduced."
    prompt = "We need to eat less meat so"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)

    assert len(feedback) == 1
    assert feedback[0].type == "Common Opinionated Phrases Keyword Check"
    assert feedback[0].start == 47
    assert feedback[0].end == 56


def test_opinioncheck2():
    sentence = "We need to end climate change so I'm thinking of eating less meat."
    prompt = "We need to end climate change so"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)

    assert len(feedback) == 1
    assert feedback[0].type == "First-person opinionated phrase keyword check"
    assert feedback[0].start == 33
    assert feedback[0].end == 45


def test_opinioncheck3():
    sentence = "We need to end climate change so you have to eat less meat."
    prompt = "We need to end climate change so"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)

    assert len(feedback) == 1
    assert feedback[0].type == "Second-Person Reference Keyword Check"
    assert feedback[0].start == 33
    assert feedback[0].end == 36


def test_opinioncheck4():
    sentence = "We need to end climate change so it would perhaps be better if people ate less meat."
    prompt = "We need to end climate change so"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)

    assert len(feedback) == 1
    assert feedback[0].type == "Using Perhaps"
    assert feedback[0].start == 42
    assert feedback[0].end == 49


def test_opinioncheck5():
    sentence = "We need to end climate change so all Americans should eat vegetables."
    prompt = "We need to end climate change so"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)

    assert len(feedback) == 1
    assert feedback[0].type == "Modal Check"
    assert feedback[0].start == 47
    assert feedback[0].end == 53


def test_opinioncheck6():
    sentence = "We need to end climate change because Barack Obama says all Americans should eat vegetables."
    prompt = "We need to end climate change because"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)

    assert len(feedback) == 0


def test_opinioncheck7():
    sentence = "We need to end climate change so all Americans ought to eat vegetables."
    prompt = "We need to end climate change so"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)

    assert len(feedback) == 1
    assert feedback[0].type == "Modal Check"
    assert feedback[0].start == 47
    assert feedback[0].end == 52


def test_opinioncheck8():
    sentence = "We need to end climate change because Barack Obama says all Americans ought to eat vegetables."
    prompt = "We need to end climate change because"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)

    assert len(feedback) == 0


def test_opinioncheck9():
    sentence = "Plastic bag reduction laws are helpful, so according to this article, plastic bag usage should be limited."
    prompt = "Plastic bag reduction laws are helpful, so"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)

    assert len(feedback) == 0


def test_opinioncheck10():
    sentence = "Plastic bag reduction laws are helpful, but not enough of " \
               "the general public is aware of the consumption and amount " \
               "of plastics consumed daily per household in the US."
    prompt = "Plastic bag reduction laws are helpful, but"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)

    assert len(feedback) == 0


def test_opinioncheck11():
    sentence = "Plastic bag reduction laws are helpful, because by those " \
               "laws we learn to protect environment , because plastic bag " \
               "reduction is very harmful for environment and people's health."
    prompt = "Plastic bag reduction laws are helpful, because"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)
    print(feedback)

    assert len(feedback) == 1


def test_opinioncheck12():
    sentence = "Plastic bag reduction laws are helpful, because not only " \
               "will it be good for our environment, but equally as good " \
               "for people health who frequently use plastic bags."
    prompt = "Plastic bag reduction laws are helpful, because"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)
    print(feedback)

    assert len(feedback) == 1


def test_opinioncheck13():
    sentence = "Methane from cow burps harms the environment, so it needs to be addressed soon."
    prompt = "Methane from cow burps harms the environment, so"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)
    print(feedback)

    assert len(feedback) == 1


def test_opinioncheck14():
    sentence = "Methane from cow burps harms the environment, so it's not wise to eat meat."
    prompt = "Methane from cow burps harms the environment, so"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)
    print(feedback)

    assert len(feedback) == 1


def test_opinioncheck15():
    sentence = "Plastic bag reduction laws are helpful, but the " \
               "downside is that when we reduce the creation of plastic " \
               "bags, some people will lose their jobs."

    prompt = "Plastic bag reduction laws are helpful, but"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)
    print(feedback)

    assert len(feedback) == 1


def test_opinioncheck16():
    sentence = "Plastic bag reduction laws are helpful, but " \
               "lets not exaggerate."

    prompt = "Plastic bag reduction laws are helpful, but"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)
    print(feedback)

    assert len(feedback) == 1


def test_opinioncheck17():
    sentence = "Large amounts of meat consumption are harming the environment, " \
               "so continue to eat cows more so that way they die faster."

    prompt = "Large amounts of meat consumption are harming the environment, so"

    check = OpinionCheck()
    feedback = check.check_from_text(sentence, prompt)
    print(feedback)

    assert len(feedback) == 1


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
    fp = 0
    fn = 0
    tp = 0
    with open("opinion_output.tsv", "w") as o:
        for sentence in sentences:
            prompt = re.match(".*?(because|, but|, so)", sentence)
            if prompt:
                prompt = prompt.group(0)
            else:
                prompt = ""

            feedback = check.check_from_text(sentence, prompt)
            if feedback:
                opinions += 1
                o.write(sentence + "\t" + ",".join([str(opinion) for opinion in feedback]) + "\n")
            else:
                o.write(sentence + "\t\n")

            if sentence in opinion_labels and not feedback:
                print("False negative (missed opinion):\t", sentence)
                fn += 1
            elif sentence not in opinion_labels and feedback:
                print("False positive (incorrectly identified as an opinion):\t", sentence)
                fp += 1
            elif sentence in opinion_labels and feedback:
                tp += 1

    precision = tp/(tp+fp)
    recall = tp/(tp+fn)
    f1_score = (2 * precision * recall) / (precision + recall) if precision + recall > 0 else 0

    print(f"Opinions: {opinions}/{len(sentences)} = {opinions/len(sentences)}%")
    print("Precision:", precision)
    print("Recall:", recall)
    print("F1-score:", f1_score)



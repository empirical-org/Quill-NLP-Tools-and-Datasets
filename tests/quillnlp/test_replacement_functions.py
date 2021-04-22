from quillnlp.grammar.corpus import replace_adverb_by_adjective, get_adjective_for_adverb, replace, replace_its_vs_it_s
from quillnlp.grammar.myspacy import nlp


def test_adv_by_adj_replacement():
    sentence_pairs = [("She sings beautifully.", "She sings beautiful."),
                      ("Nicely done.", "Nice done."),
                      ("She speaks very well of you.", "She speaks very good of you."),
                      ("He thinks very highly of you.", "He thinks very high of you."),
                      ("He always runs fast.", "He always runs fast."),
                      ("He used to rise early.", "He used to rise early.")]

    for (sentence, error) in sentence_pairs:
        doc = nlp(sentence)
        synthetic_error, _ = replace_adverb_by_adjective("ADV", doc)

        assert synthetic_error == error


def test_get_adverbs():
    word_pairs = [("nicely", "nice"),
                  ("well", "good"),
                  ("highly", "high")]

    for (adv, adj) in word_pairs:
        assert get_adjective_for_adverb(adv) == adj


def test_full_replacement_function():
    texts = [("It's an honor to meet you.", "Its an honor to meets you."),
             ("I have three children.", "I has three child."),
             ("You were taller than me.", "You was taller then me."),
             ("He doesn't answer.", "He don't answers."),
             ("He speaks well.", "He speak good."),
             ("He dances beautifully.", "He dance beautiful."),
             ("The women go home.", "The woman's goes home."),
             ("He wouldn't go.", "He wouldn't goes."),
             ("He can't go.", "He can't goes."),
             ("He cannot go.", "He cannot goes."),
             ("He can not go.", "He cans not goes.")
             ]

    for source_text, target_text in texts:
        doc = nlp(source_text)
        new_text, errors = replace(doc, 1)

        print(target_text)
        print(errors)

        assert new_text == target_text


def test_be_replacement_function():

    text = "He is home."
    alternatives = set(["He be home.", "He am home.", "He are home."])

    doc = nlp(text)
    new_text, errors = replace(doc, 1)

    assert new_text in alternatives


def test_its_replacement_function():

    text = "It's a great day."
    doc = nlp(text)
    text, entities = replace_its_vs_it_s(doc, 1)

    print(text)
    print(entities)

    assert text == "Its a great day."
    assert entities[0][0] == 0


def test_replace_plural_possessive_function():

    texts = [
        ("The earth's temperature increases.", "The earths temperature increases.", "earths"),
        ("They have three cars.", "They have three car's.", "car's"),
        ("It's an honor to meet you.", "It's an honor to meet you.", ""),
        ("She is Russia's richest woman.", "She is Russias richest woman.", "Russias"),
        ("John's second house", "Johns second house", "Johns"),
        ("Cars are expensive", "Car's are expensive", "Car's"),
        ("Ronaldo's global popularity", "Ronaldos global popularity", "Ronaldos"),
        ("The United States just won bragging rights in the race to build the world's speediest supercomputer.",
         "The United States just won bragging right's in the race to build the world's speediest supercomputer.",
         "right's")
    ]

    for source_text, target_text, token in texts:
        doc = nlp(source_text)
        new_text, errors = replace_plural_possessive(doc, 1)

        print(source_text)
        print(new_text)
        print(errors)

        assert new_text == target_text

        if errors:
            assert new_text[errors[0][0]:errors[0][1]] == token


def test_subject_pronoun_replacement():

    from quillnlp.grammar.generation import subject_pronoun_error_generator

    sentence = "Help me now"
    generated_sentence, _ = subject_pronoun_error_generator.generate_from_text(sentence)
    print(generated_sentence)
    assert generated_sentence == sentence

    sentence = "I see you"
    generated_sentence, _ = subject_pronoun_error_generator.generate_from_text(sentence)
    print(generated_sentence)
    assert generated_sentence != sentence

    sentence = "You she loves"
    generated_sentence, _ = subject_pronoun_error_generator.generate_from_text(sentence)
    print(generated_sentence)
    assert generated_sentence.startswith("You ")

    sentence = "She loves you"
    generated_sentence, _ = subject_pronoun_error_generator.generate_from_text(sentence)
    print(generated_sentence)
    assert not generated_sentence.startswith("She ")

    sentence = "You're tall"
    generated_sentence, _ = subject_pronoun_error_generator.generate_from_text(sentence)
    print(generated_sentence)
    assert not generated_sentence.startswith("You're ")

    sentence = "And I will always love you"
    generated_sentence, _ = subject_pronoun_error_generator.generate_from_text(sentence)
    print(generated_sentence)


def test_object_pronoun_replacement():
    from quillnlp.grammar.generation import object_pronoun_error_generator

    sentence = "Help me now"
    generated_sentence, entities = object_pronoun_error_generator.generate_from_text(sentence)
    print(generated_sentence)
    assert generated_sentence != sentence
    assert generated_sentence[entities[0][0]: entities[0][1]] == generated_sentence.split()[1]

    sentence = "I saw him"
    generated_sentence, entities = object_pronoun_error_generator.generate_from_text(sentence)
    print(generated_sentence)
    assert generated_sentence != sentence
    assert generated_sentence[entities[0][0]: entities[0][1]] == generated_sentence.split()[-1]

    sentence = "I saw her"
    generated_sentence, entities = object_pronoun_error_generator.generate_from_text(sentence)
    print(generated_sentence)
    assert generated_sentence != sentence
    assert generated_sentence[entities[0][0]: entities[0][1]] == generated_sentence.split()[-1]

    sentence = "I saw her book"
    generated_sentence, _ = object_pronoun_error_generator.generate_from_text(sentence)
    print(generated_sentence)
    assert generated_sentence == sentence

    sentence = "She loves me"
    generated_sentence, entities = object_pronoun_error_generator.generate_from_text(sentence)
    print(generated_sentence)
    assert generated_sentence != sentence
    assert generated_sentence[entities[0][0]: entities[0][1]] == "I"


def test_possessive_pronoun_replacement():
    from quillnlp.grammar.generation import possessive_pronoun_error_generator

    sentence = "I saw her"
    generated_sentence, _ = possessive_pronoun_error_generator.generate_from_text(sentence)
    print(generated_sentence)
    assert generated_sentence == sentence

    sentence = "I saw her book"
    generated_sentence, _ = possessive_pronoun_error_generator.generate_from_text(sentence)
    print(generated_sentence)
    assert generated_sentence != sentence

    sentence = "I saw my book"
    generated_sentence, _ = possessive_pronoun_error_generator.generate_from_text(sentence)
    print(generated_sentence)
    assert generated_sentence != sentence


def test_their_replacement():
    from quillnlp.grammar.generation import their_error_generator

    sentence = "There he is!"
    generated_sentence, _ = their_error_generator.generate_from_text(sentence)
    assert generated_sentence == "Their he is!" or generated_sentence == "They're he is!"

    sentence = "It's their car."
    generated_sentence, _ = their_error_generator.generate_from_text(sentence)
    assert generated_sentence == "It's there car." or generated_sentence == "It's they're car."

    sentence = "They're cool."
    generated_sentence, _ = their_error_generator.generate_from_text(sentence)
    assert generated_sentence == "Their cool." or generated_sentence == "There cool."


def test_perfect_without_have_replacement():

    from quillnlp.grammar.verbs.perfect import PerfectTenseWithoutHaveErrorGenerator

    generator = PerfectTenseWithoutHaveErrorGenerator()

    sentence1 = "I have seen him."
    sentence1a, _ = generator.generate_from_text(sentence1)
    assert sentence1a == "I seen him."

    sentence2 = "I will have seen him."
    sentence2a, _ = generator.generate_from_text(sentence2)
    assert sentence2a == "I will seen him."

import spacy

from quillnlp.grammar.corpus import replace_adverb_by_adjective, get_adjective_for_adverb, replace

nlp = spacy.load("en")


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
             ("You were taller than me.", "You were taller then me."),
             ("He doesn't answer.", "He don't answers."),
             ("He is no Barack Obama.", "He be no Barack Obama."),
             ("You are no Barack Obama.", "You is no Barack Obama."),
             ("He speaks well.", "He speak good."),
             ("He dances beautifully.", "He dance beautiful."),
             ("The women go home.", "The woman's goes home."),
             ("There are three women.", "There is three woman.")
             ]

    for source_text, target_text in texts:
        doc = nlp(source_text)
        new_text, errors = replace(doc, 1)

        assert new_text == target_text


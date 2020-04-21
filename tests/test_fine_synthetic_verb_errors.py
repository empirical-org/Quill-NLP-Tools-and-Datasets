from quillnlp.grammar import verbs


def test_passive_without_be():

    input = "The lion is known for its ferocious roar."
    output = "The lion known for its ferocious roar."

    sentence = verbs.remove_be_from_passive(input)
    assert output == sentence


def test_passive_with_incorrect_be_form():

    input = "The lion is known for its ferocious roar."
    output1 = "The lion are known for its ferocious roar."
    output2 = "The lion been known for its ferocious roar."
    output3 = "The lion be known for its ferocious roar."
    output4 = "The lion am known for its ferocious roar."

    sentence = verbs.swap_forms_of_be(input)
    assert sentence in set([output1, output2, output3, output4])


def test_replace_past_participle_by_simple_past():

    input = "I had forgotten to pay the bill."
    output = "I had forgot to pay the bill."

    sentence = verbs.replace_past_participle_by_simple_past(input)
    assert output == sentence


def test_replace_past_participle_by_incorrect_simple_past():

    input = "She had broken all the windows."
    output = "She had breaked all the windows."

    sentence = verbs.replace_past_participle_by_incorrect_simple_past(input)
    assert output == sentence


def test_remove_be_from_perfect_progressive():

    input = "I have been working here for a long time."
    output = "I been working here for a long time."

    sentence = verbs.remove_have_from_perfect_progressive(input)
    assert output == sentence


def test_remove_have_from_perfect():

    input = "The dog has eaten my homework."
    output = "The dog eaten my homework."

    sentence = verbs.remove_have_from_perfect(input)
    assert output == sentence


def test_remove_have_from_passive_perfect():

    # TODO: distinguish from above
    input = "The lion has been known for its ferocious roar."
    output = "The lion been known for its ferocious roar."

    sentence = verbs.remove_have_from_perfect(input)
    assert output == sentence


def test_irregular_past_tense():

    input = "I broke the lamp."
    output = "I breaked the lamp."

    sentence = verbs.create_incorrect_irregular_past_tense(input)
    assert output == sentence


def test_verb_shifts():

    input_output_pairs = [("When my alarm went off, I got out of bed.",
                           "When my alarm goes off, I got out of bed."),
                          ("When my alarm goes off, I get out of bed.",
                           "When my alarm went off, I get out of bed.")]

    for input, output in input_output_pairs:

        sentence = verbs.change_tense_in_subclause(input)
        assert output == sentence


def test_incorrect_future():

    input = "I will give you candy when you clean your room."
    output = "I will give you candy when you will clean your room."

    sentence = verbs.insert_future_in_subclause(input)

    assert output == sentence


def test_incorrect_past_perfect():

    input = "I had already eaten dinner when you called."
    output = "I had already eaten dinner when you had called."

    sentence = verbs.replace_past_simple_with_past_perfect(input)

    assert output == sentence


def test_incorrect_past_passive():

    input = "My dinner was eaten a long time ago."
    output = "My dinner was ate a long time ago."

    sentence = verbs.replace_past_participle_by_simple_past(input)

    assert output == sentence


def test_incorrect_regular_past_passive():

    input = "The lion is known for its ferocious roar."
    output = "The lion is knowed for its ferocious roar."

    sentence = verbs.replace_past_participle_by_incorrect_simple_past(input)

    assert output == sentence


def test_incorrect_third_person_verb():

    input = "The wind blows through the leaves."
    output = "The wind blow through the leaves."

    sentence = verbs.replace_3rd_person_verb_by_infinitive(input)

    assert output == sentence


def test_incorrect_verb_after_personal_pronoun():

    # TODO: this is more specific than the previous rule.
    # Make sure this is run first.

    input_output_pairs = [("They are late again.", "They is late again."),
                          ("He lives in Belgium.", "He live in Belgium.")]

    for input, output in input_output_pairs:
        sentence = verbs.swap_3rd_and_other_person_verb_form_after_pronoun(input)

        assert output == sentence


def test_plural_after_collective():

    # TODO: again a more specific rule

    input = "The herd is stampeding"
    output = "The herd are stampeding"

    sentence = verbs.replace_singular_by_plural_after_collective(input)
    assert output == sentence


def test_plural_after_indefinite():

    # TODO: is more specific

    input = "Each student is expected to present"
    output = "Each student are expected to present"

    sentence = verbs.replace_singular_by_plural_after_indefinite(input)

    assert output == sentence


def test_incorrect_negative():

    # TODO: is more specific

    input = "He doesn't know where to go."
    output = "He don't know where to go."

    sentence = verbs.replace_3rd_person_verb_by_infinitive(input)
    assert sentence == output

from quillgrammar.grammar.constants import GrammarError
from quillnlp.grammar.generation import TokenReplacementErrorGenerator, subject_pronoun_error_generator, \
    object_pronoun_error_generator, possessive_pronoun_error_generator, PluralPossessiveErrorGenerator, \
    their_error_generator, PronounReplacementErrorGenerator, IncorrectIrregularPastErrorGenerator, \
    IncorrectParticipleErrorGenerator, IrregularPluralNounErrorGenerator


def test_token_replacement_through():

    error_generator = TokenReplacementErrorGenerator({"through": ["threw", "thru"],
                                                     "threw": ["through", "thru"],
                                                     "thru": ["threw", "through"]},
                                                    GrammarError.THROUGH_THREW_THRU.value)

    sentence = 'I drove through town.'
    error_sentence, entities, relevant = error_generator.generate_from_text(sentence)
    print(error_sentence)
    assert error_sentence == 'I drove threw town.' or error_sentence == 'I drove thru town.'


def test_token_replacement_lose():
    error_generator = TokenReplacementErrorGenerator({"loose": ["lose"],
                                                      "lose": ["loose"]},
                                                    GrammarError.LOOSE_LOSE.value)

    sentence = 'We lose a loose cannon.'
    error_sentence, entities, relevant = error_generator.generate_from_text(sentence)
    print(error_sentence)
    assert error_sentence == 'We loose a loose cannon.' or error_sentence == 'We lose a lose cannon.'


def test_subject_pronouns():

    error_generator = subject_pronoun_error_generator

    sentence = 'I am home.'
    error_sentence, entities, relevant = error_generator.generate_from_text(sentence)
    print(error_sentence)
    assert error_sentence in ['Me am home.', 'My am home.', 'Mine am home.', "My's am home."]

    sentence = 'Now I am home.'
    error_sentence, entities, relevant = error_generator.generate_from_text(sentence)
    print(error_sentence)
    assert error_sentence in ['Now me am home.', 'Now my am home.', 'Now mine am home.', "Now my's am home."]


def test_incorrect_irregular_past():

    error_generator = IncorrectIrregularPastErrorGenerator()

    sentence = 'I came home.'
    error_sentence, entities, relevant = error_generator.generate_from_text(sentence)
    print(error_sentence, entities)

    assert error_sentence == 'I comed home.'

    sentence = 'I thought so.'
    error_sentence, entities, relevant = error_generator.generate_from_text(sentence)
    print(error_sentence, entities)

    assert error_sentence == 'I thinked so.'


def test_incorrect_participle():

    error_generator = IncorrectParticipleErrorGenerator()
    
    sentence = 'I have come home.'
    error_sentence, entities, relevant = error_generator.generate_from_text(sentence)
    print(error_sentence, entities)

    assert error_sentence == 'I have comed home.'

    sentence = 'I have read it.'
    error_sentence, entities, relevant = error_generator.generate_from_text(sentence)
    print(error_sentence, entities)

    assert error_sentence == 'I have readed it.'


def test_irregular_plural_nouns():

    error_generator = IrregularPluralNounErrorGenerator()

    sentence = 'I have twenty sheep.'
    error_sentence, entities, relevant = error_generator.generate_from_text(sentence)
    print(error_sentence, entities)
    
    assert error_sentence == 'I have twenty sheeps.'


def test_plural_possessive():
    
    error_generator = PluralPossessiveErrorGenerator()

    sentence = 'I have twenty books.'
    error_sentence, entities, relevant = error_generator.generate_from_text(sentence)
    print(error_sentence, entities)
    
    assert error_sentence == "I have twenty book's."
    
    sentence = "This is my mother's car."
    error_sentence, entities, relevant = error_generator.generate_from_text(sentence)
    print(error_sentence, entities)
    
    assert error_sentence == "This is my mothers car."

    sentence = "He wouldn't come home."
    error_sentence, entities, relevant = error_generator.generate_from_text(sentence)
    print(error_sentence, entities)
    
    assert error_sentence == "He wouldn't come home."

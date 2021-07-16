from quillnlp.grammar.fragments import FragmentWithoutVerbGenerator, FragmentWithoutSubjectGenerator, \
    MissingObjectFragmentGenerator, prepositionalPhraseFragmentGenerator, adverbialClauseFragmentGenerator, \
    relativeClauseFragmentGenerator, infinitiveFragmentGenerator, nounPhraseFragmentGenerator

from quillnlp.grammar.myspacy import nlp


def test_fragment_without_verb_generation():

    sentences = [('This is great.', 'This great.'),
                 ('This has been great.', 'This great.'),
                 ('He lives.', 'He.')]

    generator = FragmentWithoutVerbGenerator()
    for sentence, fragment in sentences:

        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc)

        print(sentence, '=>', generated_sentence)
        assert generated_sentence == fragment


def test_fragment_without_subject_generation():

    sentences = [('This is great.', 'Is great.'),
                 ('The old man is home.', 'Is home.')]

    generator = FragmentWithoutSubjectGenerator()
    for sentence, fragment in sentences:

        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc)

        print(sentence, '=>', generated_sentence)
        assert generated_sentence == fragment


def test_missing_object_fragment_generation():

    sentences = [('While going to the store, I saw a deer next to me.',
                  'While going to the store, I saw next to me.'),
                 ('May I use the bathroom.', 'May I use.'),
                 ('May I use the bathroom that is in the corner.', 'May I use.')]

    generator = MissingObjectFragmentGenerator()
    for sentence, fragment in sentences:

        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc)

        print(sentence, '=>', generated_sentence)
        assert generated_sentence == fragment


def test_prepositional_phrase_fragment_generation():

    sentences = [('They left because of the rain.', 'Because of the rain.'),
                 ('They live in the city.', 'In the city.')]

    generator = prepositionalPhraseFragmentGenerator
    for sentence, fragment in sentences:

        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc)

        print(sentence, '=>', generated_sentence)
        assert generated_sentence == fragment


def test_adverbial_clause_fragment_generation():

    sentences = [('They left before the game ended.', 'Before the game ended.'),
                 ('Because it was raining, they left.', 'Because it was raining.'),
                 ('It starts to rain whenever I walk the dog.', 'Whenever I walk the dog.')]

    generator = adverbialClauseFragmentGenerator
    for sentence, fragment in sentences:

        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc)

        print(sentence, '=>', generated_sentence)
        assert generated_sentence == fragment


def test_relative_clause_fragment_generation():

    sentences = [('It is the cat that I saw sitting there.', 'That I saw sitting there.'),
                 ('He runs ultras, which I find to be a bit much.', 'Which I find to be a bit much.')]

    generator = relativeClauseFragmentGenerator
    for sentence, fragment in sentences:

        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc)

        print(sentence, '=>', generated_sentence)
        assert generated_sentence == fragment


def test_fragment_without_verb_generation_with_prompt():

    sentences = [('Schools should not sell fast food, because it is unhealthy.',
                  'Schools should not sell fast food,',
                  'Schools should not sell fast food, because it unhealthy.')]

    generator = FragmentWithoutVerbGenerator()
    for sentence, prompt, fragment in sentences:
        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc, prompt=prompt)

        print(sentence, '=>', generated_sentence)
        assert generated_sentence == fragment


def test_fragment_without_subject_generation_with_prompt():

    sentences = [('Schools should not sell fast food, because it is unhealthy.',
                  'Schools should not sell fast food,',
                  'Schools should not sell fast food, because is unhealthy.')]

    generator = FragmentWithoutSubjectGenerator()
    for sentence, prompt, fragment in sentences:
        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc, prompt=prompt)

        print(sentence, '=>', generated_sentence)
        assert generated_sentence == fragment


def test_fragment_infinitive_phrase():

    sentences = [('I love to dance.', 'To dance.'),
                 ('He told me to bring the food.', 'To bring the food.')]

    generator = infinitiveFragmentGenerator
    for sentence, fragment in sentences:

        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc)

        print(sentence, '=>', generated_sentence)
        assert generated_sentence == fragment


def test_fragment_noun_phrase():

    sentences = [('May I use the bathroom?', 'The bathroom.'),
                 ('He bought the car he loved the most.', 'The car he loved the most.')]

    generator = nounPhraseFragmentGenerator
    for sentence, fragment in sentences:

        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc)

        print(sentence, '=>', generated_sentence)
        assert generated_sentence == fragment

from quillnlp.grammar.fragments import FragmentWithoutVerbGenerator, FragmentWithoutSubjectGenerator, \
    MissingObjectFragmentGenerator, prepositionalPhraseFragmentGenerator, DependentClauseFragmentGenerator, \
    RelativeClauseFragmentGenerator, infinitiveFragmentGenerator, NounPhraseFragmentGenerator, VerbPhraseFragmentGenerator, \
    FragmentWithoutAuxiliaryGenerator, DependentClauseFragmentGenerator

from quillnlp.grammar.myspacy import nlp


def test_fragment_without_verb_generation():

    sentences = [('I saw the man.', 'I the man.'),
                 ('This has been great.', 'This has great.'),
                 ('He lives.', 'He.')]

    generator = FragmentWithoutVerbGenerator()
    for sentence, fragment in sentences:

        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc)

        print(sentence, '=>', generated_sentence)
        assert generated_sentence.lower()[:-1] == fragment.lower()[:-1]


def test_fragment_without_auxiliary_generation():

    sentences = [('This is great.', 'This great.'),
                 ('The boy is sitting on the chair.', 'The boy sitting on the chair.'),
                 ('Global warming is caused by greenhouse gases.', 'Global warming caused by greenhouse gases.')]

    generator = FragmentWithoutAuxiliaryGenerator()
    for sentence, fragment in sentences:

        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc)

        print(sentence, '=>', generated_sentence)
        assert generated_sentence.lower()[:-1] == fragment.lower()[:-1]


def test_fragment_without_auxiliary_not_relevant():

    sentences = ['I felt awkward and clumsy']

    generator = FragmentWithoutAuxiliaryGenerator()
    for sentence in sentences:

        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc)
        assert relevant is False


def test_fragment_without_subject_generation():

    sentences = [('This is great.', 'Is great.'),
                 ('The old man is home.', 'Is home.')]

    generator = FragmentWithoutSubjectGenerator()
    for sentence, fragment in sentences:

        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc)

        print(sentence, '=>', generated_sentence)
        assert generated_sentence.lower()[:-1] == fragment.lower()[:-1]


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
        assert generated_sentence.lower()[:-1] == fragment.lower()[:-1]


def test_prepositional_phrase_fragment_generation():

    sentences = [('They left because of the rain.', 'Because of the rain.'),
                 ('They live in the city.', 'In the city.')]

    generator = prepositionalPhraseFragmentGenerator
    for sentence, fragment in sentences:

        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc)

        print(sentence, '=>', generated_sentence)
        assert generated_sentence.lower()[:-1] == fragment.lower()[:-1]


def test_adverbial_clause_fragment_generation():

    sentences = [('They left before the game ended.', 'Before the game ended.'),
                 ('Because it rained, they left.', 'Because it rained.'),
                 ("They're doing anything to distract themselves from the fact that they feel empty inside and unworthy.",
                  "They're doing anything to distract themselves from the fact that they feel empty inside and unworthy.")]

    generator = DependentClauseFragmentGenerator()
    for sentence, fragment in sentences:

        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc)

        print(sentence, '=>', generated_sentence)
        assert generated_sentence.lower()[:-1] == fragment.lower()[:-1]


def test_relative_clause_fragment_generation():

    sentences = [('It is the cat that I saw sitting there.', 'That I saw sitting there.'),
                 ('He runs ultras, which I find to be a bit much.', 'Which I find to be a bit much.')]

    generator = RelativeClauseFragmentGenerator()
    for sentence, fragment in sentences:

        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc)

        print(sentence, '=>', generated_sentence)
        assert generated_sentence.lower()[:-1] == fragment.lower()[:-1]


def test_fragment_without_verb_generation_with_prompt():

    sentences = [('Schools should not sell fast food, because it is unhealthy.',
                  'Schools should not sell fast food,',
                  'Schools should not sell fast food, because it unhealthy.')]

    generator = FragmentWithoutVerbGenerator()
    for sentence, prompt, fragment in sentences:
        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc, prompt=prompt)

        print(sentence, '=>', generated_sentence)
        assert generated_sentence.lower()[:-1] == fragment.lower()[:-1]


def test_fragment_without_subject_generation_with_prompt():

    sentences = [('Schools should not sell fast food, because it is unhealthy.',
                  'Schools should not sell fast food,',
                  'Schools should not sell fast food, because is unhealthy.')]

    generator = FragmentWithoutSubjectGenerator()
    for sentence, prompt, fragment in sentences:
        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc, prompt=prompt)

        print(sentence, '=>', generated_sentence)
        assert generated_sentence.lower()[:-1] == fragment.lower()[:-1]


def test_fragment_infinitive_phrase():

    sentences = [('I love to dance.', 'To dance.'),
                 ('He told me to bring the food.', 'To bring the food.')]

    generator = infinitiveFragmentGenerator
    for sentence, fragment in sentences:

        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc)

        print(sentence, '=>', generated_sentence)
        assert generated_sentence.lower()[:-1] == fragment.lower()[:-1]


def test_fragment_noun_phrase():

    sentences = [('May I use the bathroom?', 'The bathroom.'),
                 ('He bought the car he loved the most.', 'He bought the car he loved the most.')]

    generator = NounPhraseFragmentGenerator()
    for sentence, fragment in sentences:

        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc)

        print(sentence, '=>', generated_sentence)
        assert generated_sentence.lower()[:-1] == fragment.lower()[:-1]


def test_fragment_verb_phrase():

    sentences = [('We are growing trees.', 'Growing trees.'),
                 ('We have been robbed.', 'Been robbed.'),
                 ('We will keep growing trees.', 'Growing trees.'),
                 ('I have cleaned the car.', 'Cleaned the car.'),
                 ('We were robbed of all our dreams.', 'Robbed of all our dreams.')]

    generator = VerbPhraseFragmentGenerator()
    for sentence, fragment in sentences:

        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc)

        print(sentence, '=>', generated_sentence)
        assert generated_sentence.lower()[:-1] == fragment.lower()[:-1]

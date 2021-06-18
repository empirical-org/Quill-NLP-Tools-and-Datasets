from quillnlp.grammar.fragments import FragmentWithoutVerbGenerator, FragmentWithoutSubjectGenerator
from quillnlp.grammar.myspacy import nlp


def test_fragment_without_verb_generation():

    sentences = [('This is great.', 'This great.'),
                 ('This has been great.', 'This great.')]

    generator = FragmentWithoutVerbGenerator()
    for sentence, fragment in sentences:

        doc = nlp(sentence)
        generated_sentence, entities, relevant = generator.generate_from_doc(doc)

        print(sentence, '=>', generated_sentence)
        assert generated_sentence == fragment


def test_fragment_without_subject_generation():

    sentences = [('This is great.', 'is great.'),
                 ('The old man is home.', 'is home.')]

    generator = FragmentWithoutSubjectGenerator()
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

from quillnlp.utils import detokenize


def test_detokenization1():

    sentence_in = "This is a tokenized sentence ."
    sentence_out = "This is a tokenized sentence."

    detokenized_sentence = detokenize(sentence_in)
    assert detokenized_sentence == sentence_out


def test_detokenization2():

    sentence_in = "This ca n't and wo n't do ."
    sentence_out = "This can't and won't do."

    detokenized_sentence = detokenize(sentence_in)
    assert detokenized_sentence == sentence_out

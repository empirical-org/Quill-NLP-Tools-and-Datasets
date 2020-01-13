import pyinflect


def has_plural_noun(doc):
    for token in doc:
        if token.tag_ == "NNS" and token.text.endswith("s"):
            return True
    return False


def replace_plural_by_possessive(error_type, doc):
    text = ""
    entities = []
    for token in doc:
        if token.tag_ == "NNS" and token.text.endswith("s"):
            lemma = token.lemma_
            if token.text.istitle():
                lemma = lemma.title()

            start_index = len(text)  # we cannot use token.idx, because there may be double replacements
            entities.append((start_index, start_index + len(lemma + "'s"), error_type))
            text += lemma + "'s" + token.whitespace_
        else:
            text += token.text_with_ws
    return text, entities


def has_possessive_noun(doc):
    for token in doc:
        if token.i > 0 and token.tag_ == "POS" and doc[token.i-1].tag_.startswith("N"):
            return True
    return False


def replace_possessive_by_plural(error_type, doc):
    text = ""
    entities = []
    skip_next = False
    for i in range(len(doc)):
        if i < len(doc)-1 and doc[i].tag_.startswith("N") and doc[i+1].tag_ == "POS":
            start_index = len(text)
            entities.append((start_index, start_index + len(doc[i].text + "s"), error_type))
            text += doc[i].text + "s" + doc[i+1].whitespace_
            skip_next = True
        elif not skip_next:
            text += doc[i].text_with_ws
        elif skip_next:
            skip_next = False
    return text, entities


def has_third_person_singular_verb(doc):
    for token in doc:
        if token.tag_ == "VBZ" and token.lemma_ != "be":
            return True
    return False


def replace_verb_form(source_tag, target_tag, error_type, doc):
    # TODO: we need to find a better solution for verbs followed by "n't", where the
    # whitespace is not correct => He ben't do that.
    text = ""
    entities = []
    for token in doc:
        if token.tag_ == source_tag:
            if token.text.startswith("'"):
                text += " "
            if target_tag == "VB":
                new_verb_form = token.lemma_
            else:
                new_verb_form = token._.inflect(target_tag)

            if new_verb_form is None or new_verb_form == token.text:
                text += token.text_with_ws
            else:
                if token.text[0].isupper():
                    new_verb_form = new_verb_form.title()
                start_index = len(text)
                text += new_verb_form + token.whitespace_
                entities.append((start_index, start_index + len(new_verb_form), error_type))
        else:
            text += token.text_with_ws
    return text, entities


def has_present_verb_non_third_person(doc):
    for token in doc:
        if token.tag_ == "VBP" and token.lemma_ != "be":
            return True
    return False


def has_infinitive(doc):
    for token in doc:
        if token.tag_ == "VB" and token.lemma_ != "be":
            return True
    return False


def contains_token(token, doc):
    tokens = set([t.text.lower() for t in doc])
    return token in tokens


def contains_phrase(token_list, doc):
    tokens = [t.text.lower() for t in doc]
    for i in range(len(tokens)-len(token_list)+1):
        if tokens[i:i+len(token_list)] == token_list:
            return True
    return False


def replace_word(source_word, target_word, error_type, doc):

    new_tokens = []
    entities = []
    for token in doc:
        if len(entities) > 0:  # we only make one correction per sentence
            new_tokens.append(token.text_with_ws)
        elif token.text.lower() == source_word:
            if token.text[0].isupper():
                new_tokens.append(target_word.title() + token.whitespace_)
            else:
                new_tokens.append(target_word + token.whitespace_)
            entities.append((token.idx, token.idx + len(target_word), error_type))
        else:
            new_tokens.append(token.text_with_ws)

    return "".join(new_tokens), entities


def replace_bigram(source_bigram, target_word, error_type, doc):
    new_tokens = []
    entities = []

    skip_token = False
    for token in doc:
        if skip_token:
            skip_token = False
        elif len(entities) > 0:  # we only make one correction per sentence
            new_tokens.append(token.text_with_ws)
        elif token.i < len(doc) - 1 and token.text.lower() == source_bigram[0] \
                and doc[token.i + 1].text.lower() == source_bigram[1]:
            if token.text[0].isupper():
                new_tokens.append(target_word.title() + doc[token.i + 1].whitespace_)
            else:
                new_tokens.append(target_word + doc[token.i + 1].whitespace_)
            entities.append((token.idx, token.idx + len(target_word), error_type))
            skip_token = True
        else:
            new_tokens.append(token.text_with_ws)
    return "".join(new_tokens), entities


def get_pos(doc):
    """ Returns a set of all pos_ attributes in the document. """
    return set([t.pos_ for t in doc])


def get_tag(doc):
    """ Returns a set of all tag_ attributes in the document. """
    return set([t.tag_ for t in doc])


def has_adverb(doc):
    return "ADV" in get_pos(doc)


def has_modal(doc):
    """ Modal verbs (will, can, should, etc.) have POS VERB and TAG MD"""
    return "MD" in get_tag(doc)


def has_aux(doc):
    return "AUX" in get_pos(doc)


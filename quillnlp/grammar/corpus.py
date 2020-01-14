import pyinflect
from itertools import chain
from typing import List, Tuple
from nltk.corpus import wordnet as wn
from difflib import get_close_matches as gcm
from spacy.tokens import Doc


def has_plural_noun(doc: Doc) -> bool:
    """ Returns True if the document contains a plural noun and False otherwise. """
    for token in doc:
        if token.tag_ == "NNS" and token.text.endswith("s"):
            return True
    return False


def has_possessive_noun(doc: Doc) -> bool:
    """ Returns True if the document contains a possessive noun and False otherwise. """
    for token in doc:
        # Return true if we find an 's (POS) preceded by a noun.
        if token.i > 0 and token.tag_ == "POS" and doc[token.i-1].tag_.startswith("N"):
            return True
    return False


def has_third_person_singular_verb(doc: Doc) -> bool:
    """ Returns True if the document contains a third person present singular verb. """
    for token in doc:
        if token.tag_ == "VBZ" and token.lemma_ != "be":
            return True
    return False


def has_present_verb_non_third_person(doc: Doc) -> bool:
    """ Returns True if the document contains a non-third-person-singular present verb. """
    for token in doc:
        if token.tag_ == "VBP" and token.lemma_ != "be":
            return True
    return False


def has_infinitive(doc: Doc) -> bool:
    """ Returns True if the document contains an infinitive verb. """
    for token in doc:
        if token.tag_ == "VB" and token.lemma_ != "be":
            return True
    return False


def contains_token(token: str, doc: Doc) -> bool:
    """ Returns True if the lowercased document contains the specified token. """
    tokens = set([t.text.lower() for t in doc])
    return token in tokens


def contains_phrase(token_list: List[str], doc: Doc) -> bool:
    """ Returns True if the lowercased document contains the specified phrase. """
    tokens = [t.text.lower() for t in doc]
    for i in range(len(tokens)-len(token_list)+1):
        if tokens[i:i+len(token_list)] == token_list:
            return True
    return False


def get_pos(doc: Doc) -> set(str):
    """ Returns the set of all pos_ attributes in the document. """
    return set([t.pos_ for t in doc])


def get_tag(doc: Doc) -> set(str):
    """ Returns a set of all tag_ attributes in the document. """
    return set([t.tag_ for t in doc])


def has_adverb(doc: Doc) -> bool:
    """ Returns True if the document contains an adverb. """
    return "ADV" in get_pos(doc)


def has_modal(doc: Doc) -> bool:
    """ Returns True if the document contains a modal verb.
    Modal verbs (will, can, should, etc.) have POS VERB and TAG MD"""
    return "MD" in get_tag(doc)


def has_aux(doc: Doc) -> bool:
    """ Returns True if the document contains an auxiliary verb other than be. """
    for token in doc:
        if token.pos_ == "AUX" and token.lemma_ != "be":
            return True
    return False


def has_do(doc: Doc) -> bool:
    """ Returns True if the document contains the verb 'do' as an auxiliary. """
    for token in doc:
        if token.pos_ == "AUX" and token.lemma_ == "do":
            return True
    return False


# Replacement functions


def replace_word(source_word: str, target_word: str, error_type: str, doc: Doc) -> Tuple[str, List[Tuple]]:
    """ Replace the source word by a target word in the document. """

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
            error_start_idx = len("".join(new_tokens))
            entities.append((error_start_idx, error_start_idx + len(target_word), error_type))
        else:
            new_tokens.append(token.text_with_ws)

    return "".join(new_tokens), entities


def get_adjective_for_adverb(adverb: str) -> str:
    """
    Get the adjective corresponding to an adverb, e.g. beautifully -> beautiful

    Args:
        adverb:

    Returns:

    """
    possible_adj = []
    for ss in wn.synsets(adverb):
        for lemmas in ss.lemmas():  # all possible lemmas
            for ps in lemmas.pertainyms():  # all possible pertainyms
                possible_adj.append(ps.name())
    close_matches = gcm(adverb, possible_adj)
    if len(close_matches) > 0:
        return close_matches[0]
    return None


def replace_bigram(source_bigram: List[str], target_word: str, error_type: str, doc) -> Tuple[str, List[Tuple]]:
    """
    Replace a bigram by a word in a document

    Args:
        source_bigram:
        target_word:
        error_type:
        doc:

    Returns:

    """
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
            error_start_idx = len("".join(new_tokens))
            entities.append((error_start_idx, error_start_idx + len(target_word), error_type))
            skip_token = True
        else:
            new_tokens.append(token.text_with_ws)
    return "".join(new_tokens), entities


def replace_adverb_by_adjective(error_type: str, doc: Doc) -> Tuple[str, List[Tuple]]:
    """ Replaces adverbs by adjectives in the provided document. """

    new_tokens = []
    entities = []
    for token in doc:
        if token.pos_ == "ADV":
            adverb = get_adjective_for_adverb(token.text.lower())
            if adverb is not None:
                if token.text.istitle():
                    adverb = adverb.title()
                new_tokens.append(adverb + token.whitespace_)
                if adverb != token.text:
                    error_start_idx = len("".join(new_tokens))
                    entities.append((error_start_idx, error_start_idx + len(adverb), error_type))
            else:
                new_tokens.append(token.text_with_ws)
        else:
            new_tokens.append(token.text_with_ws)
    return "".join(new_tokens), entities


def replace_verb_form(source_tag: str, target_tag: str, error_type: str, doc: Doc) -> Tuple[str, List[Tuple]]:
    """
    Replaces all verb forms with the given source tag in the document by the corresponding
    form with the other tag

    Args:
        source_tag: the tag of the verbs that should be replaced, e.g. VBZ
        target_tag: the tag of the replacing form, e.g. VB
        error_type: the label of the error type
        doc: the document

    Returns:

    """
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


def replace_plural_by_possessive(error_type: str, doc: Doc) -> Tuple[str, List[Tuple]]:
    """ Replaces plurals by possessives in document, e.g. books => book's """

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


def replace_possessive_by_plural(error_type: str, doc: Doc) -> Tuple[str, List[Tuple]]:
    """ Replaces possessives by plurals in a document, e.g. horse's -> horses """
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

import random

import lemminflect

from quillgrammar.grammar.constants import Tag, GrammarError, Dependency, POS, TokenSet
from quillnlp.grammar.generation import ErrorGenerator
from quillnlp.grammar.verbutils import get_subject, get_plural, is_indefinite, has_noun_subject, \
    is_negated_with_contraction, has_following_subject, subject_has_neither, subject_has_either, has_pronoun_subject, \
    has_indefinite_subject



def replace_verb(token, doc, error_name, new_sentence, entities, p):
    # present third-person singular -> other form
    if token.tag_ == Tag.PRESENT_SING3_VERB.value and random.random() < p:
        if token.lemma_ == "be" and doc[token.i + 1].text.lower() == "n't":
            # only 'is' and 'are' can be followed by "n't"
            new_form = "are"
        elif token.lemma_ == "be":
            # most confusion will be between is and are, so are gets highest probability
            new_form = random.choice(["be", "am", "are", "are", "are"])
        else:
            new_form = token.lemma_
        new_form = new_form.title() if token.text.istitle() else new_form
        entities.append((len(new_sentence),
                         len(new_sentence) + len(new_form),
                         error_name))
        new_sentence += new_form + token.whitespace_

    # present other form -> third-person form
    elif token.tag_ == Tag.PRESENT_OTHER_VERB.value and random.random() < p:
        if token.lemma_ == "be":
            other_forms = set(["be", "are", "am", "is"]) - set(token.text.lower())
            other_forms = list(other_forms)
            if "is" in other_forms:
                other_forms.extend(["is", "is", "is"])

            if doc[token.i + 1].text.lower() == "n't":
                new_form = 'is'
            else:
                new_form = random.choice(other_forms)
            new_form = new_form.title() if token.text.istitle() else new_form
            entities.append((len(new_sentence),
                             len(new_sentence) + len(new_form),
                             error_name))
            new_sentence += new_form + token.whitespace_

        # Deal with 'ain't', which has the lemma 'ai' and should not be
        # rewritten to 'aisn't'.
        elif token.text.lower() == 'ai':
            new_sentence += token.text_with_ws
        # Deal with contracted forms like Im and Theyve, which miss an apostrophe
        # and do not get the correct lemma.
        elif token.i > 0 and not token.text.startswith("'") and doc[token.i-1].whitespace_ == '':
            new_sentence += token.text_with_ws
        else:
            new_form = token._.inflect(Tag.PRESENT_SING3_VERB.value)
            if new_form is not None:
                entities.append((len(new_sentence),
                                 len(new_sentence) + len(new_form),
                                 error_name))
                new_sentence += new_form + token.whitespace_
            else:
                new_sentence += token.text_with_ws

    # past: was -> were and vice versa
    elif token.tag_ == Tag.SIMPLE_PAST_VERB.value and token.lemma_ == 'be' and random.random() < p:
        new_form = 'were' if token.text.lower() == 'was' else 'was'
        new_form = new_form.title() if token.text.istitle() else new_form
        entities.append((len(new_sentence),
                         len(new_sentence) + len(new_form),
                         error_name))
        new_sentence += new_form + token.whitespace_

    else:
        new_sentence += token.text_with_ws

    return new_sentence, entities


class SubjectVerbAgreementWithSimpleNounErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_SIMPLE_NOUN.value

    def generate_from_doc(self, doc, p=0.5):

        new_sentence = ""
        entities = []
        relevant = False
        for token in doc:
            if token.text.startswith("'"):
                new_sentence += token.text_with_ws
            elif has_noun_subject(token):
                relevant = True
                new_sentence, entities = replace_verb(token, doc, self.name, new_sentence, entities, p)
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities, relevant


class SubjectVerbAgreementWithPronounErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_PRONOUN.value

    def generate_from_doc(self, doc, p=0.5):

        new_sentence = ""
        entities = []
        relevant = False
        for token in doc:
            if token.text.startswith("'"):
                new_sentence += token.text_with_ws
            elif has_pronoun_subject(token):
                relevant = True
                new_sentence, entities = replace_verb(token, doc, self.name, new_sentence, entities, p)
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities, relevant


class SubjectVerbAgreementWithIndefinitePronounErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_INDEFINITE.value

    def generate_from_doc(self, doc, p=0.5):

        new_sentence = ""
        entities = []
        relevant = False
        for token in doc:
            if token.text.startswith("'"):
                new_sentence += token.text_with_ws
            elif has_indefinite_subject(token):
                relevant = True
                new_sentence, entities = replace_verb(token, doc, self.name, new_sentence, entities, p)
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities, relevant


class SubjectVerbAgreementErrorGenerator(ErrorGenerator):

    name = GrammarError.SUBJECT_VERB_AGREEMENT.value

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) > 0:
                new_sentence += token.text_with_ws
            elif token.text.startswith("'"):
                new_sentence += token.text_with_ws
            else:
                # singular -> plural
                if token.tag_ == Tag.PRESENT_SING3_VERB.value:
                    if token.lemma_ == "be":
                        new_form = random.choice(["be", "are", "am"])
                        new_form = new_form.title() if token.text.istitle() else new_form
                    else:
                        new_form = token.lemma_
                        new_form = new_form.title() if token.text.istitle() else new_form

                    new_sentence += new_form + token.whitespace_
                    entities.append((token.idx, token.idx+len(new_form), self.name))

                # plural -> singular
                elif token.tag_ == Tag.PRESENT_OTHER_VERB.value:
                    if token.lemma_ == "be":
                        new_form = random.choice(["be", "is", "am"])
                        new_form = new_form.title() if token.text.istitle() else new_form
                    else:
                        new_form = token._.inflect(Tag.PRESENT_SING3_VERB.value)

                    if new_form is not None:
                        new_sentence += new_form + token.whitespace_
                        entities.append((token.idx, token.idx+len(new_form), self.name))
                    else:
                        new_sentence += token.text_with_ws
                else:
                    new_sentence += token.text_with_ws

        return new_sentence, entities


class IncorrectThirdPersonWithNegationErrorGenerator(ErrorGenerator):

    name = GrammarError.INCORRECT_NEGATIVE_VERB_WITH_A_SIMPLE_NOUN_SUBJECT.value

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) > 0:
                new_sentence += token.text_with_ws
            elif token.text.startswith("'"):
                new_sentence += token.text_with_ws
            elif token.tag_ == Tag.PRESENT_SING3_VERB.value and \
                    is_negated_with_contraction(token, doc) and \
                    has_noun_subject(token):
                new_form = token.lemma_ if token.lemma_ != "be" else "are"
                new_form = new_form.title() if token.text.istitle() else new_form
                new_sentence += new_form + token.whitespace_
                entities.append((token.idx, token.idx+len(new_form), self.name))
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities



class SubjectVerbAgreementWithInversionErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_INVERSION.value

    def generate_from_doc(self, doc, p=0.5):

        new_sentence = ""
        entities = []
        relevant = False
        for token in doc:
            if token.text.startswith("'"):
                new_sentence += token.text_with_ws
            elif (token.tag_ == Tag.PRESENT_SING3_VERB.value or
                  token.tag_ == Tag.PRESENT_OTHER_VERB.value or
                  token.tag_ == Tag.SIMPLE_PAST_VERB.value) and \
                    has_following_subject(token):
                relevant = True
                new_sentence, entities = replace_verb(token, doc, self.name, new_sentence, entities, p)
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities, relevant


class SubjectVerbAgreementWithNeitherNorErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_NEITHER_NOR.value

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) > 0:
                new_sentence += token.text_with_ws
            elif token.text.startswith("'"):
                new_sentence += token.text_with_ws
            elif token.tag_ == Tag.PRESENT_SING3_VERB.value and subject_has_neither(token):
                new_form = token.lemma_ if token.lemma_ != "be" else "are"
                new_sentence += new_form + token.whitespace_
                entities.append((token.idx, token.idx+len(new_form), self.name))
            elif token.tag_ == Tag.PRESENT_OTHER_VERB.value and subject_has_neither(token):
                new_form = token._.inflect(Tag.PRESENT_SING3_VERB.value)
                new_sentence += new_form + token.whitespace_
                entities.append((token.idx, token.idx + len(new_form), self.name))
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities


class SubjectVerbAgreementWithEitherOrErrorGenerator(ErrorGenerator):

    name = GrammarError.SVA_EITHER_OR.value

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) > 0:
                new_sentence += token.text_with_ws
            elif token.text.startswith("'"):
                new_sentence += token.text_with_ws
            elif token.tag_ == Tag.PRESENT_SING3_VERB.value and subject_has_either(token, doc):
                new_form = token.lemma_ if token.lemma_ != "be" else "are"
                new_sentence += new_form + token.whitespace_
                entities.append((token.idx, token.idx+len(new_form), self.name))
            elif token.tag_ == Tag.PRESENT_OTHER_VERB.value and subject_has_either(token, doc):
                new_form = token._.inflect(Tag.PRESENT_SING3_VERB.value)
                new_sentence += new_form + token.whitespace_
                entities.append((token.idx, token.idx + len(new_form), self.name))
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities


class SubjectVerbAgreementWithCollectiveNoun(ErrorGenerator):

    name = GrammarError.SVA_COLLECTIVE_NOUN.value

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        for token in doc:
            if token.tag_ == Tag.PRESENT_SING3_VERB.value:
                subject = get_subject(token)
                if subject is not None and subject.text.lower() in TokenSet.COLLECTIVE_NOUNS.value:
                    plural = get_plural(token)
                    new_sentence += plural + token.whitespace_
                    entities.append((token.idx, token.idx + len(plural), self.name))
                else:
                    new_sentence += token.text_with_ws
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities
import re
import random
import lemminflect

from spacy.tokens.token import Token

from quillgrammar.grammar.constants import GrammarError, Dependency, Tag
from quillnlp.grammar.myspacy import nlp


subject_pronoun_unigram_replacements = {
    "i": ["me", "my", "mine", "my's"],
    "you": ["your", "yours", "your's"],
    "he": ["him", "his"],
    "she": ["her", "hers", "her's"],
    "we": ["us", "our",	"ours", "our's"],
    "they":	["them", "their", "their's"]
}

subject_pronoun_bigram_replacements = {
    "you're": ["your", "your's", "yours"],
    "they're": ["their's", "theirs"]
}

object_pronoun_unigram_replacements = {
    "me": ["I", "I", "I", "I", "I's", "me's"],
    "him": ["he", "he", "he", "he", "he's", "him's"],
    "her": ["she", "she", "she", "she", "she's", "her's"],
    "us": ["we", "we", "we", "we", "us's"]
}

possessive_pronoun_unigram_replacements = {
    "my":	["I's", "me's", "mine", "I", "my's"],
    "your":	["you's", "yours", "you", "yous", "your's", "you're"],
    "his": ["he's",	"him's", "he", "his's"],
    "her":	["she's", "her's", "hers", "she", "shes"],
    "our":	["we's", "us's", "ours", "we", "wes", "our's"],
    "their": ["they's", "them's", "theirs", "they", "theys", "their's"],
    "mine":	["I's", "me's", "mine", "I", "my's", "my"],
    "yours": ["you's", "yours", "you", "yous", "your's", "you're", "your"],
    "hers":	["she's", "her's", "hers", "she", "shes", "her"],
    "ours":	["we's", "us's", "ours", "we", "wes", "our's", "our"],
    "theirs": ["they's", "them's", "theirs", "they", "theys", "their's", "they're", "their"]
}

their_unigram_replacements = {
    "their": ["they're", "there"],
    "there": ["they're", "their"],
}

their_bigram_replacements = {
    "they're": ["there", "their"]
}



Token.set_extension("replace", default=None)

def give_same_shape(reference_token, new_token):

    if reference_token.islower():
        return new_token.lower()
    elif reference_token.istitle():
        return new_token.title()
    elif reference_token.isupper():
        return new_token.upper()
    else:
        return new_token

class ErrorGenerator:

    def generate_from_doc(self, doc):
        pass

    def generate_from_text(self, text: str):
        return self.generate_from_doc(nlp(text))

    def replace(self, doc, target_tokens, replacement_token):
        # If the token is uppercase, the replacement token should be uppercase as well
        replacement_token = replacement_token.upper() if target_tokens[0].text.isupper() and len(target_tokens[0]) > 1 else replacement_token

        # If the token is capitalized, the replacement token should be capitalized
        replacement_token = replacement_token[0].upper() + replacement_token[1:] if target_tokens[0].text.istitle() else replacement_token
        
        # If the token is "I" and it is not at the beginning of the sentence,
        # the replacement token should be lowercased, unless it also starts with I
        if len(target_tokens) == 1 and target_tokens[0].i > 0 and target_tokens[0].text == "I" and not replacement_token.startswith("I"):
            replacement_token = replacement_token.lower()

        sentence = doc[:target_tokens[0].i].text_with_ws + replacement_token + target_tokens[-1].whitespace_ + doc[target_tokens[-1].i+1:].text
        entities = [(target_tokens[0].idx, target_tokens[0].idx+len(replacement_token), self.name)]

        return sentence, entities


class TokenReplacementErrorGenerator(ErrorGenerator):

    def __init__(self, replacement_map, error_name):
        self.replacement_map = replacement_map
        self.name = error_name

    def generate_from_doc(self, doc, add_word_to_label=False):

        # Pick the token that will be replaced
        candidates = [t for t in doc if t.text.lower() in self.replacement_map]
        if not candidates:
            return doc.text, [], False 

        target = random.choice(candidates)
        replacement = random.choice(self.replacement_map[target.text.lower()])
        
        new_sentence, entities = self.replace(doc, [target], replacement)
        return new_sentence, entities, True


class PronounReplacementErrorGenerator(ErrorGenerator):

    def __init__(self, unigram_replacement_map,
                 bigram_replacement_map,
                 dependency_test, pos, error_name):
        self.pos = pos
        self.dependency_test = dependency_test
        self.unigram_replacement_map = unigram_replacement_map
        self.bigram_replacement_map = bigram_replacement_map
        self.name = error_name

    def generate_from_doc(self, doc, add_word_to_label=False):

        candidates = []
        for i, token in enumerate(doc):
            if len(doc) > i + 1 and token.text_with_ws.lower() + doc[
                i + 1].text.lower() in self.bigram_replacement_map:
                candidates.append([token, doc[i+1]])

            elif token.text.lower() in self.unigram_replacement_map and \
                    (token.text.lower() not in self.pos or
                     token.tag_ == self.pos[token.text.lower()]) and \
                    self.dependency_test(token.dep_):
                candidates.append([token])

        if not candidates:
            return doc.text, [], False 

        target = random.choice(candidates)
        if len(target) == 2:
            combined_token = target[0].text_with_ws.lower() + target[1].text.lower()
            replacement_token = random.choice(self.bigram_replacement_map[combined_token])
        elif len(target) == 1:
            replacement_token = random.choice(self.unigram_replacement_map[target[0].text.lower()])

        new_sentence, entities = self.replace(doc, target, replacement_token)

        if add_word_to_label:
            entities[0][2] = self.name + f"- {token.text[0].upper() + token.text[1:].lower()} optimal"

        return new_sentence, entities, True


subject_pronoun_error_generator = PronounReplacementErrorGenerator(
    subject_pronoun_unigram_replacements,
    subject_pronoun_bigram_replacements,
    lambda x: x in set([Dependency.SUBJECT.value, Dependency.PASS_SUBJECT.value, Dependency.CLAUSAL_SUBJECT.value]),
    {},
    GrammarError.SUBJECT_PRONOUN.value
)

object_pronoun_error_generator = PronounReplacementErrorGenerator(
    object_pronoun_unigram_replacements,
    {},  # no bigram replacement for object pronouns
    lambda x: x not in set([Dependency.SUBJECT.value, Dependency.PASS_SUBJECT.value, Dependency.CLAUSAL_SUBJECT.value]),
    {"her": "PRP"},  # only replace "her" when it has a PRP tag (I see her)
    GrammarError.OBJECT_PRONOUN.value
)

possessive_pronoun_error_generator = PronounReplacementErrorGenerator(
    possessive_pronoun_unigram_replacements,
    {},  # no bigram replacement for object pronouns
    lambda x: True,
    {"her": "PRP$"},  # only replace "her" when it has a PRP$ tag (I see her car),
    GrammarError.POSSESSIVE_PRONOUN.value
)

their_error_generator = PronounReplacementErrorGenerator(
    their_unigram_replacements,
    their_bigram_replacements,
    lambda x: True,
    {},
    GrammarError.THEIR.value
)


class IncorrectIrregularPastErrorGenerator(ErrorGenerator):

    name = GrammarError.INCORRECT_IRREGULAR_PAST_TENSE.value

    def generate_from_doc(self, doc):

        exclude_tokens = set(["was", "did", "were"])

        candidates = [t for t in doc if t.tag_ == Tag.SIMPLE_PAST_VERB.value and not t.text.endswith("ed") 
                        and t.text not in exclude_tokens]
        if not candidates:
            return doc.text, [], False 

        target = random.choice(candidates)
        replacement = target.lemma_ + "d" if target.lemma_.endswith("e") else target.lemma_ + "ed"
        
        new_sentence, entities = self.replace(doc, [target], replacement)
        return new_sentence, entities, True


class IncorrectParticipleErrorGenerator(ErrorGenerator):

    name = GrammarError.INCORRECT_PARTICIPLE.value

    def generate_from_doc(self, doc):

        candidates = [t for t in doc if t.tag_ == Tag.PAST_PARTICIPLE_VERB.value and not t.text.endswith("ed")]
        if not candidates:
            return doc.text, [], False 
        
        target = random.choice(candidates)
        replacement = target.lemma_ + 'd' if target.lemma_.endswith('e') else target.lemma_ + 'ed'
        
        new_sentence, entities = self.replace(doc, [target], replacement)
        return new_sentence, entities, True


class IrregularPluralNounErrorGenerator(ErrorGenerator):

    name = GrammarError.IRREGULAR_PLURAL_NOUN.value
    exclude_tokens = set(["men", "women", "people"])

    def get_regular_plural(self, word):

        word = word.lower()

        if re.search('(s|ss|sh|ch|x|z|es)$', word):
            return word + "es"
        else:
            return word + "s"

    def generate_from_doc(self, doc, p=0.5):

        candidates = [t for t in doc if t.tag_ == Tag.PLURAL_NOUN.value if not t.text.lower() in self.exclude_tokens]
        if not candidates:
            return doc.text, [], False 

        target = random.choice(candidates)
        replacement = self.get_regular_plural(target.lemma_)

        new_sentence, entities = self.replace(doc, [target], replacement)
        return new_sentence, entities, True


class PluralPossessiveErrorGenerator(ErrorGenerator):

    name = GrammarError.PLURAL_VERSUS_POSSESSIVE_NOUNS.value

    def generate_from_doc(self, doc):

        plurals, possessives = [], []
        for token in doc: 
            if token.tag_ == 'NNS':
                plurals.append([token])
            elif token.i < len(doc) - 1 and token.tag_.startswith("NN") and \
                    doc[token.i + 1].tag_ == "POS":
                possessives.append([token, doc[token.i+1]])

        candidates = plurals + possessives
        if not candidates:
            return doc.text, [], False 

        target = random.choice(candidates)

        replacement = target[0].lemma_ + "'s" if len(target) == 1 else target[0]._.inflect('NNS')
        if not replacement:
            replacement = target[0].lemma + 's'  # cases like Ronaldo's, which are not known to pyinflect

        new_sentence, entities = self.replace(doc, target, replacement)
        return new_sentence, entities, True


        # text = ""
        # entities = []
        # skip_next = False
        # for token in doc:
        #     if skip_next:
        #         skip_next = False
        #         continue

        #     elif len(entities) > 0:
        #         text += token.text_with_ws
        #         continue

        #     # If the token is immediately followed by "n't" (no whitespace), skip
        #     # This avoids problems like wouldn't => wouldsn't, where the indices of the error
        #     # do not match a spaCy token
        #     elif token.i < len(doc) - 1 and token.text.lower() in PROBLEM_VERBS and \
        #             (doc[token.i + 1].text == "n't" or doc[token.i + 1].text == "not") \
        #             and not token.whitespace_:
        #         new_token = token.text

        #     elif token.tag_ == "NNS":
        #         new_token = token.lemma_ + "'s"
        #         error_type = self.name
        #     elif token.i < len(doc) - 1 and token.tag_.startswith("NN") and \
        #             doc[token.i + 1].tag_ == "POS":
        #         new_token = token._.inflect("NNS")
        #         if not new_token:
        #             new_token = token.lemma_ + "s"  # handle cases like Ronaldo's
        #         error_type = self.name
        #         skip_next = True
        #     else:
        #         new_token = token.text

        #     if new_token is None or new_token == token.text or len(entities) > 0:
        #         text += token.text_with_ws
        #         skip_next = False
        #     else:
        #         if token.text[0].isupper():
        #             new_token = new_token[0].upper() + new_token[1:]

        #         # Add a space to the text if it does not end in a space.
        #         # This solves problems like he's => hebe
        #         if len(text) > 0 and not text[-1].isspace():
        #             text += " "

        #         # The start index is the length of the text before
        #         # the new token is added
        #         start_index = len(text)

        #         # When replacing a possessive by a plural, we have to skip the next
        #         # token in the text ('s) and just add the whitespace that follows it.
        #         if skip_next:
        #             text += new_token + doc[token.i + 1].whitespace_
        #         else:
        #             text += new_token + token.whitespace_

        #         entities.append((start_index, start_index + len(new_token), error_type))

        # return text, entities



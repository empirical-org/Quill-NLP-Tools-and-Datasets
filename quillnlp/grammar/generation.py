from spacy.tokens.token import Token

from quillgrammar.grammar.constants import GrammarError
from quillnlp.grammar.myspacy import nlp

Token.set_extension("replace", default=None)


class ErrorGenerator:

    def generate_from_doc(self, doc):
        pass

    def generate_from_text(self, text: str):
        return self.generate_from_doc(nlp(text))


class TokenReplacementErrorGenerator:

    def __init__(self, replacement_map, error_name):
        self.replacement_map = replacement_map
        self.error_name = error_name

    def generate_from_doc(self, doc):

        new_sentence = ""
        entities = []
        for token in doc:
            if len(entities) > 0:
                new_sentence += token.text_with_ws
            elif token.text.lower() in self.replacement_map:
                replacement_token = self.replacement_map[token.text.lower()]

                # If the token is allcaps, the replacement token should be allcaps
                if token.text.upper() == token.text:
                    replacement_token = replacement_token.upper()

                # If the token is capitalized, the replacement token should be capitalized
                elif token.text[0].upper() == token.text[0]:
                    replacement_token = replacement_token[0].upper() + replacement_token[1:]
                new_sentence += replacement_token + token.whitespace_
                entities.append((token.idx, token.idx+len(replacement_token), self.error_name))
            else:
                new_sentence += token.text_with_ws

        return new_sentence, entities

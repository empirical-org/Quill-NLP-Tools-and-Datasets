import spacy
from spacy.tokens.token import Token

nlp = spacy.load("en")
Token.set_extension("replace", default=None)


class ErrorGenerator:

    def generate_from_doc(self, doc):
        pass

    def generate_from_text(self, text: str):
        return self.generate_from_doc(nlp(text))
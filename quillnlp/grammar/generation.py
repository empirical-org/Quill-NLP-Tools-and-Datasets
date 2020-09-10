from spacy.tokens.token import Token

from quillnlp.grammar.myspacy import nlp

Token.set_extension("replace", default=None)


class ErrorGenerator:

    def generate_from_doc(self, doc):
        pass

    def generate_from_text(self, text: str):
        return self.generate_from_doc(nlp(text))
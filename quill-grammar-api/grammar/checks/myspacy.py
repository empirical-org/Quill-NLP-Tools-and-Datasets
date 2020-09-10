import os
import spacy
from spacy.tokens.doc import Doc

from grammar.utils import Error

spacy_path = os.environ["SPACY_GRAMMAR_PATH"]
nlp = spacy.load(spacy_path)

ERROR_TYPES = []


class SpaCyGrammarChecker:

    def __init__(self):
        self.unclassified = False
        self.name = "spaCy"

    def check(self, doc: Doc, prompt=""):
        errors = []
        for entity in doc.ents:
            #if entity.label_ in ERROR_TYPES:
            error = Error(text=entity.text,
                          index=entity.start_char,
                          error_type=entity.label_,
                          model=self.name)

            errors.append(error)

        return errors

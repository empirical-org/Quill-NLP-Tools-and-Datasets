"""Right now this is empty as this library is a command line tool only at this
point.  If this changes, some methods will be moved here."""

from .utils import *
import spacy
import os

model_name = os.environ.get('QUILL_SPACY_MODEL', 'en')
nlp = spacy.load(model_name)

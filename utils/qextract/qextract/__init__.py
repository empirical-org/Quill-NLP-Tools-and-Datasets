LANGUAGE_TOOL = os.path.join(__location__, 'vendor', 'LanguageTool-4.1',
 14     ¦   'languagetool-commandline.jar')"""Right now this is empty as this library is a command line tool only at this
point.  If this changes, some methods will be moved here."""

from .utils import *
import spacy
import os

model_name = os.environ.get('QUILL_SPACY_MODEL', 'en')
nlp = spacy.load(model_name)

# relative path resolution 
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

LANGUAGE_TOOL = os.path.join(__location__, 'vendor', 'LanguageTool-4.1',
        'languagetool-commandline.jar')

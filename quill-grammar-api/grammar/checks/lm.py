import re

from spacy.tokens import Doc

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

from grammar.constants import GrammarError, POS
from grammar.checks.myspacy import nlp
from grammar.utils import Error

PRESENT_VERB_TAGS = set(["VBZ", "VB", "VBP"])
OTHER_VERB_TAGS = set(["VBD", "VBN"])
ALL_VERB_TAGS = PRESENT_VERB_TAGS | OTHER_VERB_TAGS

BE_FORMS = set(["be", "am", "are", "is"])
CONTRACTED_BE_FORMS = set(["'s", "'m", "'re"])
TARGET_TOKENS = {"then": ["than"],
                 "than": ["then"],
                 "i": ["me", "my", "mine"],
                 "you": ["your", "yours"],
                 "he": ["him", "his"],
                 "she": ["her", "hers"],
                 "it": ["its"],
                 "we": ["us", "our", "ours"],
                 "they": ["them", "their", "theirs"],
                 "me": ["i"],
                 "my": ["i"],
                 "mine": ["i"],
                 "your": ["you"],
                 "yours": ["you"],
                 "him": ["he"],
                 "his": ["he"],
                 "her": ["she"],
                 "hers": ["she"],
                 "its": ["it"],
                 "us": ["we"],
                 "our": ["we"],
                 "ours": ["we"],
                 "them": ["they"],
                 "their": ["they"],
                 "theirs": ["they"],
                 "an": ["a"],
                 "a": ["an"],
                 "woman": ["women"],
                 "women": ["woman"],
                 "men": ["man"],
                 "man": ["men"],
                 "child": ["children"],
                 "children": ["child"],
                 "been": ["is", "are", "was"],
                 ".": ["?"],
                 ";": ["?"],
                 ":": ["?"],
                 ",": ["?"],
                 "!": ["?"]}

TOKENS2ERRORS = {"then": GrammarError.THAN_THEN.value,
                 "than": GrammarError.THAN_THEN.value,
                 "i": GrammarError.OBJECT_PRONOUN.value,
                 "you": GrammarError.OBJECT_PRONOUN.value,
                 "he": GrammarError.OBJECT_PRONOUN.value,
                 "she": GrammarError.OBJECT_PRONOUN.value,
                 "we": GrammarError.OBJECT_PRONOUN.value,
                 "they": GrammarError.OBJECT_PRONOUN.value,
                 "me": GrammarError.SUBJECT_PRONOUN.value,
                 "my": GrammarError.SUBJECT_PRONOUN.value,
                 "mine": GrammarError.SUBJECT_PRONOUN.value,
                 "your": GrammarError.SUBJECT_PRONOUN.value,
                 "yours": GrammarError.SUBJECT_PRONOUN.value,
                 "him": GrammarError.SUBJECT_PRONOUN.value,
                 "his": GrammarError.SUBJECT_PRONOUN.value,
                 "her": GrammarError.SUBJECT_PRONOUN.value,
                 "hers": GrammarError.SUBJECT_PRONOUN.value,
                 "its": GrammarError.SUBJECT_PRONOUN.value,
                 "it": GrammarError.SUBJECT_PRONOUN.value,
                 "us": GrammarError.SUBJECT_PRONOUN.value,
                 "our": GrammarError.SUBJECT_PRONOUN.value,
                 "ours": GrammarError.SUBJECT_PRONOUN.value,
                 "them": GrammarError.SUBJECT_PRONOUN.value,
                 "their": GrammarError.SUBJECT_PRONOUN.value,
                 "theirs": GrammarError.SUBJECT_PRONOUN.value,
                 "a": GrammarError.ARTICLE.value,
                 "an": GrammarError.ARTICLE.value,
                 "been": GrammarError.PASSIVE_WITH_INCORRECT_BE.value,
                 "man": GrammarError.MAN_MEN.value,
                 "men": GrammarError.MAN_MEN.value,
                 "woman": GrammarError.WOMAN_WOMEN.value,
                 "women": GrammarError.WOMAN_WOMEN.value,
                 "child": GrammarError.CHILD_CHILDREN.value,
                 "children": GrammarError.CHILD_CHILDREN.value,
                 ".": GrammarError.QUESTION_MARK.value,
                 ":": GrammarError.QUESTION_MARK.value,
                 ";": GrammarError.QUESTION_MARK.value,
                 ",": GrammarError.QUESTION_MARK.value,
                 "!": GrammarError.QUESTION_MARK.value}


synonyms = {"am": "'m", "are": "'re", "is": "'s", "have": "'ve",
            "will": "'ll", "would": "'d", "wo": "will", "ca": "can"}
synonyms_reversed = {v: k for k, v in synonyms.items()}
synonyms.update(synonyms_reversed)

TARGET_OPEN_TAG = "<target>"
TARGET_CLOSE_TAG = "</target>"


def make_request_from_sentence(sentence: str, prompt: str = ""):
    doc = nlp(sentence)
    return make_request_from_doc(doc, prompt)


def make_request_from_doc(doc: Doc, prompt: str = ""):
    request = {
        "sentence": doc.text,
        "targets": []
    }

    prompt_char_length = len(prompt)

    for token in doc:

        if token.idx < prompt_char_length:
            continue

        if token.text.lower() in TARGET_TOKENS:
            alternative_forms = TARGET_TOKENS.get(token.text.lower())
        elif token.text.lower() in BE_FORMS:
            alternative_forms = set([f for f in BE_FORMS if f != token.text.lower()])
            alternative_forms.update([synonyms[f] for f in alternative_forms if f in synonyms])
        elif token.text.lower() in CONTRACTED_BE_FORMS:
            alternative_forms = set([f for f in CONTRACTED_BE_FORMS if f != token.text.lower()])
            alternative_forms.update([synonyms[f] for f in alternative_forms if f in synonyms])
        elif token.tag_ in PRESENT_VERB_TAGS:
            alternative_forms = set(
                [token._.inflect(tag) for tag in PRESENT_VERB_TAGS])
        elif token.tag_ in OTHER_VERB_TAGS:
            alternative_forms = set(
                [token._.inflect(tag) for tag in OTHER_VERB_TAGS])
        else:
            alternative_forms = set()

        if token.text.lower() in alternative_forms:
            alternative_forms.remove(token.text.lower())

        if alternative_forms:
            request["targets"].append({
                "token": token.text.lower(),
                "start": token.idx,
                "alternatives": list(alternative_forms),
            })

    return request


def create_masked_sentences(sentence, tokenizer):
    for match in re.finditer(f"{TARGET_OPEN_TAG}.+?{TARGET_CLOSE_TAG}", sentence):
        target_token = match.group(0).replace(TARGET_OPEN_TAG, "").replace(TARGET_CLOSE_TAG, "")
        masked_sentence = sentence[:match.start()] + tokenizer.mask_token + sentence[match.end():]
        masked_sentence = masked_sentence.replace(TARGET_OPEN_TAG, "").replace(TARGET_CLOSE_TAG, "")
        yield {"token": target_token,
               "masked_sentence": masked_sentence,
               "alternatives": TARGET_TOKENS[target_token.lower()]}


class GoogleAIModelChecker:

    def __init__(self):
        self.project = "grammar-api"
        self.model_name = "grammar"
        self.version_name = "v2"
        self.unclassified = True  # indicates that the errors have to be classified by type in postprocessing
        self.name = "lm"

    def check(self, doc, prompt):

        request = make_request_from_doc(doc, prompt)

        # JSON format the requests
        request_data = {'instances': [request]}

        # Authenticate and call CMLE prediction API
        credentials = GoogleCredentials.get_application_default()
        api = discovery.build('ml', 'v1', credentials=credentials,
                              discoveryServiceUrl='https://storage.googleapis.com/cloud-ml/discovery/ml_v1_discovery.json')

        parent = 'projects/%s/models/%s/versions/%s' % (self.project, self.model_name, self.version_name)

        response = api.projects().predict(body=request_data, name=parent).execute()
        prediction = response["predictions"][0]

        if "start" in prediction:
            error_type = TOKENS2ERRORS.get(prediction["original_token"].lower(),
                                           GrammarError.SUBJECT_VERB_AGREEMENT.value)

            return [Error(prediction["original_token"],
                          prediction["start"],
                          error_type=error_type,
                          predicted_token=prediction["predicted_token"],
                          predicted_sentence=prediction["correct"],
                          model=self.name)]

        return None


class OfflineLMChecker():

    def __init__(self, path: str):
        from aimodel.albert_predictor import BertPredictor
        self.model = BertPredictor.from_path(path)
        self.unclassified = True  # indicates that the errors have to be classified by type in postprocessing
        self.name = "lm"

    def check(self, doc, prompt):

        instance = make_request_from_doc(doc, prompt)
        prediction = self.model.correct_instance(instance)

        if "start" in prediction:
            error_type = TOKENS2ERRORS.get(prediction["original_token"].lower(),
                                           GrammarError.SUBJECT_VERB_AGREEMENT.value)

            return [Error(prediction["original_token"],
                          prediction["start"],
                          error_type=error_type,
                          predicted_token=prediction["predicted_token"],
                          predicted_sentence=prediction["correct"],
                          model=self.name)]

        return None

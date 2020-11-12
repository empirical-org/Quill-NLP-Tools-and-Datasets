from spacy.tokens import Doc

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

from ..constants import GrammarError, AGREEMENT_ERRORS, POS
from ..checks.myspacy import nlp
from ..utils import Error

PRESENT_VERB_TAGS = set(["VBZ", "VB", "VBP"])
OTHER_VERB_TAGS = set(["VBD", "VBN"])
ALL_VERB_TAGS = PRESENT_VERB_TAGS | OTHER_VERB_TAGS

BE_FORMS = set(["be", "am", "are", "is"])
CONTRACTED_BE_FORMS = set(["'s", "'m", "'re"])

ERRORS = {
    GrammarError.THAN_THEN.value:
        {
            "then": ["than"],
            "than": ["then"]
        },
    GrammarError.OBJECT_PRONOUN.value:
        {
            "i": ["me", "my", "mine"],
            "you": ["your", "yours"],
            "he": ["him", "his"],
            "she": ["her", "hers"],
            "we": ["us", "our", "ours"],
            "they": ["them", "their", "theirs"]
        },
    GrammarError.SUBJECT_PRONOUN.value:
        {
            "me": ["i"],
            "my": ["i"],
            "mine": ["i"],
            "your": ["you"],
            "yours": ["you"],
            "him": ["he"],
            "his": ["he"],
            "her": ["she"],
            "hers": ["she"],
            "it": ["its"],
            "its": ["it"],
            "us": ["we"],
            "our": ["we"],
            "ours": ["we"],
            "them": ["they"],
            "their": ["they"],
            "theirs": ["they"]
        },
#    GrammarError.ARTICLE.value:  # Commented out because Albert is not good at this.
#        {
#            "an": ["a"],
#            "a": ["an"]
#        },
    GrammarError.PASSIVE_WITH_INCORRECT_BE.value:
        {
            "been": ["is", "are", "was"]
        },
    GrammarError.MAN_MEN.value:
        {
            "men": ["man"],
            "man": ["men"]
        },
    GrammarError.WOMAN_WOMEN.value:
        {
            "woman": ["women"],
            "women": ["woman"]
        },
    GrammarError.CHILD_CHILDREN.value:
        {
            "child": ["children"],
            "children": ["child"]
        },
    GrammarError.QUESTION_MARK.value:
        {
            ".": ["?"],
            ";": ["?"],
            ":": ["?"],
            ",": ["?"],
            "!": ["?"]
        }
}


TARGET_OPEN_TAG = "<target>"
TARGET_CLOSE_TAG = "</target>"


def make_request_from_sentence(sentence: str, prompt: str = ""):
    doc = nlp(sentence)
    return make_request_from_doc(doc, prompt)


def make_request_from_doc(doc: Doc, prompt: str = "", config={}):
    request = {
        "sentence": doc.text,
        "targets": []
    }

    prompt_char_length = len(prompt)

    catch_agreement_errors = False
    for error in config["errors"]:
        if config["errors"][error] == 1 and error in AGREEMENT_ERRORS:
            catch_agreement_errors = True

    for token in doc:

        if token.idx < prompt_char_length:
            continue

        for error in ERRORS:

            # For the question-mark error, we only check sentence-final punctuation.
            if error == GrammarError.QUESTION_MARK.value and token != doc[-1]:
                continue

            if error in config["errors"] and config["errors"][error] == 1:

                # If the token is among the target tokens for an error,
                # fetch the alternatives.
                if token.text.lower() in ERRORS[error]:

                    # For subject pronouns errors, we only consider cases where the pronoun has
                    # a verb as its head, in order to exclude cases like "my mother".
                    if error == GrammarError.SUBJECT_PRONOUN.value and not token.head.pos_ == POS.VERB.value:
                        continue

                    alternative_forms = ERRORS[error].get(token.text.lower())
                    request["targets"].append({
                            "token": token.text.lower(),
                            "tag": token.tag_,
                            "start": token.idx,
                            "alternatives": list(alternative_forms),
                            "error_type": error
                    })

        if catch_agreement_errors:

            # If the token is a form of "be",
            # the alternatives are the other forms of be
            if token.text.lower() in BE_FORMS and token.tag_ in PRESENT_VERB_TAGS:
                alternative_forms = set([f for f in BE_FORMS if f != token.text.lower()])

            # If the token is a contracted form of "be",
            # the alternatives are the other forms of be
            elif token.text.lower() in CONTRACTED_BE_FORMS and token.tag_ in PRESENT_VERB_TAGS:
                alternative_forms = set([f for f in CONTRACTED_BE_FORMS if f != token.text.lower()])

            # If the token is a present verb,
            # the alternatives are the other present forms of the same verb
            elif token.tag_ in PRESENT_VERB_TAGS:
                alternative_forms = set(
                    [token._.inflect(tag) for tag in PRESENT_VERB_TAGS])

            # If the token is a past or participle form of a verb
            # the alternatives are the other past or participle forms of the same verb
            elif token.tag_ in OTHER_VERB_TAGS:
                alternative_forms = set(
                    [token._.inflect(tag) for tag in OTHER_VERB_TAGS])

            # In all other cases, we don't have any alternatives
            else:
                alternative_forms = set()

            # If the token itself has ended up in the alternative forms, remove it
            # (for example when past and participle are the same)
            if token.text.lower() in alternative_forms:
                alternative_forms.remove(token.text.lower())

            # If any alternative forms remain, add this potential error
            # to the request

            if alternative_forms:
                request["targets"].append({
                    "token": token.text.lower(),
                    "tag": token.tag_,
                    "start": token.idx,
                    "alternatives": list(alternative_forms),
                    "error_type": GrammarError.SUBJECT_VERB_AGREEMENT.value
                })

    import json
    # print(json.dumps(request, indent=4))

    return request


# def create_masked_sentences(sentence, tokenizer):
#     for match in re.finditer(f"{TARGET_OPEN_TAG}.+?{TARGET_CLOSE_TAG}", sentence):
#         target_token = match.group(0).replace(TARGET_OPEN_TAG, "").replace(TARGET_CLOSE_TAG, "")
#         masked_sentence = sentence[:match.start()] + tokenizer.mask_token + sentence[match.end():]
#         masked_sentence = masked_sentence.replace(TARGET_OPEN_TAG, "").replace(TARGET_CLOSE_TAG, "")
#         yield {"token": target_token,
#                "masked_sentence": masked_sentence,
#                "alternatives": TARGET_TOKENS[target_token.lower()]}


class GoogleAIModelChecker:

    candidate_checks = set(ERRORS.keys()) | AGREEMENT_ERRORS

    def __init__(self, config):
        self.project = "grammar-api"
        self.model_name = "grammar"
        self.version_name = "v2"
        self.unclassified = True  # indicates that the errors have to be classified by type in postprocessing
        self.name = "lm"
        self.config = config

    def check(self, doc, prompt):

        request = make_request_from_doc(doc, prompt, self.config)

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

            return [Error(prediction["original_token"],
                          prediction["start"],
                          error_type=prediction["error_type"],
                          predicted_token=prediction["predicted_token"],
                          predicted_sentence=prediction["correct"],
                          model=self.name)]

        return None


class OfflineLMChecker:

    candidate_checks = set(ERRORS.keys()) | AGREEMENT_ERRORS

    def __init__(self, path: str, config):
        from aimodel.albert_predictor import BertPredictor
        self.model = BertPredictor.from_path(path)
        self.unclassified = True  # indicates that the errors have to be classified by type in postprocessing
        self.name = "lm"
        self.config = config

        print("Initialized LM-based Error Check for these errors:")
        for error_check in self.candidate_checks:
            if error_check in self.config["errors"] and \
                    self.config["errors"][error_check] > 0:
                print(f"[x] {error_check}")
            else:
                print(f"[ ] {error_check}")

    def check(self, doc, prompt):

        instance = make_request_from_doc(doc, prompt, self.config)
        prediction = self.model.correct_instance(instance)

        if "start" in prediction:

            return [Error(prediction["original_token"],
                          prediction["start"],
                          error_type=prediction["error_type"],
                          predicted_token=prediction["predicted_token"],
                          predicted_sentence=prediction["correct"],
                          model=self.name)]

        return None

import time

from .checks.rules import RuleBasedGrammarChecker, GrammarError
from .checks.lm import GoogleAIModelChecker, OfflineLMChecker
from .checks.myspacy import SpaCyGrammarChecker
from .postprocess import classify_error
from .checks.myspacy import nlp


class GrammarPipeline:

    def __init__(self, config={}):
        self.nlp = nlp
        self.config = config
        self.rules = RuleBasedGrammarChecker(config)
        self.supervised = SpaCyGrammarChecker(config)
#        self.unsupervised = GoogleAIModelChecker()
        # self.unsupervised = OfflineLMChecker("/samba/public/models/albert-large/", config)
        # self.pipeline = [self.rules, self.supervised, self.unsupervised]
        self.pipeline = [self.rules, self.supervised]

    def check(self, sentence: str, prompt: str = ""):

        doc = self.nlp(sentence)
        errors = []
        for pipe in self.pipeline:

            pipe_errors = pipe.check(doc, prompt)
            classified_pipe_errors = []
            for error in pipe_errors:
                if error.type == GrammarError.SUBJECT_VERB_AGREEMENT.value:
                    classified_error = classify_error(error, self.config)
                    if classified_error is not None:
                        classified_pipe_errors.append(error)
                else:
                    classified_pipe_errors.append(error)

                pipe_errors = classified_pipe_errors

            if pipe_errors:
                errors.extend(pipe_errors)

        for error in errors:
            error.set_precedence(self.config)

        errors.sort(reverse=True)

        return errors

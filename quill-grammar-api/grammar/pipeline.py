from grammar.checks.rules import RuleBasedGrammarChecker
from grammar.checks.lm import GoogleAIModelChecker, OfflineLMChecker
from grammar.checks.myspacy import SpaCyGrammarChecker
from grammar.postprocess import classify_error
from grammar.checks.myspacy import nlp


class GrammarPipeline:

    def __init__(self):
        self.nlp = nlp
        self.rules = RuleBasedGrammarChecker()
        self.supervised = SpaCyGrammarChecker()
        self.unsupervised = GoogleAIModelChecker()
        self.unsupervised = OfflineLMChecker("/samba/public/models/albert-large/")
        self.pipeline = [self.rules, self.supervised, self.unsupervised]

    def check(self, sentence: str, prompt: str = ""):

        doc = self.nlp(sentence)
        errors = []
        for pipe in self.pipeline:
            pipe_errors = pipe.check(doc, prompt)
            if pipe.unclassified and pipe_errors:
                pipe_errors = [classify_error(error) for error in pipe_errors]

            if pipe_errors:
                errors.extend(pipe_errors)

        errors.sort(reverse=True)

        return errors

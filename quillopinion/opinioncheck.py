import yaml
import spacy

from collections import namedtuple

from quillgrammar.grammar.constants import Tag, Dependency

nlp = spacy.load("en_core_web_sm")

Opinion = namedtuple("Opinion", ["type", "start", "end", "match", "precedence"])


class KeywordCheck:

    def __init__(self, config):
        self.config = config
        self.nlp = nlp
        self.checks = [
            "First-Person Opinionated Phrase Keyword Check",
            "First-Person Reference Keyword Check",
            "Second-Person Reference Keyword Check",
            "Common Opinionated Phrases Keyword Check",
            "Using Maybe",
            "Using Perhaps",
            "Using Please"
        ]

        self.checks_with_tokens = []
        for check in self.checks:
            tokenized_phrases_for_check = []
            phrases = self.config[check]
            for phrase in phrases:
                tokens = tuple([t.text.lower() for t in self.nlp(phrase)])
                tokenized_phrases_for_check.append(tokens)

            self.checks_with_tokens.append((check, tokenized_phrases_for_check))

    def check_from_text(self, sentence: str, prompt: str):

        def lowercase(token: str) -> str:
            if token == "US":
                return token
            else:
                return token.lower()

        prompt_length = len(prompt)+1
        response = sentence[len(prompt)+1:]
        doc = self.nlp(response)

        # Get all possible ngrams from the sentence, together with their
        # start and end index
        ngrams = {}
        for length in range(1, len(doc) + 1):
            for start in range(0, len(doc) + 1 - length):
                ngram = doc[start:start+length]
                ngram_strings = [lowercase(token.text) for token in ngram]
                ngram_start = ngram[0].idx
                ngram_end = ngram[-1].idx + len(ngram[-1])
                ngrams[tuple(ngram_strings)] = (ngram_start, ngram_end)

        # Check if any of the opinionated phrases is among the ngrams
        feedback = []
        for check_name, tokenized_phrases in self.checks_with_tokens:
            for tokenized_phrase in tokenized_phrases:
                if tokenized_phrase in ngrams:
                    start_idx = prompt_length+ngrams[tokenized_phrase][0]
                    end_idx = prompt_length+ngrams[tokenized_phrase][1]

                    precedence = self.config["precedence"][check_name]

                    feedback.append(Opinion(check_name, start_idx, end_idx,
                                    sentence[start_idx:end_idx], precedence))

        return feedback


class ModalCheck:

    def __init__(self, config):
        self.name = "Modal Check"
        self.config = config
        self.checks = [
            "Using Should",
            "Using Must",
            "Using Need",
            "Using Ought"
        ]

        self.modals = {}
        for check in self.checks:
            self.modals[config[check][0]] = check

        self.nlp = nlp
        self.exceptions = set(["according"])

    def check_from_text(self, sentence: str, prompt: str):

        prompt_length = len(prompt)+1
        response = sentence[prompt_length:]
        doc = self.nlp(response)

        feedback = []
        for token in doc:
            if token.text.lower() in self.exceptions:
                return None
            elif token.lemma_.lower() in self.modals:

                if token.tag_ == "VBD":
                    continue

                # if "ought" and "need" are "ROOT", they express an opinion
                elif token.dep_ == "ROOT":
                    start_idx = prompt_length+token.idx
                    end_idx = prompt_length+token.idx+len(token)

                    check_name = self.modals.get(token.lemma_.lower())
                    precedence = self.config["precedence"].get(check_name)

                    feedback.append(Opinion(check_name, start_idx, end_idx,
                                    sentence[start_idx:end_idx], precedence))

                # if "should" and "must" are "aux" and their head is "ROOT",
                # they express an opinion
                elif token.dep_ == Dependency.AUX.value and token.head.dep_ == Dependency.ROOT.value:
                    start_idx = prompt_length+token.idx
                    end_idx = prompt_length+token.idx+len(token)

                    check_name = self.modals.get(token.lemma_.lower())
                    precedence = self.config["precedence"].get(check_name)

                    feedback.append(Opinion(check_name, start_idx, end_idx,
                                            sentence[start_idx:end_idx], precedence))

        return feedback


class CommandCheck:

    def __init__(self, config):
        self.name = "Command Check"
        self.config = config
        self.modals = set(["should", "would", "ought", "must"])
        self.nlp = nlp
        self.exceptions = set()

    def check_from_text(self, sentence: str, prompt: str):

        prompt_length = len(prompt)+1
        response = sentence[prompt_length:]
        doc = self.nlp(response)

        feedback = []
        # Only identify commands in so responses
        if not prompt.strip().endswith(" so"):
            return []

        if (doc[0].tag_ == Tag.INFINITIVE.value or
            doc[0].tag_ == Tag.PRESENT_OTHER_VERB.value) \
                and doc[0].text.lower() not in self.modals:
            start_idx = prompt_length + doc[0].idx
            end_idx = prompt_length + doc[0].idx + len(doc[0])

            precedence = self.config["precedence"][self.name]
            feedback.append(Opinion(self.name, start_idx,
                            end_idx, doc[0].text, precedence))

        return feedback


class OpinionCheck:

    def __init__(self):
        with open("quillopinion/opinion.yaml") as i:
            config = yaml.load(i, Loader=yaml.FullLoader)

        self.checks = [
            KeywordCheck(config),
            ModalCheck(config),
            CommandCheck(config)
        ]

    def check_from_text(self, sentence: str, prompt: str):
        all_feedback = []
        for check in self.checks:
            feedback = check.check_from_text(sentence, prompt)
            if feedback is not None:
                all_feedback.extend(feedback)

        all_feedback.sort(key=lambda x: -x.precedence)

        return all_feedback


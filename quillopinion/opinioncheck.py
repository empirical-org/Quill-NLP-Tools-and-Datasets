import yaml
import spacy

from collections import namedtuple

nlp = spacy.load("en")

Opinion = namedtuple("Opinion", ["type", "start", "end", "match"])


class KeywordCheck:

    def __init__(self, config):
        self.config = config
        self.nlp = nlp
        self.checks = [
            ("First-person opinionated phrase keyword check", ["phrases"]),
            ("First-Person Reference Keyword Check", ["personal pronouns",
                                                      "possessive pronouns",
                                                      "reflexive pronouns"]),
            ("Second-Person Reference Keyword Check", ["second-person pronouns"]),
            ("Common Opinionated Phrases Keyword Check", ["opinionated phrases"]),
            ("Using Maybe", ["maybe"]),
            ("Using Perhaps", ["perhaps"]),
            ("Using Please", ["please"])
        ]

        self.checks_with_tokens = []
        for check, keys in self.checks:
            tokenized_phrases_for_check = []
            for key in keys:
                phrases = self.config[key]
                for phrase in phrases:
                    tokens = tuple([t.text.lower() for t in self.nlp(phrase)])
                    tokenized_phrases_for_check.append(tokens)

            self.checks_with_tokens.append((check, tokenized_phrases_for_check))

    def check(self, sentence, prompt):

        prompt_length = len(prompt)+1
        response = sentence[len(prompt)+1:].lower()
        doc = self.nlp(response)

        # Get all possible ngrams from the sentence, together with their
        # start and end index
        ngrams = {}
        for length in range(1, len(doc) + 1):
            for start in range(0, len(doc) + 1 - length):
                ngram = doc[start:start+length]
                ngram_strings = [token.text.lower() for token in ngram]
                ngram_start = ngram[0].idx
                ngram_end = ngram[-1].idx + len(ngram[-1])
                ngrams[tuple(ngram_strings)] = (ngram_start, ngram_end)

        # Check if any of the opinionated phrases is among the ngrams
        for check_name, tokenized_phrases in self.checks_with_tokens:
            for tokenized_phrase in tokenized_phrases:
                if tokenized_phrase in ngrams:
                    start_idx = prompt_length+ngrams[tokenized_phrase][0]
                    end_idx = prompt_length+ngrams[tokenized_phrase][1]
                    return Opinion(check_name, start_idx, end_idx,
                                   sentence[start_idx:end_idx])

        return None


class ModalCheck:

    def __init__(self, config):
        self.name = "Modal Check"
        self.config = config
        self.modals = set(self.config["modals"])
        self.nlp = nlp

    def check(self, sentence, prompt):

        prompt_length = len(prompt)+1
        response = sentence[prompt_length:]
        doc = self.nlp(response)

        for token in doc:
            if token.text.lower() in self.modals:

                # if "ought" and "need" are "ROOT", they express an opinion
                if token.dep_ == "ROOT":
                    start_idx = prompt_length+token.idx
                    end_idx = prompt_length+token.idx+len(token)
                    return Opinion(self.name, start_idx, end_idx,
                                   sentence[start_idx:end_idx])

                # if "should" and "must" are "aux" and their head is "ROOT",
                # they express an opinion
                elif token.dep_ == "aux" and token.head.dep_ == "ROOT":
                    start_idx = prompt_length+token.idx
                    end_idx = prompt_length+token.idx+len(token)
                    return Opinion(self.name, start_idx, end_idx,
                                   sentence[start_idx:end_idx])


class OpinionCheck:

    def __init__(self):
        with open("quillopinion/opinion.yaml") as i:
            config = yaml.load(i, Loader=yaml.FullLoader)
        self.checks = [
            KeywordCheck(config),
            ModalCheck(config)
        ]

    def check(self, sentence, prompt):
        all_feedback = []
        for check in self.checks:
            feedback = check.check(sentence, prompt)
            if feedback is not None:
                all_feedback.append(feedback)

        return all_feedback


from .precedence import error_precedence


class Error:

    def __init__(self, text: str, index: int, error_type: str,
                 predicted_token: str = None,
                 predicted_sentence: str = None,
                 subject: str = None,
                 model: str = None):

        self.text = text
        self.index = index
        self.type = error_type
        self.predicted_token = predicted_token
        self.predicted_sentence = predicted_sentence
        self.subject = subject
        self.model = model
        self.score = error_precedence.get(self.type, 0)

    def __str__(self):
        return "Error(text: {}, type: {}, model: {}, score: {})".format(self.text, self.type, self.model, self.score)

    def __repr__(self):
        return "Error(text: {}, type: {}, model: {}, score: {})".format(self.text, self.type, self.model, self.score)

    def __lt__(self, other):
        return self.score < other.score

    def set_type(self, new_type):
        self.type = new_type
        self.score = error_precedence.get(self.type, 0)

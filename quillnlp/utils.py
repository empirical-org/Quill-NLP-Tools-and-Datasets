import re


def detokenize(s):
    """ Detokenize a string by removing spaces before punctuation."""
    print(s)
    s = re.sub("\s+([;:,\.\?!])", "\\1", s)
    s = re.sub("\s+(n't)", "\\1", s)
    return s


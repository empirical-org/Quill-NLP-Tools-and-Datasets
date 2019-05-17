import re


def detokenize(s):
    """ Detokenize a string by removing spaces before punctuation."""
    print(s)
    s = re.sub("\s+([;:,\.\?!])", "\\1", s)
    s = re.sub("\s+(n't)", "\\1", s)
    return s


import re


def extract_referents_from_xml_tagged_strings(strings):
    re_tagged_referent = re.compile(
        r"<ref[ ]+id=(?P<id>(\?|-?\d+))[ ]*>(?P<string>.+?)</ref>")
    for string in strings:
        # print(string)
        spans = []
        s_scrubbed = string
        while True:
            m = re_tagged_referent.search(s_scrubbed)
            if not m:
                break
            matched_string = m.group("string")
            matched_id = m.group("id")
            s_scrubbed = s_scrubbed[:m.start(0)] + matched_string + s_scrubbed[m.end(0):]
            spans.append({"start": m.start(),
                          "end": m.start() + len(matched_string),
                          "str_": matched_string,
                          "id": matched_id})
        print(spans)
        yield {"text": s_scrubbed, "refs": spans}
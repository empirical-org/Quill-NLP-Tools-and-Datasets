import json

def postprocess_ginger(response):
    corrections = response["GingerTheDocumentResult"]["Corrections"]

    corrections.reverse()

    if len(corrections) == 0:
        return None
    else:
        for correction in corrections:
            if len(correction["Suggestions"]) > 0:
                sentence = sentence[:correction["From"]] + correction["Suggestions"][0]["Text"] + sentence[correction["To"]+1:]

        return sentence


if __name__ == "__main__":
    f = "../grammar_ginger.json"

    with open(f) as i:
        data = json.load(i)

    for item in data:
        sentence = item["sentence"]
        corrected_sentence = postprocess_ginger(item)
        print(sentence + "#" + corrected_sentence)
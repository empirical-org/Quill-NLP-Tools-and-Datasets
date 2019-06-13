# run languagetool with the following command:
# java -cp languagetool-server.jar org.languagetool.server.HTTPServer --port 8081 --allow-origin '*'
#
# and then make requests like this:
# http://localhost:8081/v2/check?language=en-US&text=the+man+are+small

import requests
import urllib
import re
import csv

IP = "localhost"
PORT = "8081"
LANGUAGE = "en-US"
URL = f"http://{IP}:{PORT}/v2/check?language={LANGUAGE}&text="

INPUT_FILE = "data/raw/junkfood_because.tsv"
OUTPUT_FILE = "junkfood_because_languagetool.tsv"

sentences = []
with open(INPUT_FILE) as i:
    for line in i:
        sentences.append("Schools should not allow junk food to be sold on campus, " + line.strip().split("\t")[0])

output = []
for sentence in sentences:

    sentence = re.sub("\s+", " ", sentence)
    original_sentence = sentence
    encoded_sentence = urllib.parse.quote_plus(sentence)
    r = requests.get(URL + encoded_sentence).json()

    if len(r["matches"]) > 0:
        print(r)

    corrections = []

    index_correction = 0
    for correction in r["matches"]:
        if len(correction["replacements"]) > 0:
            start = correction["offset"] + index_correction
            end = start + correction["length"]
            replacement = correction["replacements"][0]["value"]

            corrections.append(" ".join([sentence[start:end], "=>", replacement]))
            corrections.append(correction["message"])
            corrections.append(correction["rule"])

            sentence = sentence[:start] + replacement + sentence[end:]

            index_correction += len(replacement) - (end-start)

    #sentence = urllib.parse.unquote(sentence)
    #sentence = sentence.replace("+", " ")

    if sentence != original_sentence:
        print(original_sentence)
        print(sentence)

    sentence_info = [original_sentence, sentence]
    sentence_info += corrections

    output.append(sentence_info)

with open(OUTPUT_FILE, "w") as o:
    csvwriter = csv.writer(o, delimiter="\t")
    csvwriter.writerow(["Input sentence", "Corrected sentence", "Correction", "Message", "Rule info"])
    for row in output:
        csvwriter.writerow(row)

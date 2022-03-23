import csv
import spacy
import difflib

nlp = spacy.load("en_core_web_sm")

with open("scripts/data/spelling.csv") as i,  open("corrections2.csv", "w") as o:
    reader = csv.reader(i, delimiter = "\t")
    writer = csv.writer(o, delimiter="\t")

    for sentence1, sentence2 in reader:

        #if not sentence1.startswith("8. Methane"):
        #    continue

        corrections = []
        input_tokens = [t.text for t in nlp(sentence1)]
        output_tokens = [t.text for t in nlp(sentence2)]

        input_token, output_token = "", ""
        for token in difflib.ndiff(input_tokens, output_tokens):
            print(token)
            if token.startswith(" "):
                if input_token or output_token:
                    corrections.append((input_token.strip(), output_token.strip()))
                input_token, output_token = "", ""
            elif token.startswith("-"):
                input_token += " " + token[2:]
            elif token.startswith("+"):
                output_token += " " + token[2:]

        if input_token or output_token:
            corrections.append((input_token.strip(), output_token.strip()))

        row = []
        for correction in corrections:
            row.append(correction[0])
            row.append(correction[1])

        writer.writerow(row)
        print(row)

import requests

from private import BING_KEY, BING_URL

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ7bVBj7fLFA6e-zpZ-kGY7HkJhcDDapmUe5vpLLyqYo4LOGWy86auJIOXQCsxFQWOjXe7X4q6F4cmM/pub?gid=688772490&single=true&output=tsv"

error_equivalence = {
    "Subject-verb agreement (rule)": "Subject-verb agreement",
    "Subject-verb agreement (stats)": "Subject-verb agreement",
    "Those versus these": "This versus that",
    "Plural versus possessive nouns": "Possessive nouns",
    "Irregular past tense verbs": "Verb tense",
}


def evaluate(correct_errors, predicted_errors):

    results = {}
    for correct_item, predicted_item in zip(correct_errors, predicted_errors):
        correct_item = set([error_equivalence.get(e, e) for e in correct_item])
        predicted_item = set([error_equivalence.get(e, e) for e in predicted_item])

        print("C", correct_item)
        print("P", predicted_item)

        for predicted_error in predicted_item:
            if predicted_error not in results:
                results[predicted_error] = {"fp": 0, "tp": 0, "fn": 0, "support": 0}

            if predicted_error in correct_item:
                results[predicted_error]["tp"] += 1
            else:
                results[predicted_error]["fp"] += 1

        for correct_error in correct_item:
            if correct_error not in results:
                results[correct_error] = {"fp": 0, "tp": 0, "fn": 0, "support": 0}
            results[correct_error]["support"] += 1
            if correct_error not in predicted_item:
                results[correct_error]["fn"] += 1

    return results


def precision_recall_fscore_support(results, error):
    support = results[error]["support"]
    tp = results[error]["tp"]
    fp = results[error]["fp"]
    fn = results[error]["fn"]
    p = tp / (tp + fp) if tp + fp > 0 else 0
    r = tp / (tp + fn) if tp + fn > 0 else 0
    f = 2 * p * r / (p + r) if p + r > 0 else 0
    return p, r, f, support


def test_quill_vs_ginger():
    data = requests.get(url)
    lines = data.text.split("\n")


    all_manual_errors = []
    all_ginger_errors = []
    all_quill_errors = []
    for line in lines[1:623]:
        line = line.strip().split("\t")
        while len(line) < 11:
            line.append("")

        sentence = line[0]
        manual_errors = set([x for x in [line[1], line[2], line[3], line[4]] if x])
        ginger_errors = set([x for x in [line[6], line[7], line[8]] if x])
        quill_errors = set(line[10].split(","))
        all_manual_errors.append(manual_errors)
        all_ginger_errors.append(ginger_errors)
        all_quill_errors.append(quill_errors)

        #print(sentence)
        #print("M", manual_errors)
        #print("G", ginger_errors)
        #print("Q", quill_errors)

    ginger_results = evaluate(all_manual_errors, all_ginger_errors)
    quill_results = evaluate(all_manual_errors, all_quill_errors)
    errors = list(ginger_results.keys())
    errors.sort()

    for error in errors:
        support = ginger_results[error]["support"]
        if support > 0:
            pg, rg, fg, _ = precision_recall_fscore_support(ginger_results, error)
            pq, rq, fq, _ = precision_recall_fscore_support(quill_results, error)

            print("\t".join([error, str(pg), str(rg), str(fg),
                             str(pq), str(rq), str(fq),
                             str(support)]))


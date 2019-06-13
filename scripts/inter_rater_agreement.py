import pandas as pd
from sklearn.metrics import cohen_kappa_score, accuracy_score

CSV_INPUT_FILE = "data/raw/Comprehension Labeling - Meat Consumption Passage - Compare Labels.csv"

df = pd.DataFrame.from_csv(CSV_INPUT_FILE)
df = df.fillna(value="None")

reference_labeller = "AB Label"
other_labellers = ["HM Labels", "RD Label", "EV Labels"]

reference_labels = df[reference_labeller]
for other_labeller in other_labellers:
    other_labels = df[other_labeller]
    kappa = cohen_kappa_score(reference_labels, other_labels)
    acc = accuracy_score(reference_labels, other_labels)
    print(other_labeller, kappa, acc)

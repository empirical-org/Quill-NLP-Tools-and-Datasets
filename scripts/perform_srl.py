import json

from quillnlp.srl import perform_srl


PROMPT = "The United States is investing in self-driving trucks, so"
INPUT_FILE = "data/raw/selfdrivingtrucks_so.tsv"
OUTPUT_FILE = "scripts/data/selfdrivingtrucks_so_srl.json"


with open(INPUT_FILE) as i:
    responses = [line.strip() for line in i]


results = perform_srl(responses, PROMPT)


with open(OUTPUT_FILE, "w") as o:
    json.dump(results, o)
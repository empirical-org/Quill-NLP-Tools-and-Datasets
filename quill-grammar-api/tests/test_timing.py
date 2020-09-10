import requests
import random
import time
from tqdm import tqdm

files = {
    "We should stop eating meat because": "test/data/eating_meat_because.tsv",
    "We should stop eating meat, but": "test/data/eating_meat_because.tsv",
    "We should stop eating meat, so": "test/data/eating_meat_so.tsv",
}

sentences = []
for prompt in files:
    f = files.get(prompt)

    with open(f) as i:
        for line in i:
            sentences.append({"sentence": prompt + " " + line.strip(), "prompt": prompt})


random.shuffle(sentences)

start = time.time()
step_size = 10

for i in tqdm(range(0, len(sentences), step_size)):
    chunk = sentences[i:i+step_size]
    print(chunk)
    r = requests.post("https://grammar-api.ue.r.appspot.com", data=chunk)

end = time.time()
total = end-start

print("Total seconds:", total)
print("Seconds per sentence:", total/len(sentences))

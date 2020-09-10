import random

from locust import HttpUser, task, between

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


class TestUser(HttpUser):

    @task(1)
    def check_sentence(self):
        self.client.post("https://grammar-api.ue.r.appspot.com", data=random.choice(sentences))

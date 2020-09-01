from tqdm import tqdm
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

from quillnlp.grammar.unsupervised2 import make_request

import time

PROJECT = "comprehension-247816"
MODEL_NAME = "grammartest"
VERSION_NAME = "v4"

sentences = ["My dog barks every time he think he hears the mailman approaching, but usually it is just my sister's boyfriend coming to visit in his giant green pickup truck."]
sentences = ["You are taller then me."]
requests = [make_request(s) for s in sentences]
print(requests)


# JSON format the requests
request_data = {'instances': requests}

# Authenticate and call CMLE prediction API
credentials = GoogleCredentials.get_application_default()
api = discovery.build('ml', 'v1', credentials=credentials,
     discoveryServiceUrl='https://storage.googleapis.com/cloud-ml/discovery/ml_v1_discovery.json')

parent = 'projects/%s/models/%s/versions/%s' % (PROJECT, MODEL_NAME, VERSION_NAME)

start = time.time()
for _ in tqdm(list(range(1))):
    response = api.projects().predict(body=request_data, name=parent).execute()
    print(response)
end = time.time()

for prediction in response['predictions']:
    print(prediction)

total_time = end-start
sec_per_sent = total_time/len(sentences)
print(f"Time:{total_time} seconds ==> Per sentence: {sec_per_sent} seconds")

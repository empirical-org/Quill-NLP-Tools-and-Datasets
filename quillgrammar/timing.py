import time
import requests

start = time.time()
requests.post("https://comprehension-247816.appspot.com", data={"sentence": "We should stop eating meat, because meat are bad and makes the atmosphere warms up." , "prompt": "We should stop eating meat, because"}).json()
end = time.time()

print(end-start, "seconds")

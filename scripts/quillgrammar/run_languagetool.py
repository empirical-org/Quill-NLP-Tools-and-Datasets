import requests

url = 'http://localhost:8081/v2/check'

r = requests.post(url, data={'language': 'en-US', 'text': 'a simple test'})

for error in r.json().get('matches'):
    print(error)
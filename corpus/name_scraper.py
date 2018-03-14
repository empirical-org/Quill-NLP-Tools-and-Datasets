"""Scrape the 1000 Top Names in the USA, this list will be useful for lots of
things. This scraper is pretty rudimentary, make sure you check output"""


from bs4 import BeautifulSoup as bs
import requests

# Constants
US_1000_TOP_NAMES_URL = 'https://nameberry.com/popular_names/US'
OUTPUT_FILE = 'mostPopularNamesUSA.txt'

r = requests.get(US_1000_TOP_NAMES_URL)
soup = bs(r.text, 'html.parser')

with open(OUTPUT_FILE, 'w+') as f:
    for tr in soup.find_all('tr'):
        for line in tr.text.split('\n'):
            if line and len(line) < 20 and not line.strip().isdigit():
                f.write(line + '\n')


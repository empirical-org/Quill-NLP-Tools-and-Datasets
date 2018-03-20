"""Given a gutenberg bookshelf page, download the books on that page and put
them in our books folder"""


import re
import time
import requests
from bs4 import BeautifulSoup as bs

START_URL = 'http://www.gutenberg.org/wiki/Children%27s_Fiction_(Bookshelf)'
NEW_LINK_BASE = 'http://www.gutenberg.org/cache/epub/{}/pg{}.txt'

# fetch page
r = requests.get(START_URL)

# extract links
soup = bs(r.text)
book_links = soup.find_all(class_=re.compile("extiw"))
new_links = []
for el in book_links: 
    link = el['href']
    title = el.text
    bookid = link.split('/')[-1]
    if bookid.isdigit():
        new_link = NEW_LINK_BASE.format(bookid, bookid)
        new_links.append([title, new_link])

# save links as books
for link_tup in new_links:
    time.sleep('.25') # be nice to project gutenberg
    r1 = requests.get(link_tup[1])
    new_filename = link_tup[0].lower().replace(' ', '-').replace('\n',
            '-') + '.txt'
    new_new_filename = ''
    for char in new_filename:
        if char in 'abcdefghijklmnopqrstuvwxyz-.':
            new_new_filename += char
    new_filename = new_new_filename
    with open('books/' + new_filename, 'w+') as output_file:
        output_file.write(r1.text)
        print('wrote ' + new_filename)

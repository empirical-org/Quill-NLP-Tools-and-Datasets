"""Given a gutenberg bookshelf page, download the books on that page and put
them in our books folder"""

import os
import re
import time
import requests
import sys
from bs4 import BeautifulSoup as bs

OUTPUT_DIR = os.environ.get('GUTENFETCH_OUTPUT_DIR')
if not OUTPUT_DIR:
    OUTPUT_DIR = './'
if OUTPUT_DIR[-1] != '/':
    raise(Exception('GUTENFETCH_OUTPUT_DIRECTORY must end with a slash'))

NEW_LINK_BASE = 'http://www.gutenberg.org/cache/epub/{}/pg{}.txt'

def fetch_bookshelf(start_url, output_dir):
    """Fetch all the books off of a gutenberg project bookshelf page

    example bookshelf page,
    http://www.gutenberg.org/wiki/Children%27s_Fiction_(Bookshelf)
    """
    # make output directory
    try:
        os.mkdir(OUTPUT_DIR + output_dir)
    except OSError as e:
        raise(e)

    # fetch page
    r = requests.get(start_url)

    # extract links
    soup = bs(r.text, 'html.parser')
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
        time.sleep(.10) # be nice to project gutenberg
        r1 = requests.get(link_tup[1])
        new_filename = link_tup[0].lower().replace(' ', '-').replace('\n',
                '-')
        new_new_filename = ''
        for char in new_filename:
            if char in 'abcdefghijklmnopqrstuvwxyz-':
                new_new_filename += char
        new_filename = new_new_filename + '.txt'
        with open(OUTPUT_DIR + output_dir + '/' + new_filename, 'w+') as output_file:
            output_file.write(r1.text)

    return None


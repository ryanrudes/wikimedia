from bs4 import BeautifulSoup
from threading import Thread
from queue import Queue

import requests
import warnings
import logging
import os

logging.basicConfig(
    format  = '%(asctime)s %(levelname)-8s %(message)s',
    level   = logging.INFO,
    datefmt = '%Y-%m-%d %H:%M:%S')

def nextn(l, n):
    if n == 0:
        return next(l)

    return next(x for i, x in enumerate(l) if i == n)

url = 'https://commons.wikimedia.org'
extensions = set({'jpg', 'jpeg', 'png'})

def add(elem):
    global paths

    try:
        if not elem is None:
            href = elem['href']
            if not href is None:
                if href not in hrefs:
                    hrefs.add(href)
                    paths.put(href)
    except Exception as e:
        warnings.warn("Unexpected exception occured when trying to add the element %s: %s" % (str(elem), str(e)), UserWarning)

def worker():
    global found, fails

    while True:
        # Fetch page
        try:
            path = paths.get()
            link = url + path
            resp = requests.get(link)
            html = resp.content
            soup = BeautifulSoup(html, features = 'html.parser')
        except Exception as e:
            warnings.warn("Unexpected exception occured when trying to fetch %s: %s" % (link, str(e)))
            fails.append((path, 0))
            paths.task_done()
            continue

        # Look for subcategories
        try:
            for elem in soup.find_all('div', class_ = 'CategoryTreeItem'):
                elem = nextn(elem.children, 2)
                add(elem)
        except Exception as e:
            warnings.warn("Unexpected exception occured when trying to parse subcategories from page: " + str(e), UserWarning)
            fails.append((path, 1))

        # Look for next page of subcategories (may or may not exist)
        try:
            elem = soup.find('a', href = True, text = 'next page')
            add(elem)
        except Exception as e:
            warnings.warn("Unexpected exception occured when trying to search for next page of subcategories: " + str(e), UserWarning)
            fails.append((path, 2))

        # Look for image links
        try:
            for elem in soup.find_all('li', class_ = 'gallerybox'):
                elem = next(next(next(nextn(elem.children, 1).children).children).children)
                if elem.name == 'img':
                    src = elem['src']
                    if not src is None:
                        ext = src[src.rindex('.') + 1:].lower()
                        if ext in extensions:
                            alt = elem['alt']
                            if alt is None:
                                alt = ''

                            found.add((src, alt))
        except Exception as e:
            warnings.warn("Unexpected exception occured when trying to parse image URLs from page: " + str(e), UserWarning)
            fails.append((path, 3))

        paths.task_done()

hrefs = set()
paths = Queue()
found = set()
fails = []
chunk = 64
total = 0

outdir = input('Enter output directory path: ')
os.makedirs(outdir, exist_ok = True)

outfp = os.path.join(outdir, 'output.txt')
ooffp = os.path.join(outdir, 'failed.txt')

threads = []

for i in range(8):
    thread = Thread(target = worker, daemon = True)
    thread.start()
    threads.append(thread)

paths.put('/wiki/Category:Topics')

data = []
while found or fails or any(thread.is_alive() for thread in threads):
    if found:
        data.append(found.pop())
        if len(data) == chunk:
            total += chunk
            logging.info('Found %d images' % total)
            with open(outfp, 'a') as f:
                for src, alt in data:
                    f.write(src + '\t' + alt + '\n')
            data.clear()

    if fails:
        with open(ooffp, 'a') as f:
            path, code = fails.pop()
            f.write(path + '\t' + str(code) + '\n')

total += len(data)
with open(outfp, 'a') as f:
    for src, alt in data:
        f.write(src + '\t' + alt + '\n')
logging.info('Finished with %d images' % total)

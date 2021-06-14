from torch.utils.data import Dataset
from urllib.request import urlopen
from .utils import cycle
from skimage import io
from PIL import Image

import multiprocessing as mp
import warnings
import random
import urllib
import string
import math
import cv2
import os

def start_queue(in_queue, rangefn, total, workers):
    for i in rangefn(total):
        in_queue.put(i)
    for _ in range(workers):
        in_queue.put(None)

def process(in_queue, out_queue, path, fetch, total, size):
    while True:
        idx = in_queue.get()
        if idx is None:
            out_queue.put(None)
            break
        url = idx2url(path, idx, total, size)
        img = fetch(url)
        out_queue.put(img)

def idx2url(path, idx, total, size):
    line = getline(path, idx, total, size)

    url = 'https://upload.wikimedia.org/wikipedia/commons/'

    if int(line[0]):
        url += 'thumb/'

    return url + line[1] + '/' + line[2:4] + '/' + line[4:]

def getline(path, linenum, total, size):
    with open(path, 'rb') as f:
        f.seek(int(linenum / total * size), os.SEEK_SET)
        while f.read(1) != b'\n':
            f.seek(-2, os.SEEK_CUR)
        return f.readline()[:-1].decode()

class WikimediaCommonsDataset(Dataset):
    total = 41666578
    size = 5073656467

    def __init__(self,
                 path='filtered.txt',
                 verbose=True,
                 max_retries=None,
                 timeout=None,
                 shuffle=True,
                 max_buffer=4096,
                 workers=8,
                 transform=None):
        self.path = path
        self.verbose = verbose
        self.max_retries = 10000000000 if max_retries is None else max_retries
        self.timeout = timeout
        self.shuffle = shuffle
        self._rangefn = cycle if shuffle else range
        self.max_buffer = max_buffer
        self.workers = workers
        self.transform = transform

    def __len__(self):
        return self.total

    def __iter__(self):
        in_queue = mp.Queue(maxsize = self.max_buffer)
        out_queue = mp.Queue(maxsize = self.max_buffer)

        gen_pool = mp.Pool(1, initializer = start_queue, initargs = (in_queue, self._rangefn, self.total, self.workers))
        pool = mp.Pool(self.workers, initializer = process, initargs = (in_queue, out_queue, self.path, self.fetch, self.total, self.size))

        finished_workers = 0
        while True:
            img = out_queue.get()
            if img is None:
                finished_workers += 1
                if finished_workers == self.workers:
                    break
            else:
                yield img

    def __getitem__(self, idx):
        url = idx2url(self.path, idx)
        return self.fetch(url)

    def fetch(self, url):
        for i in range(self.max_retries):
            try:
                img = io.imread(url)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                if not self.transform is None:
                    img = transform(img)
                return img
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    self.refresh_user_agent()
                else:
                    self.warn(url, e)
            except KeyboardInterrupt:
                exit()
            except Exception as e:
                if self.verbose:
                    warnings.warn('An unexpected exception occured when attempting to fetch %s: %s' % (url, str(e)), UserWarning)
                return

        if self.verbose:
            warnings.warn('Attempt to fetch expired after reaching max retries for %s' % url, UserWarning)

    def refresh_user_agent(self):
        opener = urllib.request.build_opener()
        letters = string.ascii_letters
        user_agent = ''.join(random.choice(letters) for i in range(random.randint(8, 15)))
        opener.addheaders = [('User-agent', user_agent)]
        urllib.request.install_opener(opener)

    def warn(self, url, exc):
        if self.verbose:
            warnings.warn('Exception when attepting to fetch %s: %s' % (url, str(exc)), UserWarning)

if __name__ == '__main__':
    dataset = WikimediaCommonsDataset()
    for i, img in enumerate(dataset):
        print (i + 1, img.shape)

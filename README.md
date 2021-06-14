<img src="https://user-images.githubusercontent.com/18452581/121902225-1f5a5680-ccf5-11eb-8343-2a42720616d7.png" width="100%">

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/gist/Ryan-Rudes/ad5bc9481ffb268e1cacaf3808d395e5/wikimedia-dataset-demo.ipynb)

### Introduction

Wikimedia Commons Image Dataset is comprised of over 40 million URLs to Wikimedia Commons images.

### Requirements

These are only required if you plan to run the data scraper yourself, which is unnecessary.

- [`tqdm`](https://github.com/tqdm/tqdm)
- [`bs4`](https://github.com/waylan/beautifulsoup)

These are the requirements for the PyTorch `DataLoader`:

- [`torch`](https://github.com/pytorch/pytorch)
- [`scikit-image`](https://github.com/scikit-image/scikit-image)
- [`pillow`](https://github.com/python-pillow/Pillow)
- [`opencv-python`](https://github.com/opencv/opencv)

### Data

Data is represented in a certain compressed format. URLs are newline-delimited.

URLs to Wikimedia Commons images are formatted as follows: \
`https://upload.wikimedia.org/wikipedia/commons/thumb/<ID-1>/<ID-2>/<FILENAME>` \
or \
`https://upload.wikimedia.org/wikipedia/commons/<ID-1>/<ID-2>/<FILENAME>` (no /thumb/)

`<ID-1>` is 1 character in length, and `<ID-2>` is 2

For each URL, it is compressed as follows:
`<THUMB><ID-1><ID-2><FILENAME>`

where `<THUMB>` is a binary integer, indicating whether `/thumb/` is a component of the path.

There are 41666578 URLs in total, equating to 4.73 GB.

### Usage

Included is a:
- [x] PyTorch `DataLoader` for this dataset
- [ ] TensorFlow `Dataset` for this dataset

#### PyTorch `DataLoader` Usage
To demo the PyTorch `DataLoader`, first `cd` to the main directory. Then, download the dataset:
```
kaggle datasets download -d ryanrudes/wikimedia --unzip
```
Then, run the script:
```
python loaders/pytorch.py
```
You can use this dataset by simply importing the `DataLoader` class, for example:
```python
from loaders.pytorch import WikimediaCommonsDataset

dataset = WikimediaCommonsDataset()

for image in dataset:
    print (image.shape)
```
You can modify the following arguments of `WikimediaCommonsDataset`. Their default values are given below:
```python
path        = 'filtered.txt'
verbose     = True
max_retries = None
timeout     = None
shuffle     = True
max_buffer  = 4096
workers     = 8
transform   = None
```

### Links and Further Info

The dataset is available on [Kaggle](https://www.kaggle.com/ryanrudes/wikimedia)

This is licensed under the MIT license. Click [here](https://github.com/Ryan-Rudes/wikimedia/blob/master/LICENSE.txt) to learn more. All image links in this dataset are in the public domain. The only exception would be links to Wikimedia Foundation logos, which were already filtered prior to the data upload.

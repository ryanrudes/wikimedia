from sys import getsizeof
from tqdm import tqdm
import os

"""
https://upload.wikimedia.org/wikipedia/commons/<ID1>/<ID2>/<FILENAME>
https://upload.wikimedia.org/wikipedia/commons/thumb/<ID1>/<ID2>/<FILENAME>

<ID1> is 1 character in length
<ID2> is 2 characters in length
"""

outdir = input('Enter output directory path: ')

srcfp = os.path.join(outdir, 'output.txt')
dstfp = os.path.join(outdir, 'filter.txt')

unique = set()
hashes = set()

with open(srcfp, 'r') as f:
    for i, line in enumerate(tqdm(f, 'Getting unique URLs')):
        if not line.startswith('https://upload.wikimedia.org/wikipedia/commons/'):
            continue

        code = hash(line)

        if code not in hashes:
            unique.add(i)
            hashes.add(code)

with open(srcfp, 'r') as f, open(dstfp, 'w') as out:
    size = 0
    total = 0

    for i, line in enumerate(tqdm(f, 'Filtering, encoding, and writing')):
        total += 1

        if i in unique:
            line = line[47:]
            line = line[:line.index('\t')]
            thumb = line.startswith('thumb')

            if thumb:
                line = line[6:]

            line = line.split('/')

            if len(line) == 3:
                id1, id2, filename = line
            else:
                id1, id2, filename1, filename2 = line
                filename = filename1 + '/' + filename2

            encoded = '%d%s%s%s' % (thumb, id1, id2, filename)
            out.write(encoded + '\n')
            size += getsizeof(encoded)

    print ('Total:', total)
    print ('Unique:', len(unique))
    print ('Filtered:', total - len(unique))
    print ('Size:', size)

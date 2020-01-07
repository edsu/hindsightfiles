#!/usr/bin/env python

"""
Read urls.csv and generate listing for README.md
"""

import os
import re
import csv
import requests

seen = {}
for row in csv.DictReader(open('urls.csv')):
    if re.match(r'^https://.+\.zip$', row['url']):
        filename = os.path.basename(row['url'])
        row['filename'] = filename
        seen[filename] = row

for row in csv.DictReader(open('urls.csv')):
    if re.match(r'^https://.+\.txt$', row['url']):
        md5, filename = requests.get(row['url']).text.split()
        seen[filename]['md5'] = md5

for r in seen.values():
    print('* {url} archived at {archive_url} with MD5 {md5}'.format(**r))

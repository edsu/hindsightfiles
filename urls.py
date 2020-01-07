#!/usr/bin/env python

"""
This script will search for all the download files that were tweeted by
@HindsightFiles and make sure they are up at the Internet Archive. The results
are written to urls.csv.
"""


import csv
import json
import time
import twarc
import logging
import requests
import datetime
import dateutil.parser

def main():
    logging.basicConfig(filename='urls.log', level=logging.INFO)
    out = csv.DictWriter(
        open('urls.csv', 'w'), 
        fieldnames=['url', 'tweeted_at', 'tweet_url', 'archive_url', 'archived_at']
    )
    out.writeheader()

    # seen is used to not output the same URL twice if it was tweetd twice
    seen = set()
    for url in sorted(repo_urls(), key=lambda u: u['tweeted_at'], reverse=True):
        if url['url'] not in seen:
            logging.info('found %s, archived at %s', url['url'], url['archive_url'])
            out.writerow(url)
            seen.add(url['url'])

def repo_urls():
    urls = []
    t = twarc.Twarc()
    for tweet in t.timeline(screen_name='hindsightfiles'):
        tweet_url = 'https://twitter.com/hindsightfiles/status/{}'.format(tweet['id_str'])

        # make sure that the tweet is archived
        wayback(tweet_url)

        # look for 'repo' urls
        for e in tweet['entities']['urls']:
            if 'repo' in e['expanded_url']:
                archive_url, archived_at = wayback(e['expanded_url'])
                yield {
                    'url': e['expanded_url'],
                    'tweeted_at': parse_time(tweet['created_at']),
                    'tweet_url': tweet_url,
                    'archive_url': archive_url,
                    'archived_at': archived_at,
                }

def wayback(url):
    cdx = 'http://web.archive.org/cdx/search/cdx'
    params={'url': url, 'output': 'json', 'limit': 1000}
    snapshots = requests.get(cdx, params=params).json()
    if len(snapshots) == 0:
        # savepagenow if there is no snapshot
        logging.info('archiving %s', url)
        requests.get('https://web.archive.org/save/{}'.format(url))
        time.sleep(10)
        return wayback(url)
    first = snapshots[-1]
    dt = parse_time(first[1])
    url = 'https://web.archive.org/web/{}/{}'.format(first[1], url)
    return url, dt

def parse_time(s):
    dt = dateutil.parser.parse(s)
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

if __name__ == "__main__":
    main()

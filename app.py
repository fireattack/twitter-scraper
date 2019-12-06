#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Usage: 
python app.py <user_id>
"""
import json
import os
import requests
import sys
from bs4 import BeautifulSoup
import concurrent.futures


def crawl(user_id, items=[], max_id=None):
    url = 'https://twitter.com/i/profiles/show/' + user_id + \
        '/media_timeline' + ('?&max_id=' + max_id if max_id is not None else '')
    print(f"Parsing {url}...")
    media = requests.get(url).json()

    soup = BeautifulSoup(media['items_html'], 'lxml')
    tags = soup.find_all(attrs={'data-image-url': True})

    items.extend([tag['data-image-url'] + ':orig' for tag in tags])

    if 'has_more_items' not in media or media['has_more_items'] is False:
        return items
    else:
        max_id = media['min_position']
        return crawl(user_id, items, max_id)

def download(url, save_dir='./'):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    base_name = url.split('/')[-1].split(':')[0]
    file_path = os.path.join(save_dir, base_name)

    with open(file_path, 'wb') as file:
        print('Downloading ' + base_name)
        bytes = requests.get(url).content
        file.write(bytes)


if __name__ == '__main__':
    #   user_id = sys.argv[1]

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = dict((executor.submit(download, url, './' + user_id), url) for url in crawl(user_id))

        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]

            if future.exception() is not None:
                print(f'{url} generated an exception: {future.exception()}')

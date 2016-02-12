#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gzip
from lett import read_lett_iter


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('lettfiles', help='input lett files',
                        type=argparse.FileType('r'), nargs='+')
    parser.add_argument('-translations',
                        help='url<TAB>translation pairs', required=True,
                        type=argparse.FileType('r'))
    parser.add_argument('-tlang', help='target language', default='fr')
    args = parser.parse_args()

    translation_urls = set()
    fh = args.translations
    if fh.name.endswith('.gz'):
        fh = gzip.GzipFile(fileobj=fh, mode='r')
    for line in fh:
        url = line.rstrip().split('\t', 1)[0]
        translation_urls.add(url)

    for lett_file in args.lettfiles:
        for page in read_lett_iter(lett_file, decode=False):
            if page.url in translation_urls:
                translation_urls.remove(page.url)

    if translation_urls:
        print "Could not find %d target urls: %s" \
            % (len(translation_urls), "\n".join(translation_urls))

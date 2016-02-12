#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lett import read_lett_iter


def read_url_pairs(fh):
    pairs = []
    source_urls = set()
    target_urls = set()
    for line in fh:
        if not len(line.strip().split('\t')) == 2:
            print line, line.strip().split('\t')
        source_url, target_url = line.strip().split('\t')

        assert source_url not in source_urls,\
            "Repeated source url: %s\n" % (source_url)
        assert target_url not in target_urls,\
            "Repeated target url: %s\n" % (target_url)
        assert source_url not in target_urls,\
            "source url already seen as target url: %s\n" % (target_url)
        assert target_url not in source_urls,\
            "target url already seen as source url: %s\n" % (target_url)

        pairs.append((source_url, target_url))

    return pairs

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('lettfiles', help='input lett files',
                        type=argparse.FileType('r'), nargs='+')
    parser.add_argument('-train', help='training url pairs', required=True,
                        type=argparse.FileType('r'))
    parser.add_argument('-slang', help='source language', default='en')
    parser.add_argument('-tlang', help='target language', default='fr')
    args = parser.parse_args()

    train_pairs = read_url_pairs(args.train)
    all_urls = set()
    for su, tu in train_pairs:
        assert su not in all_urls
        all_urls.add(su)
        assert tu not in all_urls
        all_urls.add(tu)

    sorted_pairs = []

    for lett_file in args.lettfiles:
        for page in read_lett_iter(lett_file):
            if page.url not in all_urls:
                continue
            pair = None

            assert page.lang == args.slang or page.lang == args.tlang

            for su, tu in train_pairs:
                if su == page.url:
                    pair = (su, tu)
                if tu == page.url:
                    pair = (tu, su)

            assert pair is not None

            if page.lang == args.tlang:
                pair = (pair[1], pair[0])

            all_urls.remove(pair[0])
            all_urls.remove(pair[1])

            print "\t".join(pair)

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

    source_urls = set(su for su, tu in train_pairs)
    target_urls = set(tu for su, tu in train_pairs)
    assert len(source_urls) == len(target_urls)

    for lett_file in args.lettfiles:
        for page in read_lett_iter(lett_file):
            if page.lang == args.slang:
                assert page.url not in target_urls, \
                    "%s is in %s and cannot be a target url" % (
                        page.url, page.lang)
                if page.url in source_urls:
                    source_urls.remove(page.url)
            elif page.lang == args.tlang:
                assert page.url not in source_urls, \
                    "%s is in %s and cannot be a source url" % (
                        page.url, page.lang)
                if page.url in target_urls:
                    target_urls.remove(page.url)
            else:  # ignore all other languages
                pass

    if source_urls:
        print "Could not find %d source urls: %s" \
            % (len(source_urls), "\n".join(source_urls))
    if target_urls:
        print "Could not find %d target urls: %s" \
            % (len(target_urls), "\n".join(target_urls))

    print "All %d pairs found in lett files" % (len(train_pairs))

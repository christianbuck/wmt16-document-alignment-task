#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
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
    parser.add_argument('-out', help='output file',
                        type=argparse.FileType('w'))
    parser.add_argument('-multipairs', help='output file',
                        type=argparse.FileType('w'))
    parser.add_argument('-slang', help='source language', default='en')
    parser.add_argument('-tlang', help='target language', default='fr')
    args = parser.parse_args()

    train_pairs = read_url_pairs(args.train)

    source_urls = set(su for su, tu in train_pairs)
    target_urls = set(tu for su, tu in train_pairs)
    assert len(source_urls) == len(target_urls)

    for lett_file in args.lettfiles:
        hash2url_s, hash2url_t = defaultdict(list), defaultdict(list)
        n_s, n_t = 0, 0
        for page in read_lett_iter(lett_file):
            h = hash(page.text)

            if page.lang == args.slang:
                hash2url_s[h].append(page.url)
                n_s += 1
            elif page.lang == args.tlang:
                hash2url_t[h].append(page.url)
                n_t += 1

        if args.out:
            for h, urls in hash2url_s.iteritems():
                if len(urls) > 1:
                    args.out.write("%d\t%s\n" % (len(urls), "\t".join(urls)))

            for h, urls in hash2url_t.iteritems():
                if len(urls) > 1:
                    args.out.write("%d\t%s\n" % (len(urls), "\t".join(urls)))

        seen_s = {}
        seen_t = {}
        n_multi = 0

        for su, tu in train_pairs:
            if su in seen_s:
                print "%s seen before as %s" % (su, seen_s[su])
            if tu in seen_t:
                print "%s seen before as %s" % (tu, seen_t[tu])

            out = ""
            for h, urls in hash2url_s.iteritems():
                if su in urls:
                    out += "\t".join(urls)
                    for u in urls:
                        seen_s[u] = su

            out += "\t<->\t"
            for h, urls in hash2url_t.iteritems():
                if tu in urls:
                    out += "\t".join(urls)
                    for u in urls:
                        seen_t[u] = tu
            if args.multipairs and len(out.strip().split()) > 1:
                args.multipairs.write("%s\n" % (out))
            if len(out.strip().split('\t')) > 3:
                n_multi += 1

        seen_pairs = []
        for su, tu in train_pairs:
            if su in seen_s and tu in seen_t:
                seen_pairs.append((su, tu))

        print lett_file.name, n_s, len(hash2url_s), n_t, len(hash2url_t), \
            len(seen_pairs), n_multi

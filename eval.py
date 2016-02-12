#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys


def read_pairs(infile, swap=False):
    """ reads file of format SOURCE_URL<TAB>TARGET_URL """
    url_pairs = []
    for line in infile:
        assert len(line.split('\t')) == 2, "expected format: url<tab>url\n"
        source_url, target_url = line.rstrip().split("\t")
        if swap:
            target_url, source_url = source_url, target_url
        url_pairs.append((source_url, target_url))
    return url_pairs


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('reference',
                        help='correct pairs in dev set',
                        type=argparse.FileType('r'))
    parser.add_argument('predicted',
                        help='predicted pairs',
                        type=argparse.FileType('r'))
    parser.add_argument('-wins',
                        help='write correct pairs to this file',
                        type=argparse.FileType('w'))
    parser.add_argument('-fails',
                        help='write fails to this file',
                        type=argparse.FileType('w'))
    args = parser.parse_args()

    reference = read_pairs(args.reference, swap=True)
    sys.stderr.write("Read %d reference pairs from %s\n" %
                     (len(reference), args.reference.name))

    predicted = read_pairs(args.predicted)
    sys.stderr.write("Read %d predicted pairs from %s\n" %
                     (len(predicted), args.predicted.name))

    # Filter pairs so that every url only occurs once
    pairs_s2t, pairs_t2s = {}, {}
    for su, tu in predicted:
        if su not in pairs_s2t and tu not in pairs_t2s:
            pairs_s2t[su] = tu
            pairs_t2s[tu] = su

    sys.stderr.write(
        "Keeping %d pairs after enforcing 1-1 rule\n" % (len(pairs_s2t)))
    n_found = len(set(reference).intersection(pairs_s2t.items()))
    percent_found = n_found * 100. / len(reference)
    sys.stderr.write("Found %d (%3.2f%%) pairs from reference\n" %
                     (n_found, percent_found))

    # write wins and fails
    if args.fails:
        for su, tu in set(reference).difference(pairs_s2t.items()):
            if su in pairs_s2t:
                args.fails.write("S2T MISMATCH: %s\t->\t%s\texpected: %s\n" %
                                 (su, pairs_s2t[su], tu))
            if tu in pairs_t2s:
                args.fails.write("T2S MISMATCH: %s\t->\t%s\texpected: %s\n" %
                                 (tu, pairs_t2s[tu], tu))
            if su not in pairs_s2t and tu not in pairs_t2s:
                args.fails.write("Missing: %s\t->\t%s\n" %
                                 (su, tu))

    if args.wins:
        for su, tu in set(reference).intersection(pairs_s2t.items()):
            args.wins.write("%s\t%s\n" % (su, tu))

    sys.exit()

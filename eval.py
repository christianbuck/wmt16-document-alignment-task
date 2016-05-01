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
    seen_urls = set()
    predicted_filtered = {}
    for su, tu in predicted:
        if su not in seen_urls and tu not in seen_urls:
            seen_urls.add(su)
            seen_urls.add(tu)

            predicted_filtered[su] = tu
            predicted_filtered[tu] = su

    sys.stderr.write(
        "Keeping %d pairs after enforcing 1-1 rule\n" % (
            len(predicted_filtered) / 2))

    found_pairs = set(reference).intersection(predicted_filtered.items())
    n_found = len(found_pairs)
    percent_found = n_found * 100. / len(reference)
    sys.stderr.write("Found %d (%3.2f%%) pairs from reference\n" %
                     (n_found, percent_found))

    # write wins and fails
    if args.fails:
        for su, tu in set(reference).difference(predicted_filtered.items()):
            if su in predicted_filtered:
                args.fails.write("S2T MISMATCH: %s\t->\t%s\texpected: %s\n" %
                                 (su, predicted_filtered[su], tu))
            if tu in predicted_filtered:
                args.fails.write("T2S MISMATCH: %s\t->\t%s\texpected: %s\n" %
                                 (tu, predicted_filtered[tu], tu))
            if su not in predicted_filtered and tu not in predicted_filtered:
                args.fails.write("Missing: %s\t->\t%s\n" %
                                 (su, tu))

    if args.wins:
        for su, tu in set(reference).intersection(predicted_filtered.items()):
            args.wins.write("%s\t%s\n" % (su, tu))

    sys.exit()

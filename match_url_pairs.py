#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from collections import defaultdict
from languagestripper import LanguageStripper


def normalize_url(url):
    """ It seems some URLs have an empty query string.
    This function removes the trailing '?' """
    url = url.rstrip('?')
    if not url.startswith("http://"):
        url = ''.join(("http://", url))
    return url


def read_urls(infile, source_lang='fr', target_lang='en'):
    """ reads file of format LANG<TAB>URL """

    source_urls, target_urls, other_urls = set(), set(), set()
    for line in infile:
        line = line.strip().split('\t')
        if len(line) != 2:
            continue
        lang, url = line

        url = normalize_url(url.strip())
        if lang == source_lang:
            source_urls.add(url)
        elif lang == target_lang:
            target_urls.add(url)
        else:
            other_urls.add(url)
    return source_urls, target_urls, other_urls


def read_reference(infile):
    """ reads file of format SOURCE_URL<TAB>TARGET_URL """
    url_pairs = []
    for line in infile:
        target_url, source_url = line.strip().split("\t")
        url_pairs.append((source_url, target_url))
    return url_pairs


def strip_urls(urls, lang, strip_query_variables=False):
    language_stripper = LanguageStripper(
        languages=[lang], strip_query_variables=False)
    language_stripper_query = LanguageStripper(
        languages=[lang], strip_query_variables=True)
    language_stripper_nolang = LanguageStripper(
        strip_query_variables=True)
    stripped = defaultdict(set)
    for url in urls:
        stripped_url, success = language_stripper.strip_uri(
            url, expected_language=lang)
        if not success:
            # removes '/fr-FR/' and 'lang=FR'
            stripped_url, success = language_stripper.strip_uri(url)
        if not success:
            # removes 'clang=1'
            stripped_url, success = language_stripper_query.strip_uri(url)
        if not success:
            # removes '/en-en/fr-fr'
            stripped_url, success = language_stripper_nolang.strip_uri(url)

        if success:
            assert stripped_url != url
            stripped[stripped_url].add(url)

    return stripped


def find_pairs(source_urls, target_urls,
               source_stripped, target_stripped,
               devset):
    pairs = []
    # stripped source url matches unstripped target url
    # e.g. mypage.net/index.html?lang=fr <-> mypage.net/index.html
    for stripped_source_url in set(
            source_stripped.iterkeys()).intersection(target_urls):
        tu = stripped_source_url
        for su in source_stripped[stripped_source_url]:
            pairs.append((su, tu))
    npairs = len(set(pairs))
    sys.stderr.write(
        "Found %d %s pairs (total: %d) covering %d pairs from devset\n"
        % (npairs, "stripped source + unmodified target",
           npairs, len(set(devset).intersection(pairs))))

    # stripped target url matches unstripped source url.
    # e.g. lesite.fr/en/bonsoir <-> lesite.fr/bonsoir
    for stripped_target_url in set(
            target_stripped.iterkeys()).intersection(source_urls):
        su = stripped_target_url
        for tu in target_stripped[stripped_target_url]:
            pairs.append((su, tu))

    oldpairs = npairs
    npairs = len(set(pairs))
    sys.stderr.write(
        "Found %d %s pairs (total: %d) covering %d pairs from devset\n"
        % (npairs - oldpairs, "stripped target + unmodified source",
           npairs, len(set(devset).intersection(pairs))))

    # stripped source url matches stripped target url
    # e.g. page.net/fr <-> page.net/en
    oldpairs = len(pairs)
    for stripped_source_url, source_url in source_stripped.iteritems():
        if stripped_source_url in target_stripped:
            for su in source_url:
                for tu in target_stripped[stripped_source_url]:
                    pairs.append((su, tu))

    oldpairs = npairs
    npairs = len(set(pairs))
    sys.stderr.write(
        "Found %d %s pairs (total: %d) covering %d pairs from devset\n"
        % (npairs - oldpairs, "stripped source + stripped target",
           npairs, len(set(devset).intersection(pairs))))

    return pairs

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-sourcelang', default='fr')
    parser.add_argument('-targetlang', default='en')
    parser.add_argument('-devset',
                        help='correct pairs in dev set',
                        type=argparse.FileType('r'))
    parser.add_argument('-pairs',
                        help='write matched pairs to this file',
                        type=argparse.FileType('w'))
    parser.add_argument('-wins',
                        help='write correct pairs to this file',
                        type=argparse.FileType('w'))
    parser.add_argument('-fails',
                        help='write fails to this file',
                        type=argparse.FileType('w'))
    args = parser.parse_args(sys.argv[1:])

    source_urls, target_urls, other_urls = read_urls(
        sys.stdin, args.sourcelang, args.targetlang)

    sys.stderr.write("Read %d/%d/%d %s/%s/other URLs from stdin\n" % (
        len(source_urls), len(target_urls), len(other_urls), args.sourcelang,
        args.targetlang))

    devset = None
    if args.devset:
        devset = read_reference(args.devset)
        sys.stderr.write("Read %d url pairs from %s\n" %
                         (len(devset), args.devset.name))

        unreachable = []
        for source_url, target_url in devset:
            if source_url not in source_urls:
                sys.stderr.write(
                    "Source URL %s not found in candidate URLs\n" % source_url)
                unreachable.append(source_url)
            if target_url not in target_urls:
                sys.stderr.write(
                    "Target URL %s not found in candidate URLs\n" % target_url)
                unreachable.append(target_url)

        sys.stderr.write("%d urls missing from candidate URLs\n" %
                         (len(unreachable)))

    source_stripped = strip_urls(source_urls, args.sourcelang)
    target_stripped = strip_urls(target_urls, args.targetlang)
    print "%d/%d stripped source/target urls" % (len(source_stripped),
                                                 len(target_stripped))

    pairs = find_pairs(source_urls, target_urls,
                       source_stripped, target_stripped,
                       devset)
    del source_stripped, target_stripped
    sys.stderr.write("Total: %d candidate pairs\n" % (len(set(pairs))))

    # Filter pairs so that every url only occurs once
    pairs_s2t, pairs_t2s = {}, {}
    for su, tu in pairs:
        if su not in pairs_s2t and tu not in pairs_t2s:
            pairs_s2t[su] = tu
            pairs_t2s[tu] = su

            if args.pairs:
                args.pairs.write("%s\t%s\n" % (su, tu))

    sys.stderr.write(
        "Keeping %d pairs after enforcing 1-1 rule\n" % (len(pairs_s2t)))
    if devset:
        sys.stderr.write("%d pairs from devset\n" %
                         (len(set(devset).intersection(pairs_s2t.items()))))

    # write wins and fails
    if args.fails:
        for su, tu in set(devset).difference(pairs_s2t.items()):
            if su in pairs_s2t:
                args.fails.write("S2T MISMATCH: %s\t->\t%s\texpected: %s\n" %
                                 (su, pairs_s2t[su], tu))
            if tu in pairs_t2s:
                args.fails.write("T2S MISMATCH: %s\t->\t%s\texpected: %s\n" %
                                 (tu, pairs_t2s[tu], tu))
            if su not in pairs_s2t and tu not in pairs_t2s:
                args.fails.write("Missing: %s\t->\t%s\n" %
                                 (su, tu))

            if (su, tu) in pairs:
                args.fails.write("Was in pairs\n")

    if args.wins:
        for su, tu in set(devset).intersection(pairs_s2t.items()):
            args.wins.write("%s\t%s\n" % (su, tu))

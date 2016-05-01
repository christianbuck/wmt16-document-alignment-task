#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import gzip
import sys
from collections import namedtuple

Page = namedtuple(
    "Page", "url, html, text, mime_type, encoding, lang")


def read_lett_iter(f, decode=True):
    fh = f
    fh.seek(0)
    if f.name.endswith('.gz'):
        fh = gzip.GzipFile(fileobj=fh, mode='r')
    for line in fh:
        lang, mime, enc, url, html, text = line[:-1].split("\t")

        html = base64.b64decode(html)
        text = base64.b64decode(text)

        if decode:
            html = html.decode("utf-8")
            text = text.decode("utf-8")

        p = Page(url, html, text, mime, enc, lang)
        yield p


def write_lett(page, fh):
    html = page.html
    if isinstance(html, unicode):
        html = html.encode('utf-8')

    text = page.text
    if isinstance(text, unicode):
        text = text.encode('utf-8')

    fh.write("\t".join(
        [page.lang,
         page.mime_type,
         page.encoding,
         page.url,
         base64.b64encode(html),
         base64.b64encode(text)]) + "\n")


def read_lett(f, source_language, target_language):
    source_corpus, target_corpus = {}, {}
    for p in read_lett_iter(f):

        if p.lang == source_language:
            source_corpus[p.url] = p
        elif p.lang == target_language:
            target_corpus[p.url] = p
        else:  # ignore all other languages
            pass
    return source_corpus, target_corpus


def write_tokenized_lett(f, pages):
    pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'lettfile', help='input lett file', type=argparse.FileType('r'))
    parser.add_argument('-slang', help='source language', default='en')
    parser.add_argument('-tlang', help='target language', default='fr')
    args = parser.parse_args()

    # read source and target corpus
    source_corpus, target_corpus = read_lett(
        args.lettfile, args.slang, args.tlang)

    sys.stderr.write("Read %d %s docs and %d %s docs from %s\n" %
                     (len(source_corpus), args.slang,
                      len(target_corpus), args.tlang, args.lettfile.name))

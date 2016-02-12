#!/usr/bin/env bash

zcat lett.train/*.lett.gz | cut -f 1,4 | python match_url_pairs.py  -pairs predicted.pairs -devset train.pairs
echo '\n\nRunning eval\n\n'
python eval.py train.pairs predicted.pairs

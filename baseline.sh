#!/usr/bin/env bash

zcat lett.train/*.lett.gz | cut -f 1,4 | python match_url_pairs.py  -pairs predicted.pairs -devset train.pairs
echo -e '\nRunning eval\n'
python eval.py train.pairs predicted.pairs

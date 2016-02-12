#!/usr/bin/env python
# -*- coding: utf-8 -*-

from languagestripper import LanguageStripper
import unittest


class TestQueryStripping(unittest.TestCase):

    def runTest(self):
        language_stripper = LanguageStripper(
            languages=['fr'])

        self.assertEqual(language_stripper.strip_uri(
            'http://bla.com?lang=fr'), ('http://bla.com', True))
        self.assertEqual(language_stripper.strip_uri(
            'http://bla.com?lang=1'), ('http://bla.com?lang=1', False))

        language_stripper = LanguageStripper(
            languages=['fr'], strip_query_variables=True)

        self.assertEqual(language_stripper.strip_uri(
            'http://bla.com?lang=fr'), ('http://bla.com', True))
        self.assertEqual(language_stripper.strip_uri(
            'http://bla.com?lang=1'), ('http://bla.com', True))
        self.assertEqual(language_stripper.strip_uri(
            'http://bla.com/?clang=1'), ('http://bla.com/', True))


class TestPathStripping(unittest.TestCase):

    def runTest(self):
        language_stripper = LanguageStripper(
            languages=['fr'])

        self.assertEqual(language_stripper.strip_uri(
            'http://bla.com/fr/x'), ('http://bla.com/x', True))
        self.assertEqual(language_stripper.strip_uri(
            'http://bla.com/FR/x'), ('http://bla.com/x', True))
        self.assertEqual(language_stripper.strip_uri(
            'http://bla.com/fr-FR/x'), ('http://bla.com/x', True))

        # remove multiple
        self.assertEqual(language_stripper.strip_uri(
            'http://bla.com/fr-FR/fr'), ('http://bla.com', True))

        # removing only the language identifier
        self.assertEqual(language_stripper.strip_uri(
            'http://bla.com/lang-FR/x'), ('http://bla.com/lang/x', True))

        # keep / at the end consistent
        self.assertEqual(language_stripper.strip_uri(
            'http://bla.com/x/fr'), ('http://bla.com/x', True))
        self.assertEqual(language_stripper.strip_uri(
            'http://bla.com/x/fr/'), ('http://bla.com/x/', True))

        # removing bits from them middle of a path part
        self.assertEqual(language_stripper.strip_uri(
            'http://bla.com/lang-FR-foo/x'), ('http://bla.com/lang-foo/x', True))
        self.assertEqual(language_stripper.strip_uri(
            'http://bla.com/lang-fr-FR-foo/x'), ('http://bla.com/lang-foo/x', True))

        # mixed languages
        language_stripper = LanguageStripper(
            languages=['fr', 'en'])
        self.assertEqual(language_stripper.strip_uri(
            'http://bla.com/x/fr/'), ('http://bla.com/x/', True))
        self.assertEqual(language_stripper.strip_uri(
            'http://bla.com/x/en/'), ('http://bla.com/x/', True))
        self.assertEqual(language_stripper.strip_uri(
            'http://bla.com/x/en/fr/'), ('http://bla.com/x/', True))

if __name__ == '__main__':
    unittest.main()

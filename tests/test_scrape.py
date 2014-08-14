# -*- coding: utf-8 -*-

from __future__ import division

import unittest
from nose.tools import *
from nose_parameterized import parameterized

import os

from sciscrape.utils import pubtools
from sciscrape.scrapetools import scrape

FIXTURE_PATH = 'tests/fixtures'
MAX_DIFF = 0.05

from diff_match_patch import diff_match_patch
differ = diff_match_patch()

def diff_ratio(txt1, txt2):
    diffs = differ.diff_main(txt1, txt2)
    num_diff_chars = sum([
        len(diff[1])
        for diff in diffs
        if diff[0] != 0
    ])
    avg_txt_length = (len(txt1) + len(txt2)) / 2
    return num_diff_chars / avg_txt_length

class TestScrapeMethods(unittest.TestCase):

    def setUp(self):

        pubtools.email = 'foo@bar.baz'
        self.scrape = scrape.Scrape()

    def test_resolve_doi(self):

        url = self.scrape._resolve_doi('10.1016/j.jmr.2013.08.010')
        assert_equal(url, 'http://www.sciencedirect.com/science/article/pii/S1090780713002061')

    def test_resolve_pmid(self):

        url = self.scrape._resolve_pmid('24091140')
        assert_equal(url, 'http://www.sciencedirect.com/science/article/pii/S1090780713002061')

class TestScrapeOpen(unittest.TestCase):

    def setUp(self):

        pubtools.email = 'foo@bar.baz'
        self.scrape = scrape.Scrape()

    def test_scrape_plos(self):

        info = self.scrape.scrape(pmid='23638070')

        for document_type in ['html', 'pdf', 'pmc']:
            assert_in(document_type, info.docs)
            diff = diff_ratio(
                info.docs[document_type],
                open(
                    os.path.join(
                        FIXTURE_PATH,
                        '23638070',
                        '23638070.{}'.format(document_type)),
                ).read()
            )
            assert_less(diff, MAX_DIFF)


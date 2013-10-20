import unittest
from nose.tools import *
from nose_parameterized import parameterized

from sciscrape.utils import mechtools
from sciscrape.scrapetools import scrape

from .fixtures import fixtures

import urlparse

def build_name(fixture, document_type):
    return '{}_{}_{}'.format(fixture.publisher, fixture.pmid, document_type)

def fixture_to_params(fixture):
    return [
        (
            build_name(fixture, document_type),
            fixture.publisher,
            fixture.pmid,
            document_type,
            fixture.start_url,
            expected_url
        )
        for document_type, expected_url in fixture.expected_urls.iteritems()
        if expected_url is not None
    ]

def fixtures_to_params(fixtures):
    return sum([
        fixture_to_params(fixture)
        for fixture in fixtures
    ], [])

def remove_qs(url):

    url_clean = urlparse.urlparse(url)._replace(query=None)
    return urlparse.urlunparse(url_clean)

def equal_modulo_qs(url1, url2):

    return url1 == url2 or \
            remove_qs(url1) == remove_qs(url2)

class TestGetters(unittest.TestCase):

    def setUp(self):

        self.browser = mechtools.PubBrowser(agent='sciscrape')
        self.info = scrape.ScrapeInfo()

    @parameterized.expand(fixtures_to_params(fixtures))
    def test_getter(self, _, publisher, pmid, document_type, start_url, expected_url):
        """Test that document getter browses to the expected URL.

        :param _: Test name; used by nose_parameterized
        :param publisher: Publisher name
        :param pmid: PubMed ID of article
        :param document_type: Document type (html, pdf, pmc)
        :param start_url: Starting URL
        :param expected_url: Expected URL

        """
        # Browse to starting URL and cache documents
        self.browser.open(start_url)
        self.info.pmid = pmid
        self.info.init_html, self.info.init_qhtml = self.browser.get_docs()

        # Get download link
        html_getter = scrape.getter_map[document_type][publisher]()
        html_getter.get(self.info, self.browser)

        # Check download link
        assert_true(equal_modulo_qs(self.browser.geturl(), expected_url))

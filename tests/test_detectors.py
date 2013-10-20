import unittest
from nose.tools import *
from nose_parameterized import parameterized

from sciscrape.utils import mechtools
from sciscrape.scrapetools import pubdet

from .fixtures import fixtures

def build_name(fixture):
    return '{}_{}'.format(fixture.publisher, fixture.pmid)

def fixture_to_param(fixture):
    return [
        (
            build_name(fixture),
            fixture.publisher,
            fixture.start_url,
        )
    ]

def fixtures_to_params(fixtures):
    return sum([
        fixture_to_param(fixture)
        for fixture in fixtures
    ], [])

tests = fixtures_to_params(fixtures)

class TestDetectors(unittest.TestCase):

    def setUp(self):

        self.browser = mechtools.PubBrowser(agent='sciscrape')

    @parameterized.expand(tests)
    def test_detect(self, name, publisher, start_url):
        """Test that publishers are correctly detected.

        :param name: Test name; used by nose_parameterized
        :param publisher: Correct publisher name
        :param start_url: Staring URL

        """
        self.browser.open(start_url)
        init_html, init_qhtml = self.browser.get_docs()
        assert_equal(publisher, pubdet.pubdet(init_html))

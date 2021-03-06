import unittest
from nose.tools import *
from nose_parameterized import parameterized

from sciscrape.utils import mechtools
from sciscrape.scrapetools import scrape
from sciscrape.exceptions import NoAccessError, NotFoundError

params = [

    # ScienceDirect
    ('elsevier_access', 'elsevier', 'http://www.sciencedirect.com/science/article/pii/S1053811913004539', True),
    ('elsevier_no_access', 'elsevier', 'http://www.sciencedirect.com/science/article/pii/S1053811913005442', False),

    # Highwire
    ('highwire_access', 'highwire', 'http://cercor.oxfordjournals.org/content/23/7/1572.abstract', True),
    ('highwire_no_access', 'highwire', 'http://cercor.oxfordjournals.org/content/24/9/2297.abstract', False),

    # Wiley
    ('wiley_access', 'wiley', 'http://onlinelibrary.wiley.com/doi/10.1002/hbm.22150/full', True),
    ('wiley_no_access', 'wiley', 'http://onlinelibrary.wiley.com/doi/10.1002/hbm.21440/abstract', False),

    # Springer
    ('springer_access', 'springer', 'http://link.springer.com/article/10.3758/s13415-012-0141-7', True),
    ('springer_no_access', 'springer', 'http://link.springer.com/article/10.1007/s12273-013-0136-5', False),

    # Thieme
    ('thieme_access', 'thieme', 'https://www.thieme-connect.com/ejournals/abstract/10.1055/s-0033-1346973', True),
    ('thieme_no_access', 'thieme', 'https://www.thieme-connect.com/DOI/DOI?10.1055/s-2008-1071333', False),

    # Wolters Kluwer
    ('wolterskluwer_access', 'wolterskluwer', 'http://pt.wkhealth.com/pt/re/lwwgateway/landingpage.htm;jsessionid=TtBHlTny2RTlkdpbQKLH32QrRThGzQGtZ41d8j04mQXvsKNsMN5h!-773986214!181195628!8091!-1?issn=0959-4965&volume=25&issue=13&spage=1038', True),
    ('wolterskluwer_no_access', 'wolterskluwer', 'http://pt.wkhealth.com/pt/re/lwwgateway/landingpage.htm;jsessionid=TtDXBnQxQ5KKcmtJWW8rZpykZyNTQgnT3GXJYnFD5Nn6TkmyRJG0!-773986214!181195628!8091!-1?issn=0959-4965&volume=24&issue=14&spage=768', False),

    # IEEE
    ('ieee_access', 'ieee', 'http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=6527311', True),
    ('ieee_no_access', 'ieee', 'http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=4527218', False),

    # Informa
    ('informa_access', 'informa', 'http://informahealthcare.com/doi/abs/10.3109/08990220.2010.513111', True),
    ('informa_no_access', 'informa', 'http://informahealthcare.com/doi/abs/10.3109/08990220.2012.686935', False),

    # Cambridge
    ('cambridge_access', 'cambridge', 'http://journals.cambridge.org/action/displayAbstract?aid=9040968', True),
    ('cambridge_no_access', 'cambridge', 'http://journals.cambridge.org/action/displayAbstract?aid=9040962', False),

    # APA Psychiatry
    ('apa_psychiatry_access', 'apa_psychiatry', 'http://ajp.psychiatryonline.org/article.aspx?articleid=176149', True),
    ('apa_psychiatry_no_access', 'apa_psychiatry', 'http://ajp.psychiatryonline.org/article.aspx?articleid=1712527', False),

    # Maney
    ('maney_access', 'maney', 'http://www.maneyonline.com/doi/full/10.1179/1743132811Y.0000000049', True),
    ('maney_no_access', 'maney', 'http://www.maneyonline.com/doi/full/10.1179/1743132814Y.0000000337', False),

]

class TestAccess(unittest.TestCase):

    def setUp(self):

        self.browser = mechtools.PubBrowser(agent='sciscrape')
        self.info = scrape.ScrapeInfo()

    @parameterized.expand(params)
    def test_access(self, _, publisher, start_url, has_access):
        """Test that document getter browses to the expected URL.

        :param _: Test name; used by nose_parameterized
        :param publisher: Publisher name
        :param start_url: Starting URL
        :param has_access: Should the default scraper have access?

        """
        # Browse to starting URL and cache documents
        self.browser.open(start_url)
        self.info.init_html, self.info.init_qhtml = self.browser.get_docs()

        # Get download link
        html_getter = scrape.getter_map['html'][publisher]()

        # Getting should not raise error
        if has_access:
            html_getter.get(self.info, self.browser)

        # Getting should raise error
        else:
            with assert_raises(Exception) as error:
                html_getter.get(self.info, self.browser)
            assert_true(
                type(error.exception) in [NoAccessError, NotFoundError]
            )

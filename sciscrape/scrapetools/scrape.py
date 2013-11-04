"""
Utilities for converting between article IDs (DOI and PubMed ID)
and full-text documents. Scrape objects can use the scrape() method
to take an article ID, browse to the publisher's page, determine
which publisher is hosting the article, and download the full-text
files using the appropriate Getter classes from getters.py.
"""

# Imports
import os
import re
import logging
import urlparse
import collections
from urllib2 import HTTPError, URLError
from httplib import HTTPException

# Project imports
from sciscrape.scrapetools import pubdet
from sciscrape.scrapetools import getters
from sciscrape.utils import utils
from sciscrape.utils import pubtools
from sciscrape.utils import mechtools
from sciscrape.utils import pmid_doi
from sciscrape.utils import retry
from sciscrape.exceptions import ScrapeError, BadDOIError

# Set email
pubtools.email = 'foo@bar.com'

# URLs
DOI_URL = 'http://dx.doi.org/'
PUBMED_URL = 'http://www.ncbi.nlm.nih.gov/pubmed/'

EXTENSIONS = {
    'pmc': 'pmc',
    'html': 'html',
    'pdf': 'pdf',
}

# Default getters
# Covers Frontiers, NAS, Oxford, Highwire, Wiley, Springer
getter_map = {
    'html': collections.defaultdict(lambda: getters.MetaHTMLGetter),
    'pdf': collections.defaultdict(lambda: getters.MetaPDFGetter),
    'pmc': collections.defaultdict(lambda: getters.PMCGetter),
}

# Publisher-specific getters
getter_map['html']['plos'] = getters.PassHTMLGetter
getter_map['html']['npg'] = getters.PassHTMLGetter

getter_map['html']['elsevier'] = getters.ElsevierHTMLGetter
getter_map['pdf']['elsevier'] = getters.ElsevierPDFGetter

getter_map['html']['wiley'] = getters.WileyHTMLGetter

getter_map['pdf']['npg'] = getters.NPGPDFGetter

getter_map['html']['npg_old'] = getters.NPGOldHTMLGetter
getter_map['pdf']['npg_old'] = getters.NPGOldPDFGetter

getter_map['html']['mit'] = getters.MITHTMLGetter
getter_map['pdf']['mit'] = getters.MITPDFGetter

getter_map['html']['tandf'] = getters.TaylorFrancisHTMLGetter
getter_map['pdf']['tandf'] = getters.TaylorFrancisPDFGetter

getter_map['html']['thieme'] = getters.ThiemeHTMLGetter
getter_map['pdf']['thieme'] = getters.ThiemePDFGetter

getter_map['html']['apa'] = getters.APAHTMLGetter
getter_map['pdf']['apa'] = getters.APAPDFGetter

getter_map['html']['wolterskluwer'] = getters.WoltersKluwerHTMLGetter
getter_map['pdf']['wolterskluwer'] = getters.WoltersKluwerPDFGetter

getter_map['html']['ieee'] = getters.IEEEHTMLGetter
getter_map['pdf']['ieee'] = getters.IEEEPDFGetter

getter_map['html']['springer'] = getters.SpringerHTMLGetter
getter_map['pdf']['springer'] = getters.MetaPDFGetter

getter_map['html']['informa'] = getters.InformaHTMLGetter
getter_map['pdf']['informa'] = getters.InformaPDFGetter

getter_map['html']['ios'] = getters.IOSHTMLGetter
getter_map['pdf']['ios'] = getters.IOSPDFGetter

getter_map['html']['cambridge'] = getters.CambridgeHTMLGetter

class ScrapeInfo(object):
    
    def __init__(self, doi=None, pmid=None):
        
        # Initialize identifiers
        self.doi = doi
        self.pmid = pmid

        # Initialize documents
        self.docs = {}
        self.status = {}
    
    @property
    def pretty_status(self):
        return '; '.join(['%s: %s' % (k, self.status[k]) for k in self.status])

    def save(self, name, save_dir='.', save_dirs=None):
        """

        """

        save_dirs = save_dirs or {}
        saved = {}

        # Write documents
        for doc_type in self.docs:

            doc_save_dir = save_dirs.get(doc_type, save_dir)

            # Make directory if necessary
            if doc_save_dir != '.':
                utils.mkdir_p(doc_save_dir)

            file_name = '{}.{}'.format(name, EXTENSIONS[doc_type])
            save_name = os.path.join(doc_save_dir, file_name)

            with open(save_name, 'w') as f:
                f.write(self.docs[doc_type])

            saved[doc_type] = {
                'name': file_name,
                'path': doc_save_dir,
            }

        return saved

class Scrape(object):

    # Browser class
    _browser_klass = mechtools.PubBrowser

    def __init__(self, agent='sciscrape', timeout=None, **kwargs):
        
        self.browser = self._browser_klass(
            agent=agent, timeout=timeout, **kwargs
        )
        self.info = ScrapeInfo()
    
    def scrape(self, doi=None, pmid=None, fetch_pmid=True, fetch_types=None):
        """Download documents for a target article.

        :param doi: Article DOI
        :param pmid: Article PubMed ID
        :param fetch_pmid: Look up PMID if not provided
        :return: ScrapeInfo instance

        """
        # Initialize ScrapeInfo object to store results
        self.info = ScrapeInfo(doi, pmid)
        
        # Get publisher link
        pub_link = None
        if doi:
            try:
                pub_link = self._resolve_doi(doi)
            except BadDOIError:
                logging.debug('Could not resolve DOI {}'.format(doi))
            if not pmid and fetch_pmid:
                logging.debug('Looking up PMID by DOI')
                self.info.pmid = pmid_doi.pmid_doi({'doi': doi})['pmid']
        if pmid and not pub_link:
            pub_link = self._resolve_pmid(pmid)

        # Quit if no publisher link found
        if not pub_link:
            raise ScrapeError('No publisher link found')
        
        # Log publisher link to ScrapeInfo
        self.info.pub_link = pub_link
        
        # Detect publisher
        self.info.publisher = pubdet.pubdet(self.info.init_html)

        # Get documents
        for doc_type in getter_map:

            # Skip documents not to be included
            if fetch_types and doc_type not in fetch_types:
                continue
            
            # Browser to publisher link
            if self.browser.geturl() != pub_link:
                self.browser.reopen(pub_link)

            # Identify getter
            getter = getter_map[doc_type][self.info.publisher]()
            
            # Get document
            try:
                # Success
                get_success = getter.reget(self.info, self.browser)
                self.info.docs[doc_type] = self.info.html
                self.info.status[doc_type] = 'Success'
            except Exception as error:
                # Failure
                self.info.status[doc_type] = repr(error)
        
        # Return ScrapeInfo object
        return self.info


    @retry.retry((HTTPError, HTTPException, URLError), tries=3, default='')
    def _resolve_doi(self, doi):
        """Follow DOI link, store HTML, and return final URL."""
        
        # Open DOI link
        self.browser.open(urlparse.urljoin(DOI_URL, doi))
        
        # Read documents and save in ScrapeInfo
        self.info.init_html, self.info.init_qhtml = self.browser.get_docs()
        
        # Check for bad DOI
        if self.info.init_qhtml:
            title_text = self.info.init_qhtml('title').text()
            if title_text and re.search(r'doi not found', title_text, re.I):
                raise BadDOIError(doi)
        
        # Return URL
        return self.browser.geturl()

    @retry.retry((HTTPError, HTTPException, URLError), tries=3, default='')
    def _resolve_pmid(self, pmid):
        """Follow PMID link, store HTML, and return final URL."""
        
        # Get DOI from PubMed API
        pub_data = pubtools.download_pmids([pmid])[0]
        doi = pubtools.record_to_doi(pub_data)
        if doi:
            return self._resolve_doi(doi)

        pub_link = pubtools.pmid_to_publisher_link(pmid)
        
        # Follow publisher link
        if pub_link:

            # Browse to link
            self.browser.open(pub_link)

            # Read documents and save in ScrapeInfo
            self.info.init_html, self.info.init_qhtml = self.browser.get_docs()

            # Return URL
            return self.browser.geturl()

class UMScrape(Scrape):
    
    _browser_klass = mechtools.UMBrowser

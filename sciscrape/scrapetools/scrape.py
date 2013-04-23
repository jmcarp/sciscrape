'''
Utilities for converting between article IDs (DOI and PubMed ID)
and full-text documents. Scrape objects can use the scrape() method
to take an article ID, browse to the publisher's page, determine
which publisher is hosting the article, and download the full-text
files using the appropriate Getter classes from getters.py.
'''

# Imports
import re
import urllib2
import collections

# Project imports
from sciscrape.scrapetools import pubdet
from sciscrape.scrapetools import getters
from sciscrape.utils import utils
from sciscrape.utils import pubtools
from sciscrape.utils import mechtools
from sciscrape.utils import pmid_doi

# Set email
pubtools.email = 'foo@bar.com'

# Default getters
# Covers PLOS, Frontiers, NAS, Oxford, Highwire, Wiley, Springer
getter_map = {
    'html' : collections.defaultdict(lambda: getters.MetaHTMLGetter),
    'pdf' : collections.defaultdict(lambda: getters.MetaPDFGetter),
    'pmc' : collections.defaultdict(lambda: getters.PMCGetter),
}

# Publisher-specific getters
getter_map['html']['elsevier'] = getters.ElsevierHTMLGetter
getter_map['pdf']['elsevier'] = getters.ElsevierPDFGetter

getter_map['html']['npg'] = getters.NPGHTMLGetter
getter_map['pdf']['npg'] = getters.NPGPDFGetter

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

class BadDOIException(Exception): pass

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

    def save(self, save_dir='.', save_dirs={}, id_type='doi'):
        '''

        '''
        
        # Try to get document ID
        if hasattr(self, id_type):
            id = getattr(self, id_type)
        elif hasattr(self, 'doi'):
            id = getattr(self, 'doi')
        elif hasattr(self, 'pmid'):
            id = getattr(self, 'pmid')
        else:
            # TODO: Write default name
            return
        
        # Replace /s in ID
        id = id.replace('/', '__')
        
        # Make directory if necessary
        utils.mkdir_p(save_dir)

        # Write documents
        for doc_type in self.docs:
            if doc_type in save_dirs:
                save_name = '%s/%s.%s' % (save_dirs[doc_type], id, doc_type)
            else:
                save_name = '%s/%s.%s' % (save_dir, id, doc_type)
            with open(save_name, 'w') as f:
                f.write(self.docs[doc_type])

class Scrape(object):
    
    # URLs
    _doi_url = 'http://dx.doi.org'
    _pubmed_url = 'http://www.ncbi.nlm.nih.gov/pubmed'

    # Browser class
    _browser_klass = mechtools.PubBrowser

    def __init__(self, agent='sciscrape'):
        
        self.browser = self._browser_klass(agent=agent)
        self.info = ScrapeInfo()
    
    def scrape(self, doi=None, pmid=None, fetch_pmid=True):
        '''Download documents for a target article.

        Args:
            doi : Article DOI
            pmid : Article PubMed ID
            fetch_pmid : Look up PMID if not provided
        Returns:
            ScrapeInfo instance

        '''
        
        # Initialize ScrapeInfo object to store results
        self.info = ScrapeInfo(doi, pmid)
        
        # Get publisher link
        pub_link = None
        if doi:
            pub_link = self._resolve_doi(doi)
            if not pmid and fetch_pmid:
                self.info.pmid = pmid_doi.pmid_doi({'doi' : doi})['pmid']
        if pmid and not pub_link:
            pub_link = self._resolve_pmid(pmid)

        # Quit if no publisher link found
        if not pub_link:
            return
        
        # Log publisher link to ScrapeInfo
        self.info.pub_link = pub_link
        
        # Detect publisher
        self.info.publisher = pubdet.pubdet(self.info.init_html)

        # Get documents
        for doc_type in getter_map:
            if self.browser.geturl() != pub_link:
                self.browser.open(pub_link)
            getter = getter_map[doc_type][self.info.publisher]()
            try:
                get_success = getter.reget(self.info, self.browser)
                self.info.docs[doc_type] = self.info.html
                self.info.status[doc_type] = 'Success'
            except Exception as e:
                self.info.status[doc_type] = '%s, %s' % ('Fail', e.message)
        
        # Return ScrapeInfo object
        return self.info

    def _resolve_doi(self, doi):
        '''Follow DOI link, store HTML, and return final URL.'''
        
        # Try to open DOI link, else raise BadDOIException
        try:
            self.browser.open('%s/%s' % (self._doi_url, doi))
        except urllib2.HTTPError:
            raise BadDOIException
        
        # Read documents and save in ScrapeInfo
        self.info.init_html, self.info.init_qhtml = self.browser.get_docs()
        
        # Check for bad DOI
        if re.search('doi not found',
                     self.info.init_qhtml('title').text(),
                     re.I):
            raise BadDOIException
        
        # Return URL
        return self.browser.geturl()

    def _resolve_pmid(self, pmid):
        '''Follow PMID link, store HTML, and return final URL.'''
        
        # Get DOI from PubMed API
        pminfo = pubtools.pmid_to_document(pmid)
        if 'doi' in pminfo:
            return self._resolve_doi(pminfo['doi'])
        
        # Get publisher link from PubMed site
        self.browser.open('%s/%s' % (self._pubmed_url, pmid))
        html, qhtml = self.browser.get_docs()
        pub_link = qhtml('a[title^=Full text]').attr('href')
        
        # Follow publisher link
        if pub_link:

            # Browse to link
            self.browser.open(pub_link)

            # Read documents and save in ScrapeInfo
            self.info.init_html, self.info.init_qhtml = self.browser.get_docs()

class UMScrape(Scrape):
    
    _browser_klass = mechtools.UMBrowser


# Imports
import collections

# Project imports
import pubdet
import getters
import pubtools
import mechtools

# Default getters
# Covers PLOS, Frontiers, NAS, Oxford, Highwire, Wiley, Springer
getter_map = collections.defaultdict(lambda: {
    'html' : getters.MetaHTMLGetter,
    'pdf'  : getters.MetaPDFGetter,
})

# Publisher-specific getters
getter_map['elsevier'] = {
    'html' : getters.ElsevierHTMLGetter,
    'pdf' : getters.ElsevierPDFGetter,
}
getter_map['npg'] = {
    'html' : getters.NPGHTMLGetter,
    'pdf' : getters.NPGPDFGetter,
}
getter_map['tandf'] = {
    'html' : getters.TaylorFrancisHTMLGetter,
    'pdf' : getters.TaylorFrancisPDFGetter,
}
getter_map['thieme'] = {
    'html' : getters.ThiemeHTMLGetter,
    'pdf' : getters.ThiemePDFGetter,
}
getter_map['apa'] = {
    'html' : getters.APAHTMLGetter,
    'pdf' : getters.APAPDFGetter,
}
getter_map['wolterskluwer'] = {
    'html' : getters.WoltersKluwerHTMLGetter,
    'pdf' : getters.WoltersKluwerPDFGetter,
}

class ScrapeInfo(object):
    
    def __init__(self, doi=None, pmid=None):
        
        # Initialize identifiers
        self.doi = doi
        self.pmid = pmid

        # Initialize documents
        self.docs = {}

class SciScrape(object):
    
    # URLs
    _doi_url = 'http://dx.doi.org'
    _pubmed_url = 'http://www.ncbi.nlm.nih.gov/pubmed'

    # Browser class
    _browser_klass = mechtools.PubBrowser

    def __init__(self):
        
        self.browser = self._browser_klass()#mechtools.UMBrowser()
        self.info = ScrapeInfo()
    
    def scrape(self, doi=None, pmid=None):
        
        # Initialize ScrapeInfo object to store results
        self.info = ScrapeInfo(doi, pmid)
        
        # Get publisher link
        pub_link = None
        if doi:
            pub_link = self._resolve_doi(doi)
        if pmid and not pub_link:
            pub_link = self._resolve_pmid(pmid)
        if not pub_link:
            return
        self.info.pub_link = pub_link
        
        # Detect publisher
        self.info.publisher = pubdet.pubdet(self.info.init_html)

        # Get documents
        getters = getter_map[self.info.publisher]
        for doc_type in getters:
            if self.browser.geturl() != pub_link:
                self.browser.open(pub_link)
            getter = getters[doc_type]()
            get_success = getter.get(self.info, self.browser)
            if get_success:
                self.info.docs[doc_type] = self.info.html
        
        # Return ScrapeInfo object
        return self.info

    def _resolve_doi(self, doi):
        '''Follow DOI link, store HTML, and return final URL.'''
        
        self.browser.open('%s/%s' % (self._doi_url, doi))
        self.info.init_html, self.info.init_qhtml = self.browser.get_docs()
        return self.browser.geturl()

    def _resolve_pmid(self, pmid):
        '''Follow PMID link, store HTML, and return final URL.'''
        
        # Get DOI from PubMed API
        pminfo = pubtools.pmid_to_document(pmid)
        if 'doi' in pminfo:
            print 'foo', pminfo['doi']
            return self._resolve_doi(pminfo['doi'])
        
        # Get publisher link from PubMed site
        self.browser.open('%s/%s' % (self._pubmed_url, pmid))
        html, qhtml = self.browser.get_docs()
        pub_link = qhtml('a[title^=Full text]').attr('href')
        if pub_link:
            print 'bar', pub_link
            self.browser.open(pub_link)
            self.info.init_html, self.info.init_qhtml = self.browser.get_docs()

class UMSciScrape(SciScrape):
    
    _browser_klass = mechtools.UMBrowser


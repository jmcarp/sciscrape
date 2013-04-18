# Imports
import re
import json
import urlparse
from pyquery import PyQuery

# Project imports
import retry
import utils

class NoAccessException(Exception): pass
class BadDocumentException(Exception): pass

class AccessRule(object):
    '''Base class for access checkers.'''
    
    def __call__(self, text, qtext):
        raise NotImplementedError('Subclasses must implement check()')

class RegexAccessRule(AccessRule):
    '''Access checker using regex on article text.'''
    
    def __init__(self, regex, flags=re.I):
        self.regex = regex
        self.flags = flags

    def __call__(self, text, qtext):
        return bool(re.search(self.regex, text, self.flags))

class ElsevierAccessRule(AccessRule):
    '''Custom black-list rule for Elsevier HTML documents.'''
    
    def __call__(self, text, qtext):
        return not bool(qtext('.svArticle.section'))
        #return not bool(qtext('.svArticle'))

class DocGetter(object):
    '''Base class for document getters.'''
    
    def get_link(self, cache):
        
        pass

    def validate(self, cache):

        return True
    
    # Access white-list functions
    _access_wlist = [
        RegexAccessRule('identitieswelcome'),
    ]
    
    # Access black-list functions
    _access_blist = [
        RegexAccessRule('why don\'t i have access'),
        RegexAccessRule('add this item to your shopping cart'),
        RegexAccessRule('access to this content is restricted'),
        RegexAccessRule('full content is available to subscribers'),
        RegexAccessRule('options for acessing this content'),
        RegexAccessRule('the requested article is not currently available'),
    ]

    def check_access(self, text, qtext):
        '''Check whether we have access to an article.'''
        
        # Check white-list functions
        for wfun in self._access_wlist:
            if wfun(text, qtext):
                return True

        # Check black-list functions
        for bfun in self._access_blist:
            if bfun(text, qtext):
                return False

        # If no hits, article is valid
        return True

    def get(self, cache, browser):
        '''Download document, then store in cache.'''
        
        # Get document link
        link = self.get_link(cache, browser)

        # Open document link
        if link:
            browser.open(link)
            cache.html, cache.qhtml = browser.get_docs()
        else:
            cache.html, cache.qhtml = cache.init_html, cache.init_qhtml
        
        # Check access
        if not self.check_access(cache.html, cache.qhtml):
            raise NoAccessException('No access')

        # Validate result
        if not self.validate(cache.html):
            raise BadDocumentException('Bad document')
        
        return True
    
    @retry.retry(Exception)
    def reget(self, cache, browser):
        return self.get(cache, browser)

class MetaGetter(DocGetter):
    '''Base class for getters that use <meta> tags.'''
    
    _attrs = []
    _filter = None

    def get_link(self, cache, browser):
        
        tags = cache.init_qhtml(utils.build_query(
            'meta',
            self._attrs
        ))
        
        if self._filter:
            tags = tags.filter(self._filter)
        
        return tags.attr('content')

class HTMLGetter(DocGetter):
    '''Base class for HTML getters.'''

    def validate(self, text):
        
        return not utils.ispdf(text)

class PDFGetter(DocGetter):
    
    def validate(self, text):
        
        return utils.ispdf(text)

class MetaHTMLGetter(MetaGetter, HTMLGetter):
    
    _attrs = [
        ['name', 'citation_fulltext_html_url'],
    ]

class MetaPDFGetter(MetaGetter, PDFGetter):
    
    _attrs = [
        ['name', 'citation_pdf_url'],
    ]

############
# Elsevier #
############

class ElsevierHTMLGetter(HTMLGetter):
    
    _access_blist = [
        ElsevierAccessRule(),
    ] + DocGetter._access_blist

    def get_link(self, cache, browser):
        
        redirect_links = cache.init_qhtml('a[role="button"]').filter(
            lambda: re.search('screen reader', PyQuery(this).text(), re.I)
        )
        if redirect_links:
            return PyQuery(redirect_links[0]).attr('href')

class ElsevierPDFGetter(PDFGetter):
    
    def get_link(self, cache, browser):
        
        return cache.init_qhtml('a#pdfLink')\
            .attr('pdfurl')

####################
# Taylor & Francis #
####################

class TaylorFrancisHTMLGetter(HTMLGetter):
    
    def get_link(self, cache, browser):
        
        return cache.init_qhtml('div.access a.txt')\
            .attr('href')

class TaylorFrancisPDFGetter(PDFGetter):
    
    def get_link(self, cache, browser):
        
        return cache.init_qhtml('div.access a.pdf')\
            .attr('href')

#######
# APA #
#######

class APAGetter(DocGetter):
    
    def open_splash(self, cache, browser):
        '''Browse to APA splash page for article.'''
        
        # Get link to abstract from starting page
        abstract_link = cache.init_qhtml(utils.build_query(
            'meta', 
            [['name', 'citation_abstract_html_url']]
        )).attr('content')
        
        # Get APA Accession Number from link
        apa_id_raw = abstract_link.split('journals')[-1].strip('/')
        apa_id = 'AN %s' % (apa_id_raw.replace('/', '-'))
        
        # Open APA search page
        browser.open('http://www.lib.umich.edu/database/link/27957')
        html, qhtml = browser.get_docs()

        # Hack: Identify search form action from JS
        action_str = qhtml('#SearchButton').attr('data-formsubmit')
        action_dict = json.loads(action_str)
        action_url = urlparse.urljoin(browser.geturl(), action_dict['action'])
        
        # Submit search form
        browser._b.select_form(nr=0)
        browser._b.form.action = action_url
        browser._b['GuidedSearchFormData[1].SearchTerm'] = apa_id 
        browser._b.submit(type='submit')
        
class APAHTMLGetter(APAGetter, HTMLGetter):
    
    def get_link(self, cache, browser):
        
        # Open splash page
        self.open_splash(cache, browser)
        html, qhtml = browser.get_docs()
        
        # Return full-text HTML link
        return qhtml('[title^="HTML Full Text"]').attr('href')

class APAPDFGetter(APAGetter, PDFGetter):
    
    def get_link(self, cache, browser):
        
        # Open splash page
        self.open_splash(cache, browser)
        html, qhtml = browser.get_docs()
        
        # Open PDF wrapper page
        pdf_wrap_link = qhtml('[title^="PDF Full Text"]').attr('href')
        browser.open(pdf_wrap_link)
        html, qhtml = browser.get_docs()
        
        # Return full-text PDF link
        return qhtml('iframe#pdfIframe').attr('src')

##################
# Wolters-Kluwer #
##################

class WoltersKluwerGetter(DocGetter):
    
    _access_blist = [
        RegexAccessRule('the limit for concurrent users'),
    ] + DocGetter._access_blist

    _base_url = 'http://ovidsp.ovid.com/ovidweb.cgi?' + \
        'T=JS&MODE=ovid&NEWS=n&PAGE=fulltext&D=ovft&SEARCH='

    def get_link(self, cache, browser):
        
        # Parse welcome URL
        url = browser.geturl()
        parsed_url = urlparse.urlparse(url)
        url_params = dict(urlparse.parse_qsl(parsed_url.query))
        
        # Build search string
        if 'an' in url_params:
            ovid_search = '%s.an.' % \
                (url_params['an'])
        elif all([p in url_params for p in 
                 ['issn', 'volume', 'issue', 'spage']]):
            ovid_search = '%s.is+and+%s.vo+and+%s.ip+and+%s.pg.' % \
                (url_params['issn'], url_params['volume'],
                url_params['issue'], url_params['spage'])
        else:
            raise NoAccessException('No access')
        
        # Return full-text URL
        return self._base_url + ovid_search
    
    @retry.retry(Exception, delay=180)
    def reget(self, cache, browser):
        return self.get(cache, browser)

class WoltersKluwerHTMLGetter(WoltersKluwerGetter, HTMLGetter):
    
    pass    

class WoltersKluwerPDFGetter(WoltersKluwerGetter, PDFGetter):
    
    def get_link(self, cache, browser):
        
        # Get full-text link
        link = super(WoltersKluwerPDFGetter, self)\
            .get_link(cache, browser)
        
        # Open full-text page
        browser.open(link)
        html, qhtml = browser.get_docs()
        
        # Get PDF wrapper link
        pdf_link = qhtml('a#pdf').attr('href')
        full_pdf_link = urlparse.urljoin(link, pdf_link)
        
        # Open PDF wrapper page
        browser.open(full_pdf_link)
        html, qhtml = browser.get_docs()
        
        # Get PDF link
        return qhtml('iframe').attr('src')

#############################
# Thieme Medical Publishers #
#############################

class ThiemeHTMLGetter(MetaHTMLGetter):
    
    _attrs = [
        ['name', 'DC.relation'],
    ]

    @staticmethod
    def _filter():
        return re.search(
            '\d$', 
            PyQuery(this).attr('content'), 
            re.I
        )

class ThiemePDFGetter(MetaPDFGetter):
    
    _attrs = [
        ['name', 'DC.relation'],
    ]

    @staticmethod
    def _filter():
        return re.search(
            '\.pdf$', 
            PyQuery(this).attr('content'), 
            re.I
        )

###########################
# Nature Publishing Group #
###########################

class NPGHTMLGetter(HTMLGetter):
    
    def get_link(self, cache, browser):
        
        pass

class NPGPDFGetter(PDFGetter):
    
    def get_link(self, cache, browser):
        
        return cache.init_qhtml('a.download-pdf')\
            .attr('href')

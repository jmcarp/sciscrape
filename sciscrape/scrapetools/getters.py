"""
Utilities to download documents from various publishers.
"""

import re
import json
import urllib
import urlparse
from pyquery import PyQuery

from sciscrape.utils import retry
from sciscrape.utils import utils

from sciscrape.exceptions import (
    NotFoundError, NoAccessError, BadDocumentError
)

class AccessRule(object):
    """ Base class for access checkers. """
    
    def __call__(self, text, qtext):
        raise NotImplemented('Subclasses must implement __call__')

class RegexAccessRule(AccessRule):
    """ Access checker using regex on article text. """
    
    def __init__(self, regex, flags=re.I):
        self.regex = regex
        self.flags = flags

    def __call__(self, text, qtext):
        return bool(re.search(self.regex, text, self.flags))

class ElsevierAccessRule(AccessRule):
    """ Custom black-list rule for Elsevier HTML documents. """
    
    def __call__(self, text, qtext):
        return not bool(qtext('.svArticle.section'))

class ThiemeAccessRule(AccessRule):

    def __call__(self, text, qtext):
        full_text_tab = qtext('li.tab').filter(
            lambda: PyQuery(this).text() == 'Full Text'
        )
        return not bool(full_text_tab)

class DocGetter(object):
    """ Base class for document getters. """
    
    def get_link(self, cache, browser):
        """

        """
        pass

    def post_process(self, cache, browser):
        """

        """
        pass

    def validate(self, cache):
        """

        """
        return True
    
    # Access white-list functions
    _access_whitelist = [
        RegexAccessRule('identitieswelcome'),
    ]
    
    # Access black-list functions
    _access_blacklist = [
        RegexAccessRule(r'why don\'t i have access'),
        RegexAccessRule(r'add this item to your shopping cart'),
        RegexAccessRule(r'access to this content is restricted'),
        RegexAccessRule(r'full content is available to subscribers'),
        RegexAccessRule(r'options for acessing this content'),
        RegexAccessRule(r'the requested article is not currently available'),
        RegexAccessRule(r'purchase short-term access'), # Highwire
        RegexAccessRule(r'purchase on springer.com'), # Springer
        RegexAccessRule(r'the fully formatted pdf and html versions '
                        r'are in production'), # SpringerOpen
        RegexAccessRule(r'You could be reading the full-text of this '
                        r'article now'), # LWW
    ]

    def check_access(self, text, qtext):
        """ Check whether we have access to an article. """
        
        # Check white-list functions
        for wfun in self._access_whitelist:
            if wfun(text, qtext):
                return True

        # Check black-list functions
        for bfun in self._access_blacklist:
            if bfun(text, qtext):
                return False

        # If no hits, article is valid
        return True

    def get(self, cache, browser):
        """ Download document, then store in cache. """
        
        # Get document link
        link = self.get_link(cache, browser)
        if not link:
            raise NoAccessError('No access')
        if link:
            try:
                browser.open(link)
            except:
                raise NoAccessError('No access')
            cache.html, cache.qhtml = browser.get_docs()
        else:
            cache.html, cache.qhtml = cache.init_html, cache.init_qhtml
        
        # Run optional post-processing steps
        self.post_process(cache, browser)

        # Check access
        if not self.check_access(cache.html, cache.qhtml):
            raise NoAccessError('No access')

        # Validate result
        if not self.validate(cache.html):
            raise BadDocumentError('Bad document')
        
        return True
    
    @retry.retry(Exception)
    def reget(self, cache, browser):
        return self.get(cache, browser)

class MetaGetter(DocGetter):
    """ Base class for getters that use <meta> tags. """
    
    _attrs = []
    _filter = None

    def get_link(self, cache, browser):

        tags = cache.init_qhtml(utils.build_query(
            'meta',
            self._attrs
        ))

        if self._filter:
            tags = tags.filter(self._filter)

        content = tags.attr('content')
        if content:
            return content

        raise NotFoundError('Link not found')

class HTMLGetter(DocGetter):
    '''Base class for HTML getters.'''

    def validate(self, text):
        
        return not utils.ispdf(text)

class PDFGetter(DocGetter):
    
    def post_process(self, cache, browser):
        
        # Quit if valid PDF
        if self.validate(cache.html):
            return

        # Check for PDF in <iframe> tag
        iframe_links = cache.qhtml('frame, iframe').map(
            lambda: PyQuery(this).attr('src')
        )
        for link in iframe_links:
            if re.search(r'pdf', link):
                browser.open(link)
                cache.html, cache.qhtml = browser.get_docs()
                return

    def validate(self, text):
        
        return utils.ispdf(text)

class PMCGetter(HTMLGetter):

    _base_url = 'http://www.ncbi.nlm.nih.gov/pmc/articles/pmid'

    def get_link(self, cache, browser):
        return '%s/%s' % (self._base_url, cache.pmid)

    def validate(self, text):
        return not bool(re.search('ipmc11|ipmc12', text, re.I))

    @retry.retry(Exception, tries=3, backoff=1)
    def reget(self, cache, browser):
        return self.get(cache, browser)

class MetaHTMLGetter(MetaGetter, HTMLGetter):
    
    _attrs = [
        ['name', 'citation_fulltext_html_url'],
    ]

class MetaPDFGetter(MetaGetter, PDFGetter):
    
    _attrs = [
        ['name', 'citation_pdf_url'],
    ]

########
# PLOS #
########

class PassHTMLGetter(HTMLGetter):

    def get_link(self, cache, browser):
        return browser.geturl()

############
# Elsevier #
############

class ElsevierHTMLGetter(HTMLGetter):
    
    _access_blacklist = [
        ElsevierAccessRule(),
    ] + DocGetter._access_blacklist

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

    _access_blacklist = [
        RegexAccessRule(r'the function listed is not available with your '
                        r'current browser configuration')
    ]

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
        return qhtml('#pdfUrl').attr('value')
        #return qhtml('iframe#pdfIframe').attr('src')

##################
# Wolters-Kluwer #
##################

class WoltersKluwerGetter(DocGetter):

    _base_url = 'http://content.wkhealth.com/linkback/openurl'
    _params = ['issn', 'volume', 'issue', 'spage']

    def get_link(self, cache, browser):
        
        # Parse welcome URL
        url = browser.geturl()
        parsed_url = urlparse.urlparse(url)
        url_params = dict(urlparse.parse_qsl(parsed_url.query))

        if 'an' in url_params:
            lww_params = {
                'an': url_params['an']
            }
        elif all([param in url_params for param in self._params]):
            lww_params = {
                key: url_params[key]
                for key in self._params
            }
        else:
            raise NoAccessError('No access')

        return '{}?{}'.format(
            self._base_url,
            urllib.urlencode(lww_params)
        )

class WoltersKluwerHTMLGetter(WoltersKluwerGetter, MetaHTMLGetter):
    
    _attrs = [
        ['name', 'wkhealth_fulltext_html_url'],
    ]

    def get_link(self, cache, browser):

        # Get welcome link
        welcome_link = WoltersKluwerGetter.get_link(self, cache, browser)

        # Browse to welcome link
        browser.open(welcome_link)

        # Hack: Overwrite initial documents with LWW page
        cache.init_html, cache.init_qhtml = browser.get_docs()

        # Get full-text link
        return MetaHTMLGetter.get_link(self, cache, browser)

class WoltersKluwerPDFGetter(WoltersKluwerGetter, PDFGetter):

    def get_link(self, cache, browser):

        # Get welcome link
        welcome_link = WoltersKluwerGetter.get_link(self, cache, browser)

        # Browse to welcome link
        browser.open(welcome_link)
        _, qhtml = browser.get_docs()

        # Get PDF link
        link = qhtml('.ej-box-01-body-li-article-tools-pdf a')\
            .attr('href')
        if link:
            return link

        # Link not found
        raise NoAccessError('No access')

#############
# MIT Press #
#############

class MITHTMLGetter(HTMLGetter):
    
    def get_link(self, cache, browser):
        
        a = cache.init_qhtml('a.header4[href]').filter(
            lambda: re.search('/full/', PyQuery(this).attr('href'), re.I)
        )
        try:
            link = a.attr('href')
            if link is not None:
                return link
            raise
        except:
            raise NotFoundError('Link not found')

class MITPDFGetter(PDFGetter):
    
    def get_link(self, cache, browser):

        a = cache.init_qhtml('a.header4[href]').filter(
            lambda: re.search('/pdf(plus)?/', PyQuery(this).attr('href'), re.I)
        )
        try:
            link = PyQuery(a[-1]).attr('href')
            if link is not None:
                return link
            raise NotFoundError('Link not found')
        except:
            raise NotFoundError('Link not found')

#############################
# Thieme Medical Publishers #
#############################

class ThiemeHTMLGetter(MetaHTMLGetter):

    _access_blacklist = [
        ThiemeAccessRule(),
    ] + DocGetter._access_blacklist

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

class NatureGetter(DocGetter):

    _access_blacklist = [
        RegexAccessRule(r'To read this story in full you will need to login '
                        r'or make a payment')
    ]

class NPGPDFGetter(NatureGetter, PDFGetter):
    
    def get_link(self, cache, browser):

        link1 = cache.init_qhtml('li.download-pdf a[href$="pdf"]')\
            .attr('href')
        if link1:
            return link1

        link2 = cache.init_qhtml('a.download-pdf').attr('href')
        if link2:
            return link2

class NatureOldGetter(NatureGetter):

    def get_link(self, cache, browser):
        """Some old Nature articles (e.g. PMID 10862705) are routed through
        Nature's doifinder service; detect doifinder links and browse to real
        content.

        """
        doifinder_link = cache.init_qhtml('a.articletext').attr('href')
        if doifinder_link:
            browser.open(doifinder_link)

class NPGOldHTMLGetter(NatureOldGetter, HTMLGetter):

    def get_link(self, cache, browser):
        NatureOldGetter.get_link(self, cache, browser)
        return browser.geturl()

class NPGOldPDFGetter(NatureOldGetter, PDFGetter):

    def get_link(self, cache, browser):
        NatureOldGetter.get_link(self, cache, browser)
        html, qhtml = browser.get_docs()
        return qhtml('a[href$="pdf"]').attr('href')

########
# IEEE #
########

ieee_access_blacklist = [
    RegexAccessRule(r'Sign-In or Purchase')
]

class IEEEHTMLGetter(HTMLGetter):

    _access_blacklist = ieee_access_blacklist

    def get_link(self, cache, browser):
        return cache.init_qhtml('a#full-text-html')\
            .attr('href')

class IEEEPDFGetter(MetaPDFGetter):
    _access_blacklist = ieee_access_blacklist

############
# Springer #
############

class SpringerAccessRule(AccessRule):
    """ Custom black-list rule for Springer HTML documents. """
    def __call__(self, text, qtext):
        return not bool(qtext('.Fulltext'))

class SpringerHTMLGetter(MetaHTMLGetter):
    _access_blacklist = [
        SpringerAccessRule()
    ]

#########
# Wiley #
#########

class WileyAccessRule(AccessRule):
    """ Custom black-list rule for Wiley HTML documents. """
    def __call__(self, text, qtext):
        return not bool(qtext('div.section'))

class WileyHTMLGetter(MetaHTMLGetter):
    _access_blacklist = [
        WileyAccessRule()
    ]

###########
# Informa #
###########

class InformaGetter(DocGetter):

    _access_blacklist = [
        RegexAccessRule(r'you have requested the following article')
    ]

class InformaHTMLGetter(InformaGetter, HTMLGetter):

    def get_link(self, cache, browser):
        return cache.init_qhtml('a[href*="doi/full"]').attr('href')

class InformaPDFGetter(InformaGetter, PDFGetter):

    def get_link(self, cache, browser):
        pdf_plus = cache.init_qhtml('a[href*="doi/pdfplus"]').attr('href')
        if pdf_plus:
            return pdf_plus
        return cache.init_qhtml('a[href*="doi/pdf"]').attr('href')

#############
# IOS Press #
#############

class IOSGetter(DocGetter):
    _access_blacklist = [
        RegexAccessRule(r'log in to verify access')
    ]

class IOSHTMLGetter(IOSGetter, HTMLGetter):

    def get_link(self, cache, browser):
        return cache.init_qhtml('a[href$="fulltext.html"]').attr('href')

class IOSPDFGetter(IOSGetter, PDFGetter):

    def get_link(self, cache, browser):
        return cache.init_qhtml('a[href$="fulltext.pdf"]').attr('href')

#############
# Cambridge #
#############

class CambridgeHTMLGetter(HTMLGetter):

    _access_blacklist = [
        RegexAccessRule(r'buy this article')
    ]

    def get_link(self, cache, browser):
        link = cache.init_qhtml('a.typeHTML').attr('href')
        if link:
            return re.sub(r'\s', '', link)


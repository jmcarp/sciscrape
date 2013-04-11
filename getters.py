# Imports
import re
from pyquery import PyQuery

# Project imports
import utils

class DocGetter(object):
    '''Base class for document getters.'''
    
    def get_link(self, cache):
        
        pass

    def validate(self, cache):

        return True

    def check_access(self, text):
        
        #TODO
        return True

    def get(self, cache, browser):
        '''Get document.'''
        
        # Get document link
        link = self.get_link(cache, browser)

        # Open document link
        if link:
            browser.open(link)
            cache.html, cache.qhtml = browser.get_docs()
        else:
            cache.html, cache.qhtml = cache.init_html, cache.init_qhtml
        
        # Check access
        if not self.check_access(cache.html):
            print 'fail'
            return False

        # Validate result
        if not self.validate(cache.html):
            print 'fail'
            return False
        
        return True

class MetaGetter(DocGetter):
    
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

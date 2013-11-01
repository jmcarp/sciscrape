'''
Utilities for detecting the publisher of a given document. Users
will typically only use the pubdet() function. Other functions
and classes describe detection rules for specific publishers.
'''

# Imports
import re
from pyquery import PyQuery

# Project imports
from sciscrape.utils import utils

def pubdet(html):
    '''Detect publisher from HTML document.'''

    for detector in PubDetector.registry:
        if PubDetector.registry[detector].detect(html):
            return detector

class PubDetector(object):
    '''Detect publisher based on arbitrary function.'''
    
    # Initialize detector registry
    registry = {}

    def __init__(self, name, fun):
        '''Bind function to detect() method, then add self
        to registry.'''
        
        self.detect = fun
        PubDetector.registry[name] = self

class TitlePubDetector(PubDetector):
    '''Detect publisher based on <title> tag.'''
    
    def __init__(self, name, regex, flags=re.I):
        
        # Build detector function
        def fun(html):
            title = PyQuery(html).xhtml_to_html()('title')
            if title:
                return bool(re.search(regex, title.text(), flags))
            return False
        
        # Call super constructor
        super(TitlePubDetector, self).__init__(name, fun)

class MetaPubDetector(PubDetector):
    '''Detect publisher based on <meta> tags.'''
    
    def __init__(self, name, attrs, opers='='):
        
        # Build detector function
        def fun(html):
            return bool(PyQuery(html).xhtml_to_html()(utils.build_query(
                'meta', attrs, opers
            )))
        
        # Call super constructor
        super(MetaPubDetector, self).__init__(name, fun)

class RegexMetaPubDetector(PubDetector):
    
    _flags = re.I

    def __init__(self, name, attrs):
        
        def fun(html):

            q = PyQuery(html).xhtml_to_html()('meta')

            for pr in attrs:

                def flt():
                    for attrib in this.attrib:
                        if re.search(pr[0], attrib, self._flags) \
                                and re.search(pr[1], this.attrib[attrib], self._flags):
                            return True
                    return False

                q = q.filter(flt)

            return bool(q)

        super(RegexMetaPubDetector, self).__init__(name, fun)

def elsevier_detector(html):

    q = PyQuery(html).xhtml_to_html()
    canonical_href = q('link[rel="canonical"]').attr('href')
    if canonical_href:
        return re.search('sciencedirect', canonical_href, re.I)

PubDetector('elsevier', elsevier_detector)

# Define detectors based on <title> tag
TitlePubDetector('thieme', r'thieme e-journals')
TitlePubDetector('wolterskluwer', r'wolters kluwer')
TitlePubDetector('wiley', r'wiley online library')
TitlePubDetector('npg_old', r'nature citation')
TitlePubDetector('ios', r'ios press')

# Define detectors based on <meta> tags using regex
RegexMetaPubDetector('mit', [
    ['name', 'dc.publisher'],
    ['content', 'mit press'],
])
RegexMetaPubDetector('npg', [
    ['name', 'dc.publisher'],
    ['content', 'nature publishing group'],
])
RegexMetaPubDetector('informa', [
    ['name', 'dc.publisher'],
    ['content', 'informa'],
])

# Define detectors based on <meta> tags
MetaPubDetector('highwire', [
    ['name', 'HW.ad-path'],
])
MetaPubDetector('apa', [
    ['name', 'citation_publisher'],
    ['content', 'American Psychological Association'],
])
MetaPubDetector('cambridge', [
    ['name', 'citation_publisher'],
    ['content', 'Cambridge University Press'],
])
MetaPubDetector('springer', [
    ['name', 'citation_publisher'],
    ['content', 'Springer-Verlag'],
])
MetaPubDetector('springeropen', [
    ['name', 'citation_publisher'],
    ['content', 'Springer'],
])
MetaPubDetector('tandf', [
    ['property', 'og:site_name'],
    ['content', 'Taylor and Francis'],
])
MetaPubDetector('royal', [
    ['name', 'DC.Publisher'],
    ['content', 'The Royal Society'],
])
MetaPubDetector('ama', [
    ['name', 'citation_publisher'],
    ['content', 'American Medical Association'],
])
MetaPubDetector('plos', [
    ['name', 'citation_publisher'],
    ['content', 'Public Library of Science'],
])
MetaPubDetector('frontiers', [
    ['name', 'citation_publisher'],
    ['content', 'Frontiers'],
])
MetaPubDetector('nas', [
    ['name', 'citation_publisher'],
    ['content', 'National Acad Sciences'],
])
MetaPubDetector('bmc', [
    ['name', 'citation_publisher'],
    ['content', 'BioMed Central Ltd'],
])
MetaPubDetector('ieee', [
    ['name', 'citation_publisher'],
    ['content', 'IEEE'],
])

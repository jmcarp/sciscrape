# Imports
import re
import utils
from pyquery import PyQuery

def pubdet(html):
    '''Detect publisher from HTML document.'''

    publisher = None
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
            title = PyQuery(html)('title')
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
            return bool(PyQuery(html)(utils.build_query(
                'meta', attrs, opers
            )))
        
        # Call super constructor
        super(MetaPubDetector, self).__init__(name, fun)

# Define detectors based on <title> tag
TitlePubDetector('elsevier', 'sciencedirect')
TitlePubDetector('springer', 'springer')
TitlePubDetector('wolterskluwer', 'wolters kluwer')

# Define detectors based on <meta> tags
MetaPubDetector('highwire', [
        ['name', 'HW.identifier'],
    ]
)
MetaPubDetector('apa', [
        ['name', 'citation_publisher'],
        ['content', 'American Psychological Association'],
    ]
)
MetaPubDetector('tandf', [
        ['property', 'og:site_name'],
        ['content', 'Taylor and Francis'],
    ]
)
MetaPubDetector('thieme', [
        ['name', 'citation_publisher'],
        ['content', 'Thieme Medical Publishers'],
    ]
)
MetaPubDetector('royal', [
        ['name', 'DC.Publisher'],
        ['content', 'The Royal Society'],
    ]
)
MetaPubDetector('mit', [
        ['name', 'dc.Publisher'],
        ['content', 'MIT Press'],
    ],
    ['=', '^='],
)
MetaPubDetector('npg', [
        ['name', 'DC.publisher'],
        ['content', 'Nature Publishing Group'],
    ]
)
MetaPubDetector('ama', [
        ['name', 'citation_publisher'],
        ['content', 'American Medical Association'],
    ]
)
MetaPubDetector('plos', [
        ['name', 'citation_publisher'],
        ['content', 'Public Library of Science'],
    ]
)
MetaPubDetector('frontiers', [
        ['name', 'citation_publisher'],
        ['content', 'Frontiers'],
    ]
)
MetaPubDetector('nas', [
        ['name', 'citation_publisher'],
        ['content', 'National Acad Sciences'],
    ]
)
MetaPubDetector('bmc', [
        ['name', 'citation_publisher'],
        ['content', 'BioMed Central Ltd'],
    ]
)

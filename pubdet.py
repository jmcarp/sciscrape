# Imports
import re
import utils
from pyquery import PyQuery

def pubdet(html):
    publisher = None
    for detklass in PubDetector.__inheritors__:
        detobj = detklass()
        if detobj.detect(html):
            return detobj._name

class PubDetector(object):
    '''Base class for publisher detectors.'''

    class __metaclass__(type):

        __inheritors__ = []
        
        def __new__(meta, name, bases, dct):
            klass = type.__new__(meta, name, bases, dct)
            try:
                _name = klass()._name
                meta.__inheritors__.append(klass)
            except NotImplementedError:
                pass
            return klass 

    @property
    def _name(self):
        raise NotImplementedError('Subclasses must define _name')

    def detect(self, html):
        raise NotImplementedError('Subclasses must implement detect()')
    
class ElsevierDetector(PubDetector):
    
    _name = 'elsevier'

    def detect(self, html):
        
        title = PyQuery(html)('title')
        if title:
            return bool(re.search('sciencedirect', title.text(), re.I))
        return False

class Springer(PubDetector):
    
    _name = 'springer'

    def detect(self, html):
        
        title = PyQuery(html)('title')
        if title:
            return bool(re.search('springer', title.text(), re.I))
        return False

#####################################
# PubDetectors based on <meta> tags #
#####################################

class MetaPubDetector(PubDetector):
    '''Base class for <meta> tag detectors.'''
    
    _ops = '='

    def detect(self, html):
        return bool(PyQuery(html)(utils.build_query(
            'meta', self._attrs, self._ops
        )))

class HighwireDetector(MetaPubDetector):
    
    _name = 'highwire'
    _attrs = [
        ['name', 'HW.identifier'],
    ]

class TaylorFrancisDetector(MetaPubDetector):
    
    _name = 'tandf'
    _attrs = [
        ['property', 'og:site_name'],
        ['content', 'Taylor and Francis'],
    ]

class ThiemeDetector(MetaPubDetector):
    
    _name = 'thieme'
    _attrs = [
        ['name', 'citation_publisher'],
        ['content', 'Thieme Medical Publishers'],
    ]

class BMCDetector(MetaPubDetector):
    
    _name = 'bmc'
    _attrs = [
        ['name', 'citation_publisher'],
        ['content', 'BioMed Central Ltd'],
    ]

class NASDetector(MetaPubDetector):
    
    _name = 'nas'
    _attrs = [
        ['name', 'citation_publisher'],
        ['content', 'National Acad Sciences'],
    ]

class PLOSDetector(MetaPubDetector):
    
    _name = 'plos'
    _attrs = [
        ['name', 'citation_publisher'],
        ['content', 'Public Library of Science'],
    ]

class FrontiersDetector(MetaPubDetector):
    
    _name = 'frontiers'
    _attrs = [
        ['name', 'citation_publisher'],
        ['content', 'Frontiers'],
    ]

class AMADetector(MetaPubDetector):
    
    _name = 'ama'
    _attrs = [
        ['name', 'citation_publisher'],
        ['content', 'American Medical Association'],
    ]

class NatureDetector(MetaPubDetector):
    
    _name = 'npg'
    _attrs = [
        ['name', 'DC.publisher'],
        ['content', 'Nature Publishing Group'],
    ]

class MITDetector(MetaPubDetector):
    
    _name = 'mit'
    _attrs = [
        ['name', 'dc.Publisher'],
        ['content', 'MIT Press'],
    ]
    _ops = ['=', '^=']

class RoyalSocietyDetector(MetaPubDetector):
    
    _name = 'royal'
    _attrs = [
        ['name', 'DC.Publisher'],
        ['content', 'The Royal Society'],
    ]


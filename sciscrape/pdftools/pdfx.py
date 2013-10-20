# -*- coding: utf-8 -*-

# Imports
import re
import requests
from pyquery import PyQuery

# Sciscrape imports
from sciscrape.utils import retry

class PDFExtractor(object):
    '''Base class for extracting information from
    PDFs using PDFx.

    '''
    
    #TODO: Figure out which exception(s) this may throw
    @retry.retry(Exception)
    def extract(self, pdf):
        '''Get XML representation of PDF. For details, see 
        http://pdfx.cs.man.ac.uk/usage

        Args:
            pdf (str / file) : PDF data
        Returns:
            Parsed XML from PDFX

        Example:
            >>> pdf = open('doc.pdf', 'rb').read()
            >>> qxml = PDFExtractor().extract(pdf)

        '''
        
        # Send request to PDFX
        req = requests.post(
            'http://pdfx.cs.man.ac.uk', 
            headers={'content-type' : 'application/pdf'},
            data=pdf,
        )

        # Remove encoding
        # Note: PyQuery / LXML will fail if 
        # encodings present
        xml_raw = req.text
        xml_clean = re.sub('encoding=\'.*?\'', '', xml_raw)

        # Parse XML
        qxml = PyQuery(xml_clean)
        
        # Quit if <error>
        if qxml[0].tag == 'error':
            return

        # Return parsed XML
        return qxml

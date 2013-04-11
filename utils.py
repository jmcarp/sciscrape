# Imports
import re
import pyPdf
import tempfile

def build_query(tag, attrs, operators='='):
    '''Build PyQuery-style query.

    Args:
        tag (str) : tag name
        attrs (list) : list of key, value lists
        operators (list) : list of operator strings
    Returns:
        query
    
    > build_query('meta', [['name', 'citation_author]], ['^='])
    'meta[name^="citation_author"]'

    '''
    
    # Initialize query
    query = tag

    # Add attributes
    for idx, attr in enumerate(attrs):
        operator = operators[idx % len(operators)]
        val = ''
        if len(attr) > 1:
            val = '{0}"{1}"'.format(operator, attr[1])
        query += '[{0}{1}]'.format(attr[0], val)
        #query += '[{0}{1}"{2}"]'.format(attr[0], operator, attr[1])

    # Return final query
    return query

def ispdf(text):
    '''Check whether document is a PDF.'''
    
    # Write text to temporary file
    tmp = tempfile.TemporaryFile()
    tmp.write(text)

    # Check PDF using pyPdf
    try:
        _ = pyPdf.PdfFileReader(tmp)
        return True
    except:
        pass

    # Check PDF using header
    if re.search('^%pdf', text, re.I):
        return True

    # Not a PDF
    return False

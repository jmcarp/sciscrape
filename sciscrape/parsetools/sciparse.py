'''

'''


# Imports
import re
import pandas as pd
from pyquery import PyQuery

# Project imports
from sciscrape.pdftools import pdfx

# Utility functions

def isfloat(s):
    '''Check whether string can be converted to a float.'''

    try:
        f = float(s)
        return True
    except ValueError:
        return False

def get_coord_groups(headers):
    '''Get contiguous, ordered groups of x, y, z columns from headers.'''
    
    # Initialize coordinate groups
    coord_groups = []
    
    # Loop over headers
    for idx in range(len(headers) - 2):
        if headers[idx:idx+3] == ['x', 'y', 'z']:
            coord_groups.append(range(idx, idx + 3))

    # Return coordinate groups
    return coord_groups

class SciParse(object):
    
    pass

class PDFParse(SciParse):

    pass

class Table(object):

    def __init__(self, data_table):
        
        # Initialize coords
        self.coords = []

        if not data_table:
            return

        # Store original data
        self._header = data_table['headers']
        self._data = data_table['data']

        # Store DataFrame
        try:
            self._ext = pd.DataFrame(self._data, columns=self._header)
        except Exception as e:
            print e.message
            self._ext = None
        
        # Get coordinate groups
        self._coord_groups = get_coord_groups(self._header)

        # Extract coordinates
        for row in self._data:
            for coord_group in self._coord_groups:
                self.add_coord(*[row[coord] for coord in coord_group])

    def __eq__(self, other):

        for coord in self.coords:
            if coord not in other.coords:
                return False

        for coord in other.coords:
            if coord not in self.coords:
                return False

        return True

    def add_coord(self, x, y, z):

        coord = Coord(x, y, z)
        if coord.validate():
            self.coords.append(coord)

class Coord(object):

    def __init__(self, x, y, z):

        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):

        return self.x == other.x and \
               self.y == other.y and \
               self.z == other.z

    def validate(self):

        # Check for non-numeric values
        try:
            self.x = float(self.x)
            self.y = float(self.y)
            self.z = float(self.z)
        except ValueError:
            return False

        # Valid
        return True

    def __repr__(self):

        return 'Coord(%r, %r, %r)' % \
            (self.x, self.y, self.z)

class PDFTableParse(PDFParse):
    
    # Translation table
    _trans = [ 
        [u'[\x80-\xff]+', '-'],
    ]   
    
    @staticmethod
    def _get_text():
        return PyQuery(this).text()

    def parse(self, pdf):
        
        # PDF -> XML
        qpdf = pdfx.PDFExtractor().extract(pdf)

        # Get XML tables
        xml_tables = qpdf('table')
        xml_tables = self._consolidate_tables(xml_tables)
        
        # XML tables -> Data tables
        data_tables = []
        for xml_table in xml_tables:
            data_table = self._parse_table(xml_table)
            if data_table:
                data_tables.append(data_table)
        
        # Data tables -> Coord tables
        coord_tables = []
        for data_table in data_tables:
            # Skip non-MRI tables
            if not self._is_mri_table(data_table):
                continue
            # Apply post-processing functions
            self._clean_headers(data_table)
            self._split_cols(data_table)
            self._sort_cols(data_table)
            self._to_float(data_table)
            
            #print data_table
            coord_table = Table(data_table)
            coord_tables.append(coord_table)

        # Return coordinate tables
        return coord_tables

    def _parse_table(self, table):

        # Initialize table
        parsed_rows = []
        
        # Parse table
        qtable = PyQuery(table)

        # Get headers
        headers = self._get_headers(qtable)
        if not headers:
            return

        # Get rows
        rows = qtable.find('tr')

        # Loop over rows
        for row in rows:

            # Get columns
            qrow = PyQuery(row)
            cols = qrow.find('td').map(self._get_text)[:]

            # Parse column values
            for colidx in range(len(cols)):
                col = reduce(
                    lambda x, y: re.sub(y[0], y[1], x),
                    self._trans,
                    cols[colidx]
                )
                cols[colidx] = col

            # Append parsed columns
            if cols:
                parsed_rows.append(cols)

        return {
            'headers' : headers,
            'data' : parsed_rows,
        }

    def _consolidate_tables(self, qtables):
        '''When tables are split across pages, PDFX assigns them the same
        "number" attribute. This method identifies unique table groups by number,
        then groups all tables by number.'''

        # Get table numbers
        numbers = [PyQuery(t).attr('number') for t in qtables]
        numbers = map(int, numbers)

        # Initialize consolidated tables
        ctables = []

        # Loop over unique table numbers
        for number in sorted(set(numbers)):
            ntables = [PyQuery(qtables[t]) for t in range(len(numbers)) if
                           numbers[t] == number]
            ctable = reduce(lambda x, y: x + y, ntables)
            ctables.append(ctable)

        # Return consolidated tables
        return ctables
    
    # Max number of <thead> / <tr> tags to check
    # for headers
    _max_header_tries = 5

    def _get_headers(self, xml_table):
        '''Extract headers from table. Headers may be stored in the
        <thead> element, or in one or more <tr> elements, or in an
        <h1 class="table"> element preceding the table. This method checks
        all of the above until it finds a valid table header (verified
        using the _is_mri_header() method).'''
        
        # Parse table
        qtable = PyQuery(xml_table)

        # Get headers from <thead> / <tr> tags
        
        # Get <thead> / <tr> tags
        trs = qtable.find('thead,tr')

        # Check up to _max_header_tries or the number of
        # <thead> / <tr> tags, whichever is least
        ntry = min(trs.length, self._max_header_tries)
        
        # Loop over rows in reverse order
        # Deals with empty / incomplete headers at the
        # top of the table
        for tryidx in range(ntry, 0, -1):
            
            # Extract text from <th> / <td> children
            headers = PyQuery(trs[tryidx])('th,td')\
                .map(self._get_text)[:]
            #headers = [h.lower() for h in headers]
            
            # Done if current value is a valid header
            if self._is_mri_header(headers):
                return headers

        # Get headers from <h1 class="table"> tags
        h1_table = qtable.prev('h1.table').text()
        if h1_table:
            headers = re.split('\s+', h1_table)
            #headers = [h.lower() for h in headers]
            # Done if current value is a valid header
            if self._is_mri_header(headers):
                return headers
        
        # No headers found
        return []

    def _clean_headers(self, data_table):
        '''Clean up headers.'''
        
        for hidx, header in enumerate(data_table['headers']):

            # Remove parenthetical values
            header = re.sub('\(.*?\)', '', header)

            # Remove commas
            header = re.sub('[,]', '', header)

            # To lower-case
            header = header.lower()

            # Remove leading / trailing whitespace
            header = header.strip()

            # Done
            data_table['headers'][hidx] = header
    
    class CellSplitter(object):

        def __init__(self, fun, subcells):
            self.fun = fun
            self.subcells = subcells

        def test(self, text):
            return self.fun(text)

    _coord_splitters = [
        CellSplitter(
            lambda c: re.search('coordinate|talairach|mni', c, re.I),
            ['x', 'y', 'z']
        ),
        CellSplitter(
            lambda c: re.search('x.*?y.*?z', c, re.I),
            ['x', 'y', 'z']
        ),
        CellSplitter(
            lambda c: re.search('x.*?y', c, re.I) and
                not re.search('z', c, re.I),
            ['x', 'y']
        ),
        CellSplitter(
            lambda c: re.search('y.*?z', c, re.I) and
                not re.search('x', c, re.I),
            ['y', 'z']
        ),
    ]

    def _split_cols(self, data_table):
        '''Split multi-value columns (MNI Coordinates; x,y,z, ...)'''

        # Identify columns to be split
        splits = []
        for idx, val in enumerate(data_table['headers']):
            for splitter in self._coord_splitters:
                if splitter.test(val):
                    splits.append([idx, splitter])
                    break
    
        # Split columns
        # Note: Apply splits in reverse order to avoid
        # messing up earlier columns
        for split in splits[::-1]:
            cidx = split[0]
            data_table['headers'][cidx:cidx+1] = split[1].subcells
            for ridx, row in enumerate(data_table['data']):
                # Split coordinates
                val_split = re.split('[\s,;:]+', row[cidx])
                # Pad values with empty strings
                val_split += [''] * (len(split[1].subcells) - len(val_split))
                # Update row
                row[cidx:cidx+1] = val_split
                # Update table
                data_table['data'][ridx] = row

    def _sort_cols(self, data_table):
        '''In some tables, X and Y coordinates, Y and Z coordinates,
        etc., may be inappropriately stuck together, e.g. X = '20, 8', 
        Y = '', Z = '-2'. This method tries to reassign coordinate
        values to the appropriate headers, e.g. X = '20', Y = '8', 
        Z = '-2'.
        
        '''

        # Get coordinate groups
        coord_groups = get_coord_groups(data_table['headers'])

        # Loop over rows
        for ridx, row in enumerate(data_table['data']):
            for coord_group in coord_groups:
                # Get coordinate values
                vals = [row[coord] for coord in coord_group]
                # Join values by space
                val_str = ' '.join(vals)
                # Split value string by space / comma
                val_split = re.split('[\s,]+', val_str)
                # If we get three values back, reassign
                # to X, Y, Z headers
                if len(val_split) == 3:
                    for cidx, coord in enumerate(coord_group):
                        row[coord] = val_split[cidx]
                    # Replace original row
                    data_table['data'][ridx] = row

    _rep_chars = '[\*,]'

    def _to_float(self, data_table):
        '''Convert cell values to float.'''

        for ridx, row in enumerate(data_table['data']):
            for cidx, col in enumerate(row):
                col = re.sub(self._rep_chars, '', col)
                try:
                    col = float(col)
                    row[cidx] = col
                except ValueError:
                    pass
            data_table['data'][ridx] = row

    # Header patterns indicating fMRI activation table
    _mri_header_patterns = [
        '^x$', '^y$', '^z$',
        '^ba$', '^lobe$', '^region$',
        'coordinates',
    ]
    
    def _is_mri_header(self, headers):
        
        # Loop over table columns
        for column in headers:
            # Loop over regex patterns
            for pattern in self._mri_header_patterns:
                if re.search(pattern, column, re.I):
                    return True
        return False

    def _is_mri_table(self, data_table):
        '''Check whether a given table is an fMRI activation table.

        Args:
            data_table (DataFrame) : data table
        Returns:
            True | False

        '''
        
        return self._is_mri_header(data_table['headers'])


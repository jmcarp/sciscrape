'''
Functions for comparing tables extracted from PDFs and hand-coded
tables. The main function most users will call is test().
'''

# Imports
import os
import glob
import operator
import pandas as pd

# Project imports
from sciscrape.scrapetools import scrape
from sciscrape.parsetools import sciparse
from sciscrape.tests import populate
from sciscrape import tests

def read_tables_csv(csv_name):
    '''Read Table objects from a CSV file.

    Args:
        csv_name (str): Path to CSV file
    Returns:
        List of Table instances

    '''
    
    csv_tables = []
    table = sciparse.Table(None)
    csv_lines = open(csv_name).read().split('\r')

    for csv_line in csv_lines:
        csv_line = csv_line.strip()
        if csv_line != ',,':
            line_split = csv_line.split(',')
            table.add_coord(*line_split)
        else:
            csv_tables.append(table)
            table = sciparse.Table(None)
    if len(table.coords):
        csv_tables.append(table)

    return csv_tables

def compare_table_groups(tref, tcmp):
    '''Compare two Table instances, computing true positives, false
    positives, and false negatives.

    Args:
        tref (Table): Reference table
        tcmp (Table): Comparison table
    Returns:
        Dictionary containing proportions of true positives, false
            positives, and false negatives
    
    '''
    
    tref_coords = reduce(operator.add, [t.coords for t in tref], [])
    tcmp_coords = reduce(operator.add, [t.coords for t in tcmp], [])

    tref_coords = list(set(tref_coords))
    tcmp_coords = list(set(tcmp_coords))
    
    n_coords = float(len(tref_coords))

    tp = len([t for t in tref_coords if t in tcmp_coords]) / n_coords
    fp = len([t for t in tcmp_coords if t not in tref_coords]) / n_coords
    fn = len([t for t in tref_coords if t not in tcmp_coords]) / n_coords

    return {
        'tp' : tp,
        'fp' : fp,
        'fn' : fn,
    }

def test(journal, scrape_klass=scrape.Scrape):
    '''Compare tables extracted from PDFs with hand-coded tables
    for all available article for a journal.

    Args:
        journal (str): Journal name
        scrape_klass (Scrape): Type of scraper to use
    Returns:
        pandas.DataFrame containing performance for each article
    
    '''
    
    # Initialize results
    cmps = []

    # Make sure PDFs have been downloaded
    populate.populate(journal, scrape_klass)

    # Get all CSV files
    csv_files = glob.glob('%s/csv/%s/*.csv' % (tests.data_dir, journal))
    
    for csv_file in csv_files:

        print 'Working on file %s...' % (csv_file)

        base_file = os.path.split(csv_file)[1]\
            .split('.csv')[0]

        pdf_file = csv_file\
            .replace('/csv/', '/doc/')\
            .replace('.csv', '.pdf')

        # Extract tables from PDF
        with open(pdf_file, 'rb') as pdf:
            pdf_tables = sciparse.PDFTableParse().parse(pdf)
        
        # Extract tables from CSV
        csv_tables = read_tables_csv(csv_file)
        
        cmp = compare_table_groups(csv_tables, pdf_tables)
        cmp['id'] = base_file
        cmp['jn'] = journal
        cmps.append(cmp)
    
    # Return results as DataFrame
    return pd.DataFrame(cmps)

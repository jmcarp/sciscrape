'''
Various tests require full-text articles to run, but articles
can't be packed with the sciscrape code for legal reasons. This code
attempts to download the relevant full-text articles from the
publishers.
'''

# Imports 
import os
import glob

# Project imports
from sciscrape.scrapetools import scrape
from sciscrape.scrapetools import searchscrape
from sciscrape import tests

def populate(journal, scrape_klass=scrape.Scrape):
    '''Attempt to download a batch of papers for which
    hand-coded activation data are available in tests/data/csv.
    
    Arguments:
        journal : journal name (must be a directory in 
                  tests/data/csv)
        scrape_klass : (sub-) class of scraper.Scrape to use

    '''
    
    # Get all CSV files
    csv_files = glob.glob('%s/csv/%s/*.csv' % (tests.data_dir, journal))
    
    # Get files to be downloaded
    todo_files = []
    for csv_file in csv_files:
        pdf_file = csv_file\
            .replace('/csv/', '/doc/')\
            .replace('.csv', '.pdf')
        if not os.path.exists(pdf_file):
            todo_files.append(csv_file)
    
    # Quit if no files to download
    if not todo_files:
        return

    # Get scraper
    scraper = scrape_klass()

    for todo_file in todo_files:

        doi = os.path.split(todo_file)[1]\
            .split('.csv')[0]\
            .replace('__', '/')
        
        info = scraper.scrape(doi=doi)
        info.save('%s/doc/%s' % (tests.data_dir, journal))

'''
Miscellaneous examples of sciscrape usage.
'''

# Project imports
from sciscrape.scrapetools import scrape
from sciscrape.scrapetools import searchscrape
from sciscrape.parsetools import sciparse

def example_full_stream(doi='10.1162/jocn.2009.21274', 
                        scrape_klass=scrape.Scrape,
                        out_dir=None):
    '''Process an article, from start (DOI) to finish (parsed tables).

    Args:
        doi : Article DOI
        scrape_klass : (Sub-) class of scrape.Scrape
        out_dir : Directory to save scraped documents

    '''
    
    # Instantiate Scrape (sub-) class
    scraper = scrape_klass()
    
    # Call scrape() on article DOI
    scrape_info = scraper.scrape(doi=doi)

    # Save documents to output directory
    if out_dir:
        scrape_info.save(out_dir)
    
    if 'pdf' in scrape_info.docs:

        # Parse PDF
        parser = sciparse.PDFTableParse()
        tables = parser.parse(scrape_info.docs['pdf'])

        # Return parsed tables
        return tables

def example_scrape_jep():
    '''Search PubMed for fMRI studies published
    in Neuroimage, download article documents,
    and save results to current working directory.'''
    
    searchscrape.searchscrape(
        'fmri AND "journal of experimental psychology. human perception and performance"[journal]',
        '.',
        scrape_klass = scrape.UMScrape,
        retmax=5
    )

def example_scrape_nimg():
    '''Search PubMed for fMRI studies published
    in Neuroimage, download article documents,
    and save results to current working directory.'''
    
    searchscrape.searchscrape(
        'fmri AND neuroimage[journal]',
        '.',
        scrape_klass = scrape.UMScrape,
        retmax=5
    )

def example_scrape_nrep():
    '''Search PubMed for fMRI studies published
    in Neuroimage, download article documents,
    and save results to current working directory.'''
    
    searchscrape.searchscrape(
        'fmri AND neuroreport[journal]',
        '.',
        scrape_klass = scrape.UMScrape,
        retmax=5
    )

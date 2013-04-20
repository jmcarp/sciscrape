# Project imports
from sciscrape.scrapetools import scrape
from sciscrape.scrapetools import searchscrape

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

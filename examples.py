# Project imports
import sciscrape
import searchscrape

def example_scrape_nimg():
    '''Search PubMed for fMRI studies published
    in Neuroimage, download article documents,
    and save results to current working directory.'''
    
    searchscrape.searchscrape(
        'fmri AND neuroimage[journal]',
        '.',
        scrape_klass = sciscrape.UMSciScrape,
        retmax=5
    )

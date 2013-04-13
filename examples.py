# Project imports
import sciscrape
import searchscrape

def example_scrape_jep():
    '''Search PubMed for fMRI studies published
    in Neuroimage, download article documents,
    and save results to current working directory.'''
    
    searchscrape.searchscrape(
        'fmri AND "journal of experimental psychology. human perception and performance"[journal]',
        '.',
        scrape_klass = sciscrape.UMSciScrape,
        retmax=5
    )
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

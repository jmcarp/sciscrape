'''
Utilities for running article searches and downloading the
resulting documents.
'''

# Project imports
from sciscrape.utils import utils
from sciscrape.utils import pubtools
from sciscrape.scrapetools import scrape

def searchscrape(query, out_dir, scrape_klass=scrape.Scrape, **kwargs):
    '''Run PubMed query, then download articles.

    Args:
        query (str) : PubMed search query
        out_dir (str) : Output directory for documents
        scrape_klass (Scrape) : Scraper type
        kwargs: Optional arguments for PubMed search
    Returns:
        None
    
    Examples:
        >>> searchscrape('fmri AND neuroimage[journal]', '.', retmax=5)

    '''
    
    # Create directory if needed
    utils.mkdir_p(out_dir)

    # Find articles on PubMed
    searcher = pubtools.PubMedSearcher()
    pmids = searcher.search(query, **kwargs)
    
    # Initialize scraper
    scraper = scrape_klass()

    # Loop over articles
    for pmid in pmids:
        
        print 'Working on article %s...' % (pmid)
        
        # Scrape article documents
        info = scraper.scrape(pmid=pmid)

        # Write documents to files
        for doc_type in info.docs:
            out_name = '%s/%s.%s' % (out_dir, pmid, doc_type)
            with open(out_name, 'w') as f:
                f.write(info.docs[doc_type])

# Imports
import os

# Project imports
import pubtools
import sciscrape

def searchscrape(query, out_dir, scrape_klass=sciscrape.SciScrape, **kwargs):
    '''Run PubMed query, then download articles.

    Args:
        query (str) : PubMed search query
        out_dir (str) : Output directory for documents
        scrape_klass (SciScrape) : Scraper type
        kwargs: Optional arguments for PubMed search
    Returns:
        None
    
    Examples:
        >>> searchscrape('fmri AND neuroimage[journal]', '.', retmax=5)

    '''
    
    # Create directory if needed
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

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


class ScrapeFixture(object):

    def __init__(self, publisher, pmid, start_url, html_url=None, pdf_url=None, pmc_url=None, params=None):

        self.publisher = publisher
        self.pmid = pmid
        self.start_url = start_url
        self.expected_urls = {
            'html': html_url,
            'pdf': pdf_url,
            'pmc': pmc_url,
        }
        self.params = params or {}

fixtures = [
    ScrapeFixture('plos', '22216274',
                  'http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0029411',
                  html_url='http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0029411',
                  pdf_url='http://www.plosone.org/article/fetchObject.action?uri=info%3Adoi%2F10.1371%2Fjournal.pone.0029411&representation=PDF',
                  pmc_url='http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3245287/'),
    ScrapeFixture('frontiers', '21212836',
                  'http://journal.frontiersin.org/Journal/10.3389/fnhum.2010.00231/full',
                  html_url='http://journal.frontiersin.org/Journal/10.3389/fnhum.2010.00231/full',
                  pdf_url='http://journal.frontiersin.org/Journal/10.3389/fnhum.2010.00231/pdf',
                  pmc_url='http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3014651/'),
    # Flagship Nature journal style (Nature, Nature Neuroscience, etc.)
    ScrapeFixture('npg', '23396282',
                  'http://www.nature.com/nmeth/journal/v10/n3/full/nmeth.2365.html',
                  html_url='http://www.nature.com/nmeth/journal/v10/n3/full/nmeth.2365.html',
                  pdf_url='http://www.nature.com/nmeth/journal/v10/n3/pdf/nmeth.2365.pdf',
                  ),
    # Secondary Nature journal style (Neuropsychopharmacology, Oncogene, etc.)
    ScrapeFixture('npg', '22907434',
                  'http://www.nature.com/onc/journal/v32/n28/full/onc2012359a.html',
                  html_url='http://www.nature.com/onc/journal/v32/n28/full/onc2012359a.html',
                  pdf_url='http://www.nature.com/onc/journal/v32/n28/pdf/onc2012359a.pdf',
                  ),
    ScrapeFixture('mit', '19929323',
                  'http://www.mitpressjournals.org/doi/abs/10.1162/jocn.2009.21407?url_ver=Z39.88-2003&rfr_id=ori:rid:crossref.org&rfr_dat=cr_pub%3dpubmed',
                  html_url='http://www.mitpressjournals.org/doi/full/10.1162/jocn.2009.21407',
                  pdf_url='http://www.mitpressjournals.org/doi/pdfplus/10.1162/jocn.2009.21407',
                  pmc_url='http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2895005/'),
    ScrapeFixture('wiley', '20210877',
                  'http://onlinelibrary.wiley.com/doi/10.1111/j.1469-8986.2009.00970.x/abstract',
                  html_url='http://onlinelibrary.wiley.com/doi/10.1111/j.1469-8986.2009.00970.x/full',
                  pdf_url='http://onlinelibrary.wiley.com/store/10.1111/j.1469-8986.2009.00970.x/asset/j.1469-8986.2009.00970.x.pdf',
                  pmc_url='http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2904495/'),
    ScrapeFixture('highwire', '21263035',
                  'http://cercor.oxfordjournals.org/content/21/9/2056.long',
                  html_url='http://cercor.oxfordjournals.org/content/21/9/2056.full',
                  pdf_url='http://cercor.oxfordjournals.org/content/21/9/2056.full.pdf',
                  pmc_url='http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3155602/'),
    ScrapeFixture('elsevier', '22776460',
                  'http://www.sciencedirect.com/science/article/pii/S1053811912006702',
                  html_url='http://www.sciencedirect.com/science/article/pii/S1053811912006702',
                  pdf_url='http://ac.els-cdn.com/S1053811912006702/1-s2.0-S1053811912006702-main.pdf',
                  pmc_url='http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3459097/'),
    ScrapeFixture('springer', '21671045',
                  'http://link.springer.com/article/10.3758%2Fs13415-011-0047-9',
                  html_url='http://link.springer.com/article/10.3758/s13415-011-0047-9/fulltext.html',
                  pdf_url='http://download.springer.com/static/pdf/120/art%253A10.3758%252Fs13415-011-0047-9.pdf',
                  pmc_url='http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3651895/',
                  ),
    ScrapeFixture('thieme', '23943717',
                  'https://www.thieme-connect.com/DOI/DOI?10.1055/s-0033-1346973',
                  html_url='https://www.thieme-connect.com/products/ejournals/html/10.1055/s-0033-1346973',
                  pdf_url='https://www.thieme-connect.com/products/ejournals/pdf/10.1055/s-0033-1346973.pdf',
                  pmc_url='http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3713555/',
                  ),
    ScrapeFixture('wolterskluwer', '24999907',
                  'http://pt.wkhealth.com/pt/re/lwwgateway/landingpage.htm;jsessionid=TsJhhmvGJLD8L3SFtpYYH1CpylynfhXhWy9CMQh2NtLwQJh1QCSY!-773986214!181195628!8091!-1?issn=0959-4965&volume=25&issue=13&spage=1038',
                  html_url='http://journals.lww.com/neuroreport/Fulltext/2014/09100/Low_attentional_engagement_makes_attention_network.11.aspx',
                  pdf_url='http://pdfs.journals.lww.com/neuroreport/2014/09100/Low_attentional_engagement_makes_attention_network.11.pdf?token=method|ExpireAbsolute;source|Journals;ttl|1408030295442;payload|mY8D3u1TCCsNvP5E421JYPPlNl9ZUXrQDsjmMHeXqBgfxP56d5BAis+WhfSrPR1S6lcHrAT5WTvTkrI7Jc1zUq2UlEn8N1x7qr2heZXbSZE2/LnQkUnbAwLtuHlqxiruZhFwwtFf4aeU4rMgwns+8TDbNbAkOUlffcIt0OqswFvWf97qU1+XR+GRM7R1S2drJjlMZyk5umnCyX0ZsO+WQO3OqrC6kWZHGFmwsUyPoy3TkarWdvvy6Y+Y2j71uz08ZT48Kq4FnoD9k2sZ/f2+VtLuq7uoIKDiRliJeppVX+rw4UyT+wiUZhSlAJO7dAyjR9vmyVAWVtaC6WwAPrLYreszSV1KWThE7hh6oMJQ6lmjEbXKC+gaal/PsKlfuCcwBrUqJIORKZEJNXxZBdgr3PQsdpBR5D41VaEH2MOCVFQOReXo4fsg/YHzlI735ThKGKWml7j5Rn+50uie6sSdJqjf0QLWOa0q+IPzv3lP9DbtjtVBzj37I05+xyFEQYy8hkPvrHfu33uPvCYtoLj6J9uZawa0r/hG4jNiOlz9FC7GJdeYruj0bK5VQBSvsgdY/dBIMeG3lNTXUCUcvJSluK0aGIw6Dz6nHkcE/3S4anFLYlT+riIYTCGiEX23hvUO;hash|I3xhAQ8hS8bsB8TQtfSTgw==',
                  ),
    ScrapeFixture('ieee', '10.1109/JTEHM.2013.2262024',
                  'http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=6527311',
                  html_url='http://ieeexplore.ieee.org/xpls/icp.jsp?arnumber=6527311',
                  pdf_url='http://ieeexplore.ieee.org/ielx7/6221039/6336546/06527311.pdf?tp=&arnumber=6527311&isnumber=6336546',
                  ),
    ScrapeFixture('informa', '20954892',
                  'http://informahealthcare.com/doi/abs/10.3109/08990220.2010.513111',
                  html_url='http://informahealthcare.com/doi/full/10.3109/08990220.2010.513111',
                  pdf_url='http://informahealthcare.com/doi/pdfplus/10.3109/08990220.2010.513111',
                  ),
    ScrapeFixture('cambridge', '23985326',
                  'http://journals.cambridge.org/action/displayAbstract?fromPage=online&aid=9040968',
                  html_url='http://journals.cambridge.org/action/displayFulltext?type=6&fid=9040969&jid=PAR&volumeId=140&issueId=13&aid=9040968&%20bodyId=&membershipNumber=&societyETOCSession=%20&fulltextType=RA&fileId=S0031182013001182',
                  pdf_url='http://journals.cambridge.org/download.php?file=%2FPAR%2FPAR140_13%2FS0031182013001182a.pdf&code=8f00ba1654e95f8adb323feb4fadd1e3',
                  pmc_url='http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3806042/',
                  params=['file'],
                  ),
    ScrapeFixture('jstage', '23474956',
                  'https://www.jstage.jst.go.jp/article/mrms/12/1/12_2011-0006/_article',
                  pdf_url='https://www.jstage.jst.go.jp/article/mrms/12/1/12_2011-0006/_pdf',
                  ),
    ScrapeFixture('apa_psychiatry', '12668352',
                  'http://ajp.psychiatryonline.org/article.aspx?articleid=176149',
                  html_url='http://ajp.psychiatryonline.org/article.aspx?articleid=176149',
                  pdf_url='http://ajp.psychiatryonline.org/data/Journals/AJP/3747/667.pdf',
                  ),
    ScrapeFixture('maney', '22196856',
                  'http://www.maneyonline.com/doi/abs/10.1179/1743132811Y.0000000049',
                  html_url='http://www.maneyonline.com/doi/full/10.1179/1743132811Y.0000000049',
                  pdf_url='http://www.maneyonline.com/doi/pdfplus/10.1179/1743132811Y.0000000049',
    ),
]

class ScrapeFixture(object):

    def __init__(self, publisher, pmid, start_url, html_url=None, pdf_url=None, pmc_url=None):

        self.publisher = publisher
        self.pmid = pmid
        self.start_url = start_url
        self.expected_urls = {
            'html': html_url,
            'pdf': pdf_url,
            'pmc': pmc_url,
        }

fixtures = [
    ScrapeFixture('plos', '22216274',
                  'http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0029411',
                  html_url='http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0029411',
                  pdf_url='http://www.plosone.org/article/fetchObject.action?uri=info%3Adoi%2F10.1371%2Fjournal.pone.0029411&representation=PDF',
                  pmc_url='http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3245287/'),
    ScrapeFixture('frontiers', '21212836',
                  'http://www.frontiersin.org/Brain_Imaging_Methods/10.3389/fnins.2012.00149/abstract',
                  html_url='http://www.frontiersin.org/Journal/10.3389/fnins.2012.00149/full',
                  pdf_url='http://www.frontiersin.org/Journal/DownloadFile/1/1223/33928/1/21/fnins-06-00149_pdf',
                  pmc_url='http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3014651/'),
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
                  'https://www.thieme-connect.com/ejournals/abstract/10.1055/s-0033-1346973',
                  html_url='https://www.thieme-connect.com/ejournals/html/10.1055/s-0033-1346973',
                  pdf_url='https://www.thieme-connect.com/ejournals/pdf/10.1055/s-0033-1346973.pdf',
                  pmc_url='http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3713555/',
                  ),
    ScrapeFixture('wolterskluwer', '23820739',
                  'http://pt.wkhealth.com/pt/re/lwwgateway/landingpage.htm;jsessionid=Sk0LdzQnrgTj45GChL11g16jpc448ylMQVtbcJLrrGzzkGVCQk2f!1583820841!181195628!8091!-1?issn=0959-4965&volume=24&issue=14&spage=763',
                  html_url='http://journals.lww.com/neuroreport/Fulltext/2013/10020/N_methyl_D_aspartate_receptors_and_protein.1.aspx',
                  pdf_url='http://pdfs.journals.lww.com/neuroreport/2013/10020/N_methyl_D_aspartate_receptors_and_protein.1.pdf?token=method|ExpireAbsolute;source|Journals;ttl|1382299311840;payload|mY8D3u1TCCsNvP5E421JYPPlNl9ZUXrQDsjmMHeXqBgfxP56d5BAis+WhfSrPR1S6lcHrAT5WTvTkrI7Jc1zUq2UlEn8N1x7qr2heZXbSZE2/LnQkUnbAwLtuHlqxiruZhFwwtFf4aeU4rMgwns+8TDbNbAkOUlffcIt0OqswFvWf97qU1+XR+GRM7R1S2drJjlMZyk5umnCyX0ZsO+WQO3OqrC6kWZHGFmwsUyPoy3TkarWdvvy6Y+Y2j71uz08ZT48Kq4FnoD9k2sZ/f2+VtLuq7uoIKDiRliJeppVX+rw4UyT+wiUZhSlAJO7dAyjR9vmyVAWVtaC6WwAPrLYreszSV1KWThE7hh6oMJQ6lmjEbXKC+gaal/PsKlfuCcwBrUqJIORKZEJNXxZBdgr3PQsdpBR5D41VaEH2MOCVFQOReXo4fsg/YHzlI735ThKGKWml7j5Rn+50uie6sSdJqjf0QLWOa0q+IPzv3lP9DbtjtVBzj37I05+xyFEQYy8hkPvrHfu33uPvCYtoLj6J9uZawa0r/hG4jNiOlz9FC7GJdeYruj0bK5VQBSvsgdY/dBIMeG3lNTXUCUcvJSluK0aGIw6Dz6nHkcE/3S4anFLYlT+riIYTCGiEX23hvUO;hash|vmv2MykiUFT+CiEbJ8nt1w==',
                  )
]


from sciscrape.scrapetools.scrape import UMScrape

s = UMScrape(user_file='/Users/jmcarp/private/ump')

i = s.scrape(pmid='22103784', fetch_types=['pdf', 'html'])
i.save('apa', save_dir='/Users/jmcarp/Desktop')
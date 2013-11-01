import requests
import urlparse
import itertools
from pyquery import PyQuery
from urllib2 import URLError
from Bio import Entrez, Medline

import retry

email = None
class EntrezEmailError(Exception): pass

PUBMED_URL = 'http://www.ncbi.nlm.nih.gov/pubmed/'

# See http://www.nlm.nih.gov/bsd/mms/medlineelements.html
def ensure_email(func):
    def wrapped(*args, **kwargs):
        if Entrez.email is None:
            if email is not None:
                Entrez.email = email
            else:
                raise EntrezEmailError(
                    "Email address not defined. "
                    "When using the pubtools module, always provide your email address: \n"
                    ">>> from sciscrape.utils import pubtools \n"
                    ">>> pubtools.email = 'foo@bar.baz' "
                )
        return func(*args, **kwargs)
    return wrapped

@ensure_email
@retry.retry(URLError, tries=3, default=[])
def search_pmids(term, retmax=999999, **kwargs):

    return Entrez.read(
        Entrez.esearch(
            term=term,
            db='pubmed',
            retmax=retmax,
            **kwargs
        )
    )['IdList']

@retry.retry(URLError, tries=3, default=[])
def parse_medline_chunk(chunk):
    handle = Entrez.efetch(
        db='pubmed',
        rettype='medline',
        id=','.join(pmid for pmid in chunk if pmid),
    )
    return Medline.parse(handle)

@ensure_email
def download_pmids(pmids, chunk_size=25):

    records = []

    # See http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
    chunks = itertools.izip_longest(
        *[iter(pmids)] * chunk_size, fillvalue=None
    )

    for chunk in chunks:
        records.extend(parse_medline_chunk(pmid for pmid in chunk if pmid))

    return records

def record_to_doi(record):

    identifiers = record.get('article_identifier', [])
    location_identifier = record.get('location_identifier')
    if location_identifier:
        identifiers.append(location_identifier)
    for identifier in identifiers:
        if ' [doi]' in identifier:
            return identifier.replace(' [doi]', '')

def _contains_publisher_url():
    parsed = PyQuery(this)
    if parsed.attr('title') == "Full text at publisher's site":
        return True
    child_image_title = parsed('img').attr('title')
    if child_image_title and child_image_title.startswith('Read full text in'):
        return True
    return False

def pmid_to_publisher_link(pmid):
    """Get publisher link from PubMed.

    :param pmid: PubMed ID
    :return: Link to document on publisher site

    """
    # Get PubMed HTML
    pubmed_url = urlparse.urljoin(PUBMED_URL, pmid)
    req = requests.get(pubmed_url)

    # Note: Use ``content`` property of request rather than ``text`` so that
    # PyQuery won't choke on unicode input.
    html_parse = PyQuery(req.content).xhtml_to_html()
    return html_parse('a').filter(_contains_publisher_url).attr('href')

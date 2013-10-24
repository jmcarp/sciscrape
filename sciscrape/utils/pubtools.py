import requests
import urlparse
import itertools

from pyquery import PyQuery
from Bio import Entrez, Medline

email = None
class EntrezEmailError(Exception): pass

PUBMED_URL = 'http://www.ncbi.nlm.nih.gov/pubmed/'

# See http://www.nlm.nih.gov/bsd/mms/medlineelements.html
MEDLINE_TO_TEXT = {
    'AB': 'abstract',
    'AD': 'affiliation',
    'AID': 'article_identifier',
    'AU': 'author',
    'CI': 'copyright_information',
    'CIN': 'comment_in',
    'CN': 'corporate_author',
    'CON': 'comment_on',
    'CRDT': 'create_date',
    'CRF': 'corrected_republished_from',
    'CRI': 'corrected_republished_in',
    'DA': 'date_created',
    'DEP': 'date_of_electronic_publication',
    'DCOM': 'date_completed',
    'DP': 'date_of_publication',
    'EDAT': 'entrez_date',
    'EFR': 'erratum_for',
    'EIN': 'erratum_in',
    'FAU': 'full_author',
    'FIR': 'full_investigator_name',
    'GN': 'general_note',
    'GR': 'grant_number',
    'IR': 'investigator_name',
    'JT': 'journal_title',
    'JID': 'nlm_unique_id',
    'LA': 'language',
    'LID': 'location_identifier',
    'LR': 'date_last_revised',
    'MH': 'mesh_terms',
    'MHDA': 'mesh_date',
    'MID': 'manuscript_id',
    'IP': 'issue',
    'IS': 'issn',
    'OAB': 'other_abstract',
    'OID': 'other_id',
    'OT': 'other_term',
    'OTO': 'other_term_owner',
    'OWN': 'owner',
    'ORI': 'original_report_in',
    'PG': 'pagination',
    'PHST': 'publication_history_status',
    'PL': 'place_of_publication',
    'PMC': 'pubmed_central_identifier',
    'PMCR': 'pubmed_central_release',
    'PMID': 'pubmed_unique_identifier',
    'PRIN': 'published_retracted_in',
    'PST': 'publication_status',
    'PT': 'publication_type',
    'RF': 'number_of_references',
    'RN': 'registry_number',
    'SB': 'subset',
    'SI': 'secondary_source_id',
    'SO': 'source',
    'STAT': 'status',
    'TA': 'journal_title_abbreviation',
    'TI': 'title',
    'TT': 'transliterated_title',
    'VI': 'volume',
}

TEXT_TO_MEDLINE = {val: key for key, val in MEDLINE_TO_TEXT.iteritems()}

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
def search_pmids(term, retmax=999999, **kwargs):

    return Entrez.read(
        Entrez.esearch(
            term=term,
            db='pubmed',
            retmax=retmax,
            **kwargs
        )
    )['IdList']

@ensure_email
def download_pmids(pmids, chunk_size=25):

    records = []

    # See http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
    chunks = itertools.izip_longest(
        *[iter(pmids)] * chunk_size, fillvalue=None
    )

    for chunk in chunks:
        handle = Entrez.efetch(
            db='pubmed',
            rettype='medline',
            id=','.join(pmid for pmid in chunk if pmid),
        )
        for record in Medline.parse(handle):
            records.append({
                MEDLINE_TO_TEXT[key]: value
                for key, value in record.iteritems()
            })

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

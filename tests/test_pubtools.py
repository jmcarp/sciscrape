import unittest
from nose.tools import *
from nose_parameterized import parameterized

from sciscrape.utils import pubtools

class TestEntrezWithEmail(unittest.TestCase):

    def setUp(self):

        pubtools.email = 'foo@bar.baz'

    def tearDown(self):

        pubtools.email = None
        pubtools.Entrez.email = None

    def test_search_pmids(self):
        """ Searching for an article by PMID should return the same PMID. """

        pmids = pubtools.search_pmids('1[uid]')
        assert_equal(pmids, ['1'])

    def test_download_pmids(self):
        """ Downloading articles by PMID should return correct MEDLINE data. """

        records = pubtools.download_pmids(['1', '2', '3'], chunk_size=2)

        assert_equal(len(records), 3)

        assert_equal(records[0], DATA_PMID_1)
        assert_equal(records[1], DATA_PMID_2)
        assert_equal(records[2], DATA_PMID_3)

class TestEntrezWithoutEmail(unittest.TestCase):

    def test_search_pmids(self):
        """ Searching for an article by PMID should return the same PMID. """

        with assert_raises(pubtools.EntrezEmailError):
            pubtools.search_pmids('1[uid]')

    def test_download_pmids(self):
        """ Downloading articles by PMID should return correct MEDLINE data. """

        with assert_raises(pubtools.EntrezEmailError):
            pubtools.download_pmids(['1', '2', '3'], chunk_size=2)

@parameterized([
    ('1', 'http://ntp.niehs.nih.gov/ntp/htdocs/LT_Rpts/TR514.pdf'),
    ('2', 'http://linkinghub.elsevier.com/retrieve/pii/0006-291X(75)90482-9'),
    ('3', 'http://linkinghub.elsevier.com/retrieve/pii/0006-291X(75)90498-2'),
])
def test_pmid_to_publisher_link(pmid, publisher_link):
    """ Should find known publisher links by PMID. """

    publisher_link = pubtools.pmid_to_publisher_link(pmid)
    assert_equal(publisher_link, publisher_link)

### Test data ###

DATA_PMID_1 = {'author': ['Makar AB', 'McMartin KE', 'Palese M', 'Tephly TR'],
 'create_date': ['1975/06/01 00:00'],
 'date_completed': '19760116',
 'date_created': '19760116',
 'date_last_revised': '20091111',
 'date_of_publication': '1975 Jun',
 'entrez_date': '1975/06/01',
 'full_author': ['Makar, A B', 'McMartin, K E', 'Palese, M', 'Tephly, T R'],
 'issn': '0006-2944 (Print) 0006-2944 (Linking)',
 'issue': '2',
 'journal_title': 'Biochemical medicine',
 'journal_title_abbreviation': 'Biochem Med',
 'language': ['eng'],
 'mesh_date': '1975/06/01 00:01',
 'mesh_terms': ['Aldehyde Oxidoreductases/metabolism',
                'Animals',
                'Body Fluids/*analysis',
                'Carbon Dioxide/blood',
                'Formates/blood/*poisoning',
                'Haplorhini',
                'Humans',
                'Hydrogen-Ion Concentration',
                'Kinetics',
                'Methanol/blood',
                'Methods',
                'Pseudomonas/enzymology'],
 'nlm_unique_id': '0151424',
 'owner': 'NLM',
 'pagination': '117-26',
 'place_of_publication': 'UNITED STATES',
 'publication_status': 'ppublish',
 'publication_type': ['Journal Article',
                      "Research Support, U.S. Gov't, P.H.S."],
 'pubmed_unique_identifier': '1',
 'registry_number': ['0 (Formates)',
                     '124-38-9 (Carbon Dioxide)',
                     '67-56-1 (Methanol)',
                     'EC 1.2.- (Aldehyde Oxidoreductases)'],
 'source': 'Biochem Med. 1975 Jun;13(2):117-26.',
 'status': 'MEDLINE',
 'subset': 'IM',
 'title': 'Formate assay in body fluids: application in methanol poisoning.',
 'volume': '13'}

DATA_PMID_2 = {'article_identifier': ['0006-291X(75)90482-9 [pii]'],
 'author': ['Bose KS', 'Sarma RH'],
 'create_date': ['1975/10/27 00:00'],
 'date_completed': '19760110',
 'date_created': '19760110',
 'date_last_revised': '20061115',
 'date_of_publication': '1975 Oct 27',
 'entrez_date': '1975/10/27',
 'full_author': ['Bose, K S', 'Sarma, R H'],
 'issn': '0006-291X (Print) 0006-291X (Linking)',
 'issue': '4',
 'journal_title': 'Biochemical and biophysical research communications',
 'journal_title_abbreviation': 'Biochem Biophys Res Commun',
 'language': ['eng'],
 'mesh_date': '1975/10/27 00:01',
 'mesh_terms': ['Fourier Analysis',
                'Magnetic Resonance Spectroscopy',
                'Models, Molecular',
                'Molecular Conformation',
                '*NAD/analogs & derivatives',
                '*NADP',
                'Structure-Activity Relationship',
                'Temperature'],
 'nlm_unique_id': '0372516',
 'owner': 'NLM',
 'pagination': '1173-9',
 'place_of_publication': 'UNITED STATES',
 'publication_status': 'ppublish',
 'publication_type': ['Journal Article',
                      "Research Support, U.S. Gov't, Non-P.H.S.",
                      "Research Support, U.S. Gov't, P.H.S."],
 'pubmed_unique_identifier': '2',
 'registry_number': ['53-59-8 (NADP)', '53-84-9 (NAD)'],
 'source': 'Biochem Biophys Res Commun. 1975 Oct 27;66(4):1173-9.',
 'status': 'MEDLINE',
 'subset': 'IM',
 'title': 'Delineation of the intimate details of the backbone conformation of pyridine nucleotide coenzymes in aqueous solution.',
 'volume': '66'}

DATA_PMID_3 = {'article_identifier': ['0006-291X(75)90498-2 [pii]'],
 'author': ['Smith RJ', 'Bryant RG'],
 'create_date': ['1975/10/27 00:00'],
 'date_completed': '19760110',
 'date_created': '19760110',
 'date_last_revised': '20061115',
 'date_of_publication': '1975 Oct 27',
 'entrez_date': '1975/10/27',
 'full_author': ['Smith, R J', 'Bryant, R G'],
 'issn': '0006-291X (Print) 0006-291X (Linking)',
 'issue': '4',
 'journal_title': 'Biochemical and biophysical research communications',
 'journal_title_abbreviation': 'Biochem Biophys Res Commun',
 'language': ['eng'],
 'mesh_date': '1975/10/27 00:01',
 'mesh_terms': ['Animals',
                'Binding Sites',
                '*Cadmium',
                '*Carbonic Anhydrases/metabolism',
                'Cattle',
                'Humans',
                'Hydrogen-Ion Concentration',
                'Magnetic Resonance Spectroscopy',
                '*Mercury',
                'Protein Binding',
                'Protein Conformation',
                '*Zinc/pharmacology'],
 'nlm_unique_id': '0372516',
 'owner': 'NLM',
 'pagination': '1281-6',
 'place_of_publication': 'UNITED STATES',
 'publication_status': 'ppublish',
 'publication_type': ['Journal Article',
                      "Research Support, U.S. Gov't, P.H.S."],
 'pubmed_unique_identifier': '3',
 'registry_number': ['7439-97-6 (Mercury)',
                     '7440-43-9 (Cadmium)',
                     '7440-66-6 (Zinc)',
                     'EC 4.2.1.1 (Carbonic Anhydrases)'],
 'source': 'Biochem Biophys Res Commun. 1975 Oct 27;66(4):1281-6.',
 'status': 'MEDLINE',
 'subset': 'IM',
 'title': 'Metal substitutions incarbonic anhydrase: a halide ion probe study.',
 'volume': '66'}
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

        assert_equal(records[0], DATA_PMID[0])
        assert_equal(records[1], DATA_PMID[1])
        assert_equal(records[2], DATA_PMID[2])

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

DATA_PMID = [{'AU': ['Makar AB', 'McMartin KE', 'Palese M', 'Tephly TR'],
  'CRDT': ['1975/06/01 00:00'],
  'DA': '19760116',
  'DCOM': '19760116',
  'DP': '1975 Jun',
  'EDAT': '1975/06/01',
  'FAU': ['Makar, A B', 'McMartin, K E', 'Palese, M', 'Tephly, T R'],
  'IP': '2',
  'IS': '0006-2944 (Print) 0006-2944 (Linking)',
  'JID': '0151424',
  'JT': 'Biochemical medicine',
  'LA': ['eng'],
  'LR': '20131121',
  'MH': ['Aldehyde Oxidoreductases/metabolism',
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
  'MHDA': '1975/06/01 00:01',
  'OWN': 'NLM',
  'PG': '117-26',
  'PL': 'UNITED STATES',
  'PMID': '1',
  'PST': 'ppublish',
  'PT': ['Journal Article', "Research Support, U.S. Gov't, P.H.S."],
  'RN': ['0 (Formates)',
         '142M471B3J (Carbon Dioxide)',
         'EC 1.2.- (Aldehyde Oxidoreductases)',
         'Y4S76JWI15 (Methanol)'],
  'SB': 'IM',
  'SO': 'Biochem Med. 1975 Jun;13(2):117-26.',
  'STAT': 'MEDLINE',
  'TA': 'Biochem Med',
  'TI': 'Formate assay in body fluids: application in methanol poisoning.',
  'VI': '13'},
 {'AID': ['0006-291X(75)90482-9 [pii]'],
  'AU': ['Bose KS', 'Sarma RH'],
  'CRDT': ['1975/10/27 00:00'],
  'DA': '19760110',
  'DCOM': '19760110',
  'DP': '1975 Oct 27',
  'EDAT': '1975/10/27',
  'FAU': ['Bose, K S', 'Sarma, R H'],
  'IP': '4',
  'IS': '0006-291X (Print) 0006-291X (Linking)',
  'JID': '0372516',
  'JT': 'Biochemical and biophysical research communications',
  'LA': ['eng'],
  'LR': '20131121',
  'MH': ['Fourier Analysis',
         'Magnetic Resonance Spectroscopy',
         'Models, Molecular',
         'Molecular Conformation',
         '*NAD/analogs & derivatives',
         '*NADP',
         'Structure-Activity Relationship',
         'Temperature'],
  'MHDA': '1975/10/27 00:01',
  'OWN': 'NLM',
  'PG': '1173-9',
  'PL': 'UNITED STATES',
  'PMID': '2',
  'PST': 'ppublish',
  'PT': ['Journal Article',
         "Research Support, U.S. Gov't, Non-P.H.S.",
         "Research Support, U.S. Gov't, P.H.S."],
  'RN': ['0U46U6E8UK (NAD)', '53-59-8 (NADP)'],
  'SB': 'IM',
  'SO': 'Biochem Biophys Res Commun. 1975 Oct 27;66(4):1173-9.',
  'STAT': 'MEDLINE',
  'TA': 'Biochem Biophys Res Commun',
  'TI': 'Delineation of the intimate details of the backbone conformation of pyridine nucleotide coenzymes in aqueous solution.',
  'VI': '66'},
 {'AID': ['0006-291X(75)90498-2 [pii]'],
  'AU': ['Smith RJ', 'Bryant RG'],
  'CRDT': ['1975/10/27 00:00'],
  'DA': '19760110',
  'DCOM': '19760110',
  'DP': '1975 Oct 27',
  'EDAT': '1975/10/27',
  'FAU': ['Smith, R J', 'Bryant, R G'],
  'IP': '4',
  'IS': '0006-291X (Print) 0006-291X (Linking)',
  'JID': '0372516',
  'JT': 'Biochemical and biophysical research communications',
  'LA': ['eng'],
  'LR': '20131121',
  'MH': ['Animals',
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
  'MHDA': '1975/10/27 00:01',
  'OWN': 'NLM',
  'PG': '1281-6',
  'PL': 'UNITED STATES',
  'PMID': '3',
  'PST': 'ppublish',
  'PT': ['Journal Article', "Research Support, U.S. Gov't, P.H.S."],
  'RN': ['00BH33GNGH (Cadmium)',
         'EC 4.2.1.1 (Carbonic Anhydrases)',
         'FXS1BY2PGL (Mercury)',
         'J41CSQ7QDS (Zinc)'],
  'SB': 'IM',
  'SO': 'Biochem Biophys Res Commun. 1975 Oct 27;66(4):1281-6.',
  'STAT': 'MEDLINE',
  'TA': 'Biochem Biophys Res Commun',
  'TI': 'Metal substitutions incarbonic anhydrase: a halide ion probe study.',
  'VI': '66'}]

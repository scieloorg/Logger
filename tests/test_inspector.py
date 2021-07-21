try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from logger.inspector import Inspector
from unittest import TestCase


class MockCollection(object):

    def __init__(self, code, acronym, acronym2):
        self.code = code
        self.acronym = acronym
        self.acronym2letters = acronym2


_COLLECTIONS = [
    MockCollection("scl", "scl", "br"),
    MockCollection("spa", "spa", "sp"),
]


@patch("logger.utils.try_get_collections", return_value=_COLLECTIONS)
class TestInspectorTests(TestCase):

    def test_is_valid_filename_node1(self, mock_):
        insp = Inspector('/var/www/scielo.br/2015-12-30_scielo.br.1.log.gz')
        self.assertTrue(insp._is_valid_filename())
        expected = {
            'date': '2015-12-30',
            'collection': 'br'
        }
        self.assertEqual(expected, insp._parsed_fn.groupdict())

    def test_is_valid_filename(self, mock_):
        insp = Inspector('/var/www/scielo.br/2015-12-30_scielo.br.log.gz')

        self.assertTrue(insp._is_valid_filename())
        expected = {
            'date': '2015-12-30',
            'collection': 'br'
        }
        self.assertEqual(expected, insp._parsed_fn.groupdict())

    def test_is_valid_filename_false(self, mock_):
        insp = Inspector('/var/www/scielo.br/2015-12-30_scilo.br.log.gz')
        self.assertFalse(insp._is_valid_filename())

    def test_is_valid_date_in_filename(self, mock_):
        insp = Inspector('/var/www/scielo.br/2015-12-30_scielo.br.log.gz')
        self.assertTrue(insp._is_valid_date())

    def test_is_valid_date_in_filename_false(self, mock_):
        insp = Inspector('/var/www/scielo.br/2015-31-12_scielo.br.log.gz')
        self.assertFalse(insp._is_valid_date())

    def test_is_valid_collection_in_filename(self, mock_):
        insp = Inspector('/var/www/scielo.br/2015-12-30_scielo.br.log.gz')
        self.assertTrue(insp._is_valid_collection())

    def test_is_invalid_collection_in_filename(self, mock_):
        insp = Inspector('/var/www/scielo.br/2015-12-30_scielo.xxx.log.gz')
        self.assertFalse(insp._is_valid_collection())

    def test_is_valid_source_directory(self, mock_):
        insp = Inspector('/var/www/scielo.br/2015-12-30_scielo.br.log.gz')
        self.assertTrue(insp._is_valid_source_directory())

    def test_is_valid_source_directory_false_1(self, mock_):
        insp = Inspector('/var/www/scielo.br/2015-12-30_sciel.br.log.gz')
        self.assertFalse(insp._is_valid_source_directory())

    def test_is_valid_source_directory_false_2(self, mock_):
        insp = Inspector('/var/www/scielo.pepsic/2015-12-30_scielo.br.log.gz')
        self.assertFalse(insp._is_valid_source_directory())

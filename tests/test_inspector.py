import unittest

from logger.inspector import Inspector
from mocker import ANY, MockerTestCase

COLLECTIONS = {
    'br': {
        "status": "certified",
        "original_name": "Brasil",
        "document_count": 392414,
        "acron": "scl",
        "domain": "www.scielo.br",
        "has_analytics": True,
        "is_active": True,
        "journal_count": {
            "deceased": 42,
            "suspended": 36,
            "current": 295
        },
        "type": "journals",
        "acron2": "br",
        "name": {
            "en": "Brazil",
            "es": "Brasil",
            "pt": "Brasil"
        },
        "code": "scl"
    }
}

class TestInspectorTests(MockerTestCase):

    def test_is_valid_filename_node1(self):

        _insp = self.mocker.patch(Inspector)
        _insp.get_collections()
        self.mocker.result(COLLECTIONS)
        self.mocker.replay()

        insp = Inspector('/var/www/scielo.br/2015-12-30_scielo.br.1.log.gz')

        self.assertTrue(insp._is_valid_filename())
        expected = {
            'date': '2015-12-30',
            'collection': 'br'
        }
        self.assertEqual(expected, insp._parsed_fn.groupdict())

    def test_is_valid_filename(self):
        _insp = self.mocker.patch(Inspector)
        _insp.get_collections()
        self.mocker.result(COLLECTIONS)
        self.mocker.replay()

        insp = Inspector('/var/www/scielo.br/2015-12-30_scielo.br.log.gz')

        self.assertTrue(insp._is_valid_filename())
        expected = {
            'date': '2015-12-30',
            'collection': 'br'
        }
        self.assertEqual(expected, insp._parsed_fn.groupdict())

    def test_is_valid_filename_false(self):
        _insp = self.mocker.patch(Inspector)
        _insp.get_collections()
        self.mocker.result(COLLECTIONS)
        self.mocker.replay()

        insp = Inspector('/var/www/scielo.br/2015-12-30_scilo.br.log.gz')

        self.assertFalse(insp._is_valid_filename())

    def test_is_valid_date_in_filename(self):
        _insp = self.mocker.patch(Inspector)
        _insp.get_collections()
        self.mocker.result(COLLECTIONS)
        self.mocker.replay()

        insp = Inspector('/var/www/scielo.br/2015-12-30_scielo.br.log.gz')

        self.assertTrue(insp._is_valid_date())

    def test_is_valid_date_in_filename_false(self):
        _insp = self.mocker.patch(Inspector)
        _insp.get_collections()
        self.mocker.result(COLLECTIONS)
        self.mocker.replay()

        insp = Inspector('/var/www/scielo.br/2015-31-12_scielo.br.log.gz')

        self.assertFalse(insp._is_valid_date())

    def test_is_valid_collection_in_filename(self):
        _insp = self.mocker.patch(Inspector)
        _insp.get_collections()
        self.mocker.result(COLLECTIONS)
        self.mocker.replay()

        insp = Inspector('/var/www/scielo.br/2015-12-30_scielo.br.log.gz')
        self.assertTrue(insp._is_valid_collection())

    def test_is_invalid_collection_in_filename(self):
        _insp = self.mocker.patch(Inspector)
        _insp.get_collections()
        self.mocker.result(COLLECTIONS)
        self.mocker.replay()

        insp = Inspector('/var/www/scielo.br/2015-12-30_scielo.xxx.log.gz')
        self.assertFalse(insp._is_valid_collection())

    def test_is_valid_source_directory(self):
        _insp = self.mocker.patch(Inspector)
        _insp.get_collections()
        self.mocker.result(COLLECTIONS)
        self.mocker.replay()
        insp = Inspector('/var/www/scielo.br/2015-12-30_scielo.br.log.gz')

        self.assertTrue(insp._is_valid_source_directory())

    def test_is_valid_source_directory_false_1(self):
        _insp = self.mocker.patch(Inspector)
        _insp.get_collections()
        self.mocker.result(COLLECTIONS)
        self.mocker.replay()
        insp = Inspector('/var/www/scielo.br/2015-12-30_sciel.br.log.gz')

        self.assertFalse(insp._is_valid_source_directory())

    def test_is_valid_source_directory_false_2(self):
        _insp = self.mocker.patch(Inspector)
        _insp.get_collections()
        self.mocker.result(COLLECTIONS)
        self.mocker.replay()

        insp = Inspector('/var/www/scielo.pepsic/2015-12-30_scielo.br.log.gz')

        self.assertFalse(insp._is_valid_source_directory())

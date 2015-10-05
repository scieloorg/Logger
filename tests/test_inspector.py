import unittest

from logger import inspector


class TestInspectorTests(unittest.TestCase):

    def test_is_valid_filename(self):
        insp = inspector.Inspector('2015-12-30_scielo.br.log.gz')

        self.assertTrue(insp._is_valid_filename())

    def test_is_valid_filename_false(self):
        insp = inspector.Inspector('2015-12-30_scilo.br.log.gz')

        self.assertFalse(insp._is_valid_filename())

    def test_is_valid_date_in_filename(self):
        insp = inspector.Inspector('2015-12-30_scielo.br.log.gz')

        self.assertTrue(insp._is_valid_date())

    def test_is_valid_date_in_filename_false(self):
        insp = inspector.Inspector('2015-31-12_scielo.br.log.gz')

        self.assertFalse(insp._is_valid_date())

    def test_is_valid_collection_in_filename(self):
        insp = inspector.Inspector('2015-12-30_scielo.br.log.gz')

        self.assertTrue(insp._is_valid_collection())

    def test_is_valid_collection_in_filename(self):
        insp = inspector.Inspector('2015-12-30_scielo.xxx.log.gz')

        self.assertFalse(insp._is_valid_collection())

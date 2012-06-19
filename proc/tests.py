# -*- encoding: utf-8 -*-
import unittest
from loginspector import LogInspector
import tests_assets

class DummyMongoConnection(object):

    HOST = "localhost"
    PORT = "27017"

    def __init__(self,host, port, **kwargs):
        self._host = host
        self._port = port

class DummyMongoCollection(object):

    def find_one(self, spec_or_id=None, *args, **kwargs):

        return test_assets.get_sample_item()

class ViewTests(unittest.TestCase):

    def setUp(self):
        self.inspector = LogInspector(tests_assets.get_sample_allowed_patterns())
    
    #def tearDown(self):
        #testing.tearDown()

    def test_listtypes(self):
        """
        Testing if the retrieved code types are correct according to the get_sample_allowed_patterns()
        The codes must be truncate to 3 characters
        """
        types = tests_assets.get_sample_types()
        self.assertEqual(types, self.inspector.listtypes())

    def test_listtypeindexes(self):
        """
        Testing if the retrieved code types and your respective contexts are correct according to 
        the get_sample_allowed_patterns()
        """
        types = tests_assets.get_sample_types_index()
        self.assertEqual(types, self.inspector.listtypeindexes())

    def test_getitem(self):
        """
        Testing the log access retrieve from a specific document code
        """

        item = tests_assets.get_sample_item()
        self.assertEqual(item, self.inspector.getitem('q5cc4'))        

if __name__ == '__main__':
    unittest.main()
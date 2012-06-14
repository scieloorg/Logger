import unittest
import request
import tests_assets

class ViewTests(unittest.TestCase):

    def setUp(self):
        self.types = tests_assets.get_sample_pattern_types()

    #def tearDown(self):
        #testing.tearDown()

    def test_listpatterns(self):
        self.assertEqual(self.types, request.listpatterns())

if __name__ == '__main__':
    unittest.main()
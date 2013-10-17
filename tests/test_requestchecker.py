# coding: utf-8

from mocker import ANY, MockerTestCase

from logger.accesschecker import AccessChecker

network = """{"total_rows":31,"offset":0,"rows":[
                {
                    "id":"arg",
                    "key":["certified","arg"],
                    "value":{
                        "_id":"arg",
                        "_rev":"1-df50175ad35971784d6f713b9c5bbe5b",
                        "acron":"arg",
                        "acron2":"ar",
                        "domain":"www.scielo.org.ar",
                        "name":{
                            "pt":"Argentina",
                            "es":"Argentina",
                            "en":"Argentina"},
                        "status":"certified",
                        "v706":"network"
                    }
                }]
            }"""

class AccessCheckerTests(MockerTestCase):

    def test_instanciatingAccessChecker(self):
        mock_urllib2 = self.mocker.replace("urllib2")
        mock_urlopen = self.mocker.mock()

        mock_urllib2.urlopen(ANY)
        self.mocker.result(mock_urlopen)

        mock_urlopen.read()
        self.mocker.result(network)
        self.mocker.replay()

        self.assertTrue(isinstance(AccessChecker(collection='scl'), AccessChecker))

    def test_instanciatingAccessChecker_with_invalid_collection(self):
        mock_urllib2 = self.mocker.replace("urllib2")
        mock_urlopen = self.mocker.mock()

        mock_urllib2.urlopen(ANY)
        self.mocker.result(mock_urlopen)

        mock_urlopen.read()
        self.mocker.result(network)
        self.mocker.replay()

        with self.assertRaises(ValueError):
            AccessChecker(collection='xxx')

    def test_allowed_collections(self):
        mock_urllib2 = self.mocker.replace("urllib2")
        mock_urlopen = self.mocker.mock()

        mock_urllib2.urlopen(ANY)
        self.mocker.result(mock_urlopen)

        mock_urlopen.read()
        self.mocker.result(network)
        self.mocker.replay()

        self.assertEqual(AccessChecker(collection='scl').collection, 'scl')

# coding: utf-8

import urllib2

from mocker import ANY, MockerTestCase

from logger.accesschecker import AccessChecker
from . import fixtures

class AccessCheckerTests(MockerTestCase):

    def test_instanciatingAccessChecker(self):
        mock_urllib2 = self.mocker.replace("urllib2")

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.network)

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.titles)

        self.mocker.replay()

        self.assertTrue(isinstance(AccessChecker(collection='scl'), AccessChecker))

    def test_instanciatingAccessChecker_with_invalid_collection(self):
        mock_urllib2 = self.mocker.replace("urllib2")

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.network)

        self.mocker.replay()

        with self.assertRaises(ValueError):
            AccessChecker(collection='xxx')

    def test_instanciatingAccessChecker_allowed_collections(self):
        mock_urllib2 = self.mocker.replace("urllib2")

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.network)

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.titles)

        self.mocker.replay()

        self.assertEqual(AccessChecker(collection='scl').collection, 'scl')

    def test_instanciatingAccessChecker_allowed_collections_exception(self):
        mock_urllib2 = self.mocker.replace("urllib2")

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.throw(urllib2.URLError('Was not possible to connect to webservices.scielo.org, try again later!'))

        self.mocker.replay()

        with self.assertRaises(urllib2.URLError):
            AccessChecker(collection='scl')

    def test_instanciatingAccessChecker_allowed_issns(self):
        mock_urllib2 = self.mocker.replace("urllib2")

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.network)

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.titles)

        self.mocker.replay()

        self.assertEqual(AccessChecker(collection='scl').allowed_issns, {u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})

    def test_instanciatingAccessChecker_allowed_issns_exception(self):
        mock_urllib2 = self.mocker.replace("urllib2")

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.network)

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.throw(urllib2.URLError('Was not possible to connect to webservices.scielo.org, try again later!'))

        self.mocker.replay()

        with self.assertRaises(urllib2.URLError):
            AccessChecker(collection='scl')


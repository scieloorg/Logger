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
        self.mocker.throw(urllib2.URLError(u'Was not possible to connect to webservices.scielo.org, try again later!'))

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
        self.mocker.throw(urllib2.URLError(u'Was not possible to connect to webservices.scielo.org, try again later!'))

        self.mocker.replay()

        with self.assertRaises(urllib2.URLError):
            AccessChecker(collection='scl')

    def test_pdf_or_html_access_for_html(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result(['scl', 'arg'])
        accesschecker._allowed_issns()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        get = u'GET http://www.scielo.br/scielo.php?pid=S0100-736X2000000300007&script=sci_arttext HTTP/1.1'

        self.assertEqual(ac.pdf_or_html_access(get), u'HTML')

        get = u'GET /scielo.php?pid=S0100-736X2000000300007&script=sci_arttext HTTP/1.1'

        self.assertEqual(ac.pdf_or_html_access(get), u'HTML')

    def test_pdf_or_html_access_for_pdf(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result(['scl', 'arg'])
        accesschecker._allowed_issns()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        get = u'GET http://www.scielo.br/pdf/isz/v96n2/a18v96n2.pdf HTTP/1.1'

        self.assertEqual(ac.pdf_or_html_access(get), u'PDF')

        get = u'GET /pdf/isz/v96n2/a18v96n2.pdf HTTP/1.1'

        self.assertEqual(ac.pdf_or_html_access(get), u'PDF')

    def test_pdf_or_html_access_for_files(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._allowed_issns()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        get = u'GET http://www.scielo.br/css/screen/styles.css HTTP/1.1'

        self.assertEqual(ac.pdf_or_html_access(get), None)

        get = u'GET /css/screen/styles.css HTTP/1.1'

        self.assertEqual(ac.pdf_or_html_access(get), None)

    def test_parse_line_with_apache_line(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._allowed_issns()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        line = '187.19.211.179 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/scielo.php?pid=S0100-736X2000000300007&script=sci_arttext HTTP/1.1" 200 25084 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'

        expected = {
                    '%l': '-',
                    '%>s': '200',
                    '%h': '187.19.211.179',
                    '%{User-Agent}i': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
                    '%b': '25084',
                    '%{Referer}i': '-',
                    '%u': '-',
                    '%t': '[30/May/2013:00:01:01 -0300]',
                    '%r': 'GET http://www.scielo.br/scielo.php?pid=S0100-736X2000000300007&script=sci_arttext HTTP/1.1'
                    }

        self.assertEqual(ac._parse_line(line), expected)

        line = '123.125.71.39 - - [30/Dec/2012:23:59:57 -0200] "GET /scielo.php?script=sci_nlinks&ref=000144&pid=S0103-4014200000020001300010&lng=pt HTTP/1.1" 200 1878 "-" "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)"'

        expected = {
                    '%l': '-',
                    '%>s': '200',
                    '%h': '123.125.71.39',
                    '%{User-Agent}i': 'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
                    '%b': '1878',
                    '%{Referer}i': '-',
                    '%u': '-',
                    '%t': '[30/Dec/2012:23:59:57 -0200]',
                    '%r': 'GET /scielo.php?script=sci_nlinks&ref=000144&pid=S0103-4014200000020001300010&lng=pt HTTP/1.1'
                    }

        self.assertEqual(ac._parse_line(line), expected)

    def test_parse_line_invalid_line(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._allowed_issns()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        line = ''

        self.assertEqual(ac._parse_line(line), None)

    def test_access_date(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._allowed_issns()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        access_date = u'[30/Dec/2012:23:59:57 -0200]'

        self.assertEqual(ac.access_date(access_date), u'2012-12-30')

    def test_access_date_with_invalid_month(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._allowed_issns()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        access_date = u'[30/xxx/2012:23:59:57 -0200]'

        self.assertEqual(ac.access_date(access_date), None)

    def test_access_date_with_invalid_day(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._allowed_issns()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        access_date = u'[xx/Dec/2012:23:59:57 -0200]'

        self.assertEqual(ac.access_date(access_date), None)

    def test_access_date_with_invalid_year(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._allowed_issns()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        access_date = u'[12/Dec/x012:23:59:57 -0200]'

        self.assertEqual(ac.access_date(access_date), None)

    def test_access_date_with_invalid_date(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._allowed_issns()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        access_date = u''

        self.assertEqual(ac.access_date(access_date), None)

    def test_query_string_with_parameters(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._allowed_issns()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        url = u'GET http://www.scielo.br/scielo.php?pid=S0100-736X2000000300007&script=sci_arttext HTTP/1.1'

        self.assertEqual(ac.query_string(url), {u'pid': u'S0100-736X2000000300007', u'script': u'sci_arttext'})

        url = u'GET /scielo.php?pid=S0100-736X2000000300007&script=sci_arttext HTTP/1.1'

        self.assertEqual(ac.query_string(url), {u'pid': u'S0100-736X2000000300007', u'script': u'sci_arttext'})

    def test_query_string_without_parameters(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._allowed_issns()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        url = u'GET http://www.scielo.br/scielo.php HTTP/1.1'

        self.assertEqual(ac.query_string(url), None)


    def test_parsed_access_with_invalid_line(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._allowed_issns()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        line = u''
        
        self.assertEqual(ac.parsed_access(line), None)





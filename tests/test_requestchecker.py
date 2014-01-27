# coding: utf-8

import urllib2

from mocker import ANY, MockerTestCase

from logger.accesschecker import AccessChecker, TimedSet, checkdatelock
from . import fixtures


class TimedSetTests(MockerTestCase):
    def test_expiration(self):
        ts = TimedSet(expired=checkdatelock)
        ts.add('art1', '2013-05-29T00:01:01')
        self.assertTrue(ts._items, {'art1': '29/May/2013:00:01:01'})

        with self.assertRaises(ValueError):
            ts.add('art1', '2013-05-29T00:01:05')

        self.assertTrue(ts._items, {'art1': '29/May/2013:00:01:01'})

        ts.add('art1', '2013-05-29T00:01:22')
        self.assertTrue(ts._items, {'art1': '29/May/2013:00:01:22'})

    def test_expiration_custom_timeout(self):
        ts = TimedSet(expired=checkdatelock)
        ts.add('art1', '2013-05-29T00:01:01', 30)
        self.assertTrue(ts._items, {'art1': '29/May/2013:00:01:01'})

        with self.assertRaises(ValueError):
            ts.add('art1', '2013-05-29T00:01:031')

        self.assertTrue(ts._items, {'art1': '29/May/2013:00:01:01'})

        ts.add('art1', '2013-05-29T00:01:32')
        self.assertTrue(ts._items, {'art1': '29/May/2013:00:01:32'})


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

    def test_instanciatingAccessChecker_acron_to_issns_dict(self):
        mock_urllib2 = self.mocker.replace("urllib2")

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.network)

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.titles)

        self.mocker.replay()

        self.assertEqual(AccessChecker(collection='scl').acronym_to_issn_dict, {u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})

    def test_instanciatingAccessChecker_acronym_to_issn_dict_exception(self):
        mock_urllib2 = self.mocker.replace("urllib2")

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.network)

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.throw(urllib2.URLError(u'Was not possible to connect to webservices.scielo.org, try again later!'))

        self.mocker.replay()

        with self.assertRaises(urllib2.URLError):
            AccessChecker(collection='scl')

    def test_instanciatingAccessChecker_allowed_issn(self):
        mock_urllib2 = self.mocker.replace("urllib2")

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.network)

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.titles)

        self.mocker.replay()

        self.assertEqual(AccessChecker(collection='scl').allowed_issns, set([u'1234-4321', u'1984-4670']))

    def test_pdf_or_html_access_for_html(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result(['scl', 'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        request = u'GET http://www.scielo.br/scielo.php?pid=S0100-736X2000000300007&script=sci_arttext HTTP/1.1'

        self.assertEqual(ac._pdf_or_html_access(request), u'HTML')

        request = u'GET /scielo.php?pid=S0100-736X2000000300007&script=sci_arttext HTTP/1.1'

        self.assertEqual(ac._pdf_or_html_access(request), u'HTML')

    def test_pdf_or_html_access_for_pdf(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result(['scl', 'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        request = u'GET http://www.scielo.br/pdf/isz/v96n2/a18v96n2.pdf HTTP/1.1'

        self.assertEqual(ac._pdf_or_html_access(request), u'PDF')

        request = u'GET /pdf/isz/v96n2/a18v96n2.pdf HTTP/1.1'

        self.assertEqual(ac._pdf_or_html_access(request), u'PDF')

    def test_pdf_or_html_access_for_files(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        request = u'GET http://www.scielo.br/css/screen/styles.css HTTP/1.1'

        self.assertEqual(ac._pdf_or_html_access(request), None)

        request = u'GET /css/screen/styles.css HTTP/1.1'

        self.assertEqual(ac._pdf_or_html_access(request), None)

    def test_parse_line_with_apache_line(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
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
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        line = ''

        self.assertEqual(ac._parse_line(line), None)

    def test_access_date(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        access_date = u'[30/Dec/2012:23:59:57 -0200]'

        self.assertEqual(ac._access_date(access_date).date().isoformat(), u'2012-12-30')

    def test_access_datetime(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        access_date = u'[30/Dec/2012:23:59:57 -0200]'

        self.assertEqual(ac._access_date(access_date).isoformat(), u'2012-12-30T23:59:57')

    def test_access_date_with_invalid_month(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        access_date = u'[30/xxx/2012:23:59:57 -0200]'

        self.assertEqual(ac._access_date(access_date), None)

    def test_access_date_with_invalid_day(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        access_date = u'[xx/Dec/2012:23:59:57 -0200]'

        self.assertEqual(ac._access_date(access_date), None)

    def test_access_date_with_invalid_year(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        access_date = u'[12/Dec/x012:23:59:57 -0200]'

        self.assertEqual(ac._access_date(access_date), None)

    def test_access_date_with_invalid_date(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        access_date = u''

        self.assertEqual(ac._access_date(access_date), None)

    def test_query_string_with_parameters(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        url = u'GET http://www.scielo.br/scielo.php?pid=S0100-736X2000000300007&script=sci_arttext HTTP/1.1'

        self.assertEqual(ac._query_string(url), {u'pid': u'S0100-736X2000000300007', u'script': u'sci_arttext'})

        url = u'GET /scielo.php?pid=S0100-736X2000000300007&script=sci_arttext HTTP/1.1'

        self.assertEqual(ac._query_string(url), {u'pid': u'S0100-736X2000000300007', u'script': u'sci_arttext'})

    def test_query_string_without_parameters(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        url = u'GET http://www.scielo.br/scielo.php HTTP/1.1'

        self.assertEqual(ac._query_string(url), None)


    def test_pid_is_valid_not_allowed_issn(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')
        
        self.assertEqual(ac._is_valid_html_request('sci_arttext', 'XXXX-XXXX2012000100001'), None)

    def test_pid_is_valid_script_sci_arttext_invalid_pid(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')
        
        self.assertEqual(ac._is_valid_html_request('sci_arttext', '123443212012000100001'), None)

    def test_pid_is_valid_script_sci_arttext_valid_pid(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')
        
        self.assertEqual(ac._is_valid_html_request('sci_arttext', '1234-43212012000100001'), True)

    def test_pid_is_valid_script_sci_arttext_valid_pid_fbpe(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')
        
        self.assertEqual(ac._is_valid_html_request('sci_arttext', '1234-4321(12)00100001'), True)

    def test_pid_is_valid_script_sci_abstract_invalid_pid(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')
        
        self.assertEqual(ac._is_valid_html_request('sci_abstract', '1234-4321201200100001'), None)

    def test_pid_is_valid_script_sci_abstract_valid_pid(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')
        
        self.assertEqual(ac._is_valid_html_request('sci_abstract', '1234-43212012000100001'), True)

    def test_pid_is_valid_script_sci_abstract_valid_pid_fbpe(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')
        
        self.assertEqual(ac._is_valid_html_request('sci_abstract', '1234-4321(12)00100001'), True)

    def test_pid_is_valid_script_sci_pdf_invalid_pid(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')
        
        self.assertEqual(ac._is_valid_html_request('sci_pdf', '1234-43219012000100001'), None)

    def test_pid_is_valid_script_sci_pdf_valid_pid(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')
        
        self.assertEqual(ac._is_valid_html_request('sci_pdf', '1234-43212012000100001'), True)

    def test_pid_is_valid_script_sci_pdf_valid_pid_fbpe(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')
        
        self.assertEqual(ac._is_valid_html_request('sci_pdf', '1234-4321(12)00100001'), True)

    def test_pid_is_valid_script_sci_serial_valid_pid(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')
        
        self.assertEqual(ac._is_valid_html_request('sci_serial', '1234-4321'), True)

    def test_pid_is_valid_script_sci_issuetoc_valid_pid(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')
        
        self.assertEqual(ac._is_valid_html_request('sci_issuetoc', '1234-432120120001'), True)

    def test_pid_is_valid_script_sci_issuetoc_invalid_pid(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')
        
        self.assertEqual(ac._is_valid_html_request('sci_issuetoc', '1234432120120001'), None)


    def test_pid_is_valid_script_sci_issues_valid_pid(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')
        
        self.assertEqual(ac._is_valid_html_request('sci_issues', '1234-4321'), True)

    def test_pid_is_valid_pdf_request(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        request = u'GET http://www.scielo.br/pdf/zool/v96n2/a18v96n2.pdf HTTP/1.1'
        
        self.assertEqual(ac._is_valid_pdf_request(request), {'pdf_issn': u'1984-4670', 'pdf_path': u'/pdf/zool/v96n2/a18v96n2.pdf'})

    def test_pid_is_valid_pdf_request_empty_file_path(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        request = u''

        self.assertEqual(ac._is_valid_pdf_request(request), None)

    def test_pid_is_valid_pdf_request_invalid_request_not_allowed_acronym(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        request = u'GET http://www.scielo.br/pdf/not_allowed_acronym/v96n2/a18v96n2.xxx HTTP/1.1'

        self.assertEqual(ac._is_valid_pdf_request(request), None)

    def test_parsed_access_valid_html_access(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        line = '187.19.211.179 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/scielo.php?pid=S1234-43212000000300007&script=sci_arttext HTTP/1.1" 200 25084 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'

        expected = {
                        'ip': '187.19.211.179',
                        'code': 'S1234-43212000000300007',
                        'access_type': 'HTML',
                        'iso_date': '2013-05-30',
                        'iso_datetime': '2013-05-30T00:01:01',
                        'year': '2013',
                        'query_string': {
                            'pid': 'S1234-43212000000300007',
                            'script': 'sci_arttext'
                        }, 
                        'day': '30',
                        'script': 'sci_arttext',
                        'month': '05'
                    }
        self.assertEqual(ac.parsed_access(line), expected)

    def test_parsed_access_invalid_article_access_without_script(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        line = '187.19.211.179 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/scielo.php?pid=S1234-43212000000300007 HTTP/1.1" 200 25084 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'

        self.assertEqual(ac.parsed_access(line), None)

    def test_parsed_access_invalid_article_access_without_pid(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        line = '187.19.211.179 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/scielo.php?script=sci_arttext HTTP/1.1" 200 25084 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'

        self.assertEqual(ac.parsed_access(line), None)

    def test_parsed_access_invalid_article_access_without_query_string(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        line = '187.19.211.179 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/scielo.php HTTP/1.1" 200 25084 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'

        self.assertEqual(ac.parsed_access(line), None)

    def test_parsed_access_valid_pdf_access(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        line = '201.14.120.2 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/pdf/bjmbr/v14n4/03.pdf HTTP/1.1" 206 4608 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'

        expected = {
                        'ip': '201.14.120.2',
                        'code': '/pdf/bjmbr/v14n4/03.pdf',
                        'access_type': 'PDF',
                        'iso_date': '2013-05-30',
                        'iso_datetime': '2013-05-30T00:01:01',
                        'year': '2013',
                        'day': '30',
                        'month': '05',
                        'query_string': None,
                        'pdf_issn': u'1234-4321',
                        'script': '',
                        'pdf_path': '/pdf/bjmbr/v14n4/03.pdf'
                    }

        self.assertEqual(ac.parsed_access(line), expected)

    def test_parsed_access_valid_pdf_with_not_allowed_acronym(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        line = '201.14.120.2 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/pdf/not_allowed_acronym/v14n4/03.pdf HTTP/1.1" 206 4608 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'

        self.assertEqual(ac.parsed_access(line), None)

    def test_parsed_access_valid_pdf_with_any_different_access(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'bjmbr': u'1234-4321', u'zool': u'1984-4670'})
        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        line = '177.191.212.233 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/img/pt/author.gif HTTP/1.1" 304 0 "http://www.scielo.br/scielo.php?script=sci_serial&pid=1415-4757&nrm=iso&rep=&lng=pt" "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36"'

        self.assertEqual(ac.parsed_access(line), None)



















# coding: utf-8

import urllib2
import datetime

from mocker import ANY, MockerTestCase

from logger.accesschecker import AccessChecker, TimedSet, checkdatelock
from logger.ratchet import RatchetQueue
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


class AccessQueueTests(MockerTestCase):

    def test_instanciating_accessqueue_without_logfile(self):

        rq = RatchetQueue('localhost:8000')

        expected = '%s_error.log' % datetime.datetime.today().isoformat()[0:10]

        self.assertEqual(rq._error_log_file.name, expected)

    def test_instanciating_accessqueue_logfile(self):

        rq = RatchetQueue('localhost:8000', error_log_file='test.log')

        self.assertEqual(rq._error_log_file.name, 'test.log')


class AccessCheckerTests(MockerTestCase):

    def test_instanciatingAccessChecker(self):
        mock_urllib2 = self.mocker.replace("urllib2")

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.collections)

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.journals)

        self.mocker.replay()

        self.assertTrue(isinstance(AccessChecker(collection='scl'), AccessChecker))

    def test_instanciatingAccessChecker_with_invalid_collection(self):
        mock_urllib2 = self.mocker.replace("urllib2")

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.collections)

        self.mocker.replay()

        with self.assertRaises(ValueError):
            AccessChecker(collection='xxx')

    def test_instanciatingAccessChecker_allowed_collections(self):
        mock_urllib2 = self.mocker.replace("urllib2")

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.collections)

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.journals)

        self.mocker.replay()

        self.assertEqual(AccessChecker(collection='scl').collection, 'scl')

    def test_instanciatingAccessChecker_not_allowed_collections(self):
        mock_urllib2 = self.mocker.replace("urllib2")

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.collections)

        self.mocker.replay()

        with self.assertRaises(ValueError):
            AccessChecker(collection='xxx')

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
        self.mocker.result(fixtures.collections)

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.journals)

        self.mocker.replay()

        self.assertEqual(AccessChecker(collection='scl').acronym_to_issn_dict, {u'bjmbr': u'0100-879X', u'zool': u'1984-4670'})

    def test_instanciatingAccessChecker_acronym_to_issn_dict_exception(self):
        mock_urllib2 = self.mocker.replace("urllib2")

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.collections)

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.throw(urllib2.URLError(u'Was not possible to connect to webservices.scielo.org, try again later!'))

        self.mocker.replay()

        with self.assertRaises(urllib2.URLError):
            AccessChecker(collection='scl')

    def test_instanciatingAccessChecker_allowed_issn(self):
        mock_urllib2 = self.mocker.replace("urllib2")

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.collections)

        mock_urllib2.urlopen(ANY, timeout=3).read()
        self.mocker.result(fixtures.journals)

        self.mocker.replay()

        self.assertEqual(AccessChecker(collection='scl').allowed_issns, [u'1984-4670', u'0100-879X'])

    def test_is_bot_GoogleBot_sample(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        line = '66.249.75.131 - - [24/Dec/2013:04:49:09 -0200] "GET http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0102-79722002000200013 HTTP/1.1" 200 102967 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"'
        
        self.assertEqual(ac.parsed_access(line), None)

    def test_is_bot_Bing_sample(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        line = '13245  157.56.92.164 - - [30/Nov/2013:03:53:26 -0200] "GET http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0104-87752010000200013 HTTP/1.1" 200 108777 "-" "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"'
        
        self.assertEqual(ac.parsed_access(line), None)

    def test_is_bot_Spider_sample(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        line = '180.76.5.118 - - [24/Dec/2013:04:49:09 -0200] "GET http://www.scielo.br/pdf/csc/v11n2/30434.pdf HTTP/1.1" 200 79618 "-" "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)"'
        
        self.assertEqual(ac.parsed_access(line), None)

    def test_is_bot_method_with_bot_agent(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        agent = '"Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)"'

        self.assertEqual(ac.is_robot(agent), True)

    def test_is_bot_method_with_common_user_agent(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        agent = '"Mozilla/5.0 (Windows NT 5.1; rv:26.0) Gecko/20100101 Firefox/26.0"'

        self.assertEqual(ac.is_robot(agent), False)

    def test_pdf_or_html_access_for_html(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result(['scl', 'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})
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
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

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
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

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
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

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
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        line = ''

        self.assertEqual(ac._parse_line(line), None)

    def test_access_date(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        access_date = u'[30/Dec/2012:23:59:57 -0200]'

        self.assertEqual(ac._access_date(access_date).date().isoformat(), u'2012-12-30')

    def test_access_datetime(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        access_date = u'[30/Dec/2012:23:59:57 -0200]'

        self.assertEqual(ac._access_date(access_date).isoformat(), u'2012-12-30T23:59:57')

    def test_access_date_with_invalid_month(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        access_date = u'[30/xxx/2012:23:59:57 -0200]'

        self.assertEqual(ac._access_date(access_date), None)

    def test_access_date_with_invalid_day(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        access_date = u'[xx/Dec/2012:23:59:57 -0200]'

        self.assertEqual(ac._access_date(access_date), None)

    def test_access_date_with_invalid_year(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        access_date = u'[12/Dec/x012:23:59:57 -0200]'

        self.assertEqual(ac._access_date(access_date), None)

    def test_access_date_with_invalid_date(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        access_date = u''

        self.assertEqual(ac._access_date(access_date), None)

    def test_query_string_with_parameters(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

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
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        url = u'GET http://www.scielo.br/scielo.php HTTP/1.1'

        self.assertEqual(ac._query_string(url), None)

    def test_pid_is_valid_not_allowed_issn(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        self.assertEqual(ac._is_valid_html_request('sci_arttext', 'XXXX-XXXX2012000100001'), False)

    def test_pid_is_valid_script_sci_arttext_invalid_pid(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        self.assertEqual(ac._is_valid_html_request('sci_arttext', '123443212012000100001'), False)

    def test_pid_is_valid_script_sci_arttext_valid_pid(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        self.assertEqual(ac._is_valid_html_request('sci_arttext', '1414-431X2012000100001'), True)

    def test_pid_is_valid_script_sci_arttext_valid_pid_fbpe(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        self.assertEqual(ac._is_valid_html_request('sci_arttext', '1414-431X(12)00100001'), True)

    def test_pid_is_valid_script_sci_abstract_invalid_pid(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        self.assertEqual(ac._is_valid_html_request('sci_abstract', '1414-431X201200100001'), False)

    def test_pid_is_valid_script_sci_abstract_valid_pid(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        self.assertEqual(ac._is_valid_html_request('sci_abstract', '1414-431X2012000100001'), True)

    def test_pid_is_valid_script_sci_abstract_valid_pid_fbpe(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        self.assertEqual(ac._is_valid_html_request('sci_abstract', '1414-431X(12)00100001'), True)

    def test_pid_is_valid_script_sci_pdf_invalid_pid(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        self.assertEqual(ac._is_valid_html_request('sci_pdf', '1414-431X9012000100001'), False)

    def test_pid_is_valid_script_sci_pdf_valid_pid(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        self.assertEqual(ac._is_valid_html_request('sci_pdf', '1414-431X2012000100001'), True)

    def test_pid_is_valid_script_sci_pdf_valid_pid_fbpe(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        self.assertEqual(ac._is_valid_html_request('sci_pdf', '1414-431X(12)00100001'), True)

    def test_pid_is_valid_script_sci_serial_valid_pid(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        self.assertEqual(ac._is_valid_html_request('sci_serial', '1414-431X'), True)

    def test_pid_is_valid_script_sci_issuetoc_valid_pid(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        self.assertEqual(ac._is_valid_html_request('sci_issuetoc', '1414-431X20120001'), True)

    def test_pid_is_valid_script_sci_issuetoc_invalid_pid(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        self.assertEqual(ac._is_valid_html_request('sci_issuetoc', '1234432120120001'), False)

    def test_pid_is_valid_script_sci_issues_valid_pid(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')
        self.assertEqual(ac._is_valid_html_request('sci_issues', '1414-431X'), True)

    def test_pid_is_valid_pdf_request(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        request = u'GET http://www.scielo.br/pdf/zool/v96n2/a18v96n2.pdf HTTP/1.1'

        self.assertEqual(ac._is_valid_pdf_request(request), {'pdf_issn': u'1984-4670', 'pdf_path': u'/pdf/zool/v96n2/a18v96n2.pdf'})

    def test_pid_is_valid_pdf_request_GET_without_domain(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        request = u'GET /pdf/zool/v29n4/18781.pdf HTTP/1.1'

        self.assertEqual(ac._is_valid_pdf_request(request), {'pdf_issn': u'1984-4670', 'pdf_path': u'/pdf/zool/v29n4/18781.pdf'})

    def test_pid_is_valid_pdf_request_empty_file_path(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        request = u''

        self.assertEqual(ac._is_valid_pdf_request(request), None)

    def test_pid_is_valid_pdf_request_invalid_request_not_allowed_acronym(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        request = u'GET http://www.scielo.br/pdf/not_allowed_acronym/v96n2/a18v96n2.xxx HTTP/1.1'

        self.assertEqual(ac._is_valid_pdf_request(request), None)

    def test_parsed_access_valid_html_access(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        line = '187.19.211.179 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/scielo.php?pid=S1414-431X2000000300007&script=sci_arttext HTTP/1.1" 200 25084 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'

        expected = {
                        'ip': '187.19.211.179',
                        'code': 'S1414-431X2000000300007',
                        'access_type': 'HTML',
                        'iso_date': '2013-05-30',
                        'iso_datetime': '2013-05-30T00:01:01',
                        'year': '2013',
                        'query_string': {
                            'pid': 'S1414-431X2000000300007',
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
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        line = '187.19.211.179 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/scielo.php?pid=S1414-431X2000000300007 HTTP/1.1" 200 25084 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'

        self.assertEqual(ac.parsed_access(line), None)

    def test_parsed_access_invalid_article_access_without_pid(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        line = '187.19.211.179 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/scielo.php?script=sci_arttext HTTP/1.1" 200 25084 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'

        self.assertEqual(ac.parsed_access(line), None)

    def test_parsed_access_invalid_article_access_without_query_string(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        line = '187.19.211.179 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/scielo.php HTTP/1.1" 200 25084 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'

        self.assertEqual(ac.parsed_access(line), None)

    def test_parsed_access_valid_pdf_access_GET_string_without_domain(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        line = '66.249.73.80 - - [30/May/2013:00:01:01 -0300] "GET /pdf/bjmbr/v29n4/18781.pdf HTTP/1.1" 200 32061 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'

        expected = {
                        'ip': '66.249.73.80',
                        'code': '/pdf/bjmbr/v29n4/18781.pdf',
                        'access_type': 'PDF',
                        'iso_date': '2013-05-30',
                        'iso_datetime': '2013-05-30T00:01:01',
                        'year': '2013',
                        'day': '30',
                        'month': '05',
                        'query_string': None,
                        'pdf_issn': u'1414-431X',
                        'script': '',
                        'pdf_path': '/pdf/bjmbr/v29n4/18781.pdf'
                    }

        self.assertEqual(ac.parsed_access(line), expected)


    def test_parsed_access_valid_pdf_access(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

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
                        'pdf_issn': u'1414-431X',
                        'script': '',
                        'pdf_path': '/pdf/bjmbr/v14n4/03.pdf'
                    }

        self.assertEqual(ac.parsed_access(line), expected)

    def test_parsed_access_valid_pdf_with_not_allowed_acronym(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        line = '201.14.120.2 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/pdf/not_allowed_acronym/v14n4/03.pdf HTTP/1.1" 206 4608 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'

        self.assertEqual(ac.parsed_access(line), None)

    def test_parsed_access_valid_pdf_with_any_different_access(self):
        accesschecker = self.mocker.patch(AccessChecker)
        accesschecker._allowed_collections()
        self.mocker.result([u'scl', u'arg'])
        accesschecker._acronym_to_issn_dict()
        self.mocker.result({u'zool': u'1984-4670', u'bjmbr': u'1414-431X'})

        self.mocker.replay()

        ac = AccessChecker(collection='scl')

        line = '177.191.212.233 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/img/pt/author.gif HTTP/1.1" 304 0 "http://www.scielo.br/scielo.php?script=sci_serial&pid=1415-4757&nrm=iso&rep=&lng=pt" "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36"'

        self.assertEqual(ac.parsed_access(line), None)



















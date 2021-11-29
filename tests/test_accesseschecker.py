# coding: utf-8
import unittest

from logger.accesschecker import AccessChecker


class AccessCheckerTests(unittest.TestCase):
    def setUp(self):
        self.ac = AccessChecker(
            collection="scl", 
            allowed_collections=lambda: [u"scl", u"arg"],
            acronym_to_issn_dict=lambda col: {u'zool': u'1984-4670', u'bjmbr': u'1414-431X'},
        )


    def test_GoogleBot_bot_is_not_parsed(self):
        line = '66.249.75.131 - - [24/Dec/2013:04:49:09 -0200] "GET http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0102-79722002000200013 HTTP/1.1" 200 102967 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"'
        self.assertEqual(self.ac.parsed_access(line), None)

    def test_Bing_bot_is_not_parsed(self):
        line = '13245  157.56.92.164 - - [30/Nov/2013:03:53:26 -0200] "GET http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0104-87752010000200013 HTTP/1.1" 200 108777 "-" "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"'
        self.assertEqual(self.ac.parsed_access(line), None)

    def test_Spider_bot_sample(self):
        line = '180.76.5.118 - - [24/Dec/2013:04:49:09 -0200] "GET http://www.scielo.br/pdf/csc/v11n2/30434.pdf HTTP/1.1" 200 79618 "-" "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)"'
        self.assertEqual(self.ac.parsed_access(line), None)

    def test_is_robot_detects_bot_useragent(self):
        agent = '"Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)"'
        self.assertEqual(self.ac.is_robot(agent), True)

    def test_is_robot_detects_mozilla_useragent(self):
        agent = '"Mozilla/5.0 (Windows NT 5.1; rv:26.0) Gecko/20100101 Firefox/26.0"'
        self.assertEqual(self.ac.is_robot(agent), False)

    def test_pdf_or_html_access_identifies_urls_of_documents_in_html_v1(self):
        request = u'GET http://www.scielo.br/article/abcd/2018.v31n3/e1382/pt/ HTTP/1.1'
        self.assertEqual(self.ac._pdf_or_html_access(request), u'HTML')

        request = u'GET /article/abcd/2018.v31n3/e1382/pt/ HTTP/1.1'
        self.assertEqual(self.ac._pdf_or_html_access(request), u'HTML')

    def test_pdf_or_html_access_identifies_urls_of_documents_in_html_v2(self):
        request = u'GET http://www.scielo.br/j/abdc/a/MYJY5Rgw5gc7mBpqYzBCVJR HTTP/1.1'
        self.assertEqual(self.ac._pdf_or_html_access(request), u'HTML')

        request = u'GET /j/abdc/a/MYJY5Rgw5gc7mBpqYzBCVJR HTTP/1.1'
        self.assertEqual(self.ac._pdf_or_html_access(request), u'HTML')

    def test_pdf_or_html_access_identifies_urls_of_documents_in_html_v3(self):
        request = u'GET http://www.scielo.br/j/abdc/a/MYJY5Rgw5gc7mBpqYzBCVJR?format=html HTTP/1.1'
        self.assertEqual(self.ac._pdf_or_html_access(request), u'HTML')

        request = u'GET /j/abdc/a/MYJY5Rgw5gc7mBpqYzBCVJR?format=html HTTP/1.1'
        self.assertEqual(self.ac._pdf_or_html_access(request), u'HTML')

    def test_pdf_or_html_access_identifies_urls_of_documents_in_html_v4(self):
        request = u'GET http://www.scielo.br/scielo.php?pid=S0100-736X2000000300007&script=sci_arttext HTTP/1.1'
        self.assertEqual(self.ac._pdf_or_html_access(request), u'HTML')

        request = u'GET /scielo.php?pid=S0100-736X2000000300007&script=sci_arttext HTTP/1.1'
        self.assertEqual(self.ac._pdf_or_html_access(request), u'HTML')

    def test_pdf_or_html_access_identifies_urls_of_documents_in_pdf_v1(self):
        request = u'GET https://www.scielo.br/pdf/abcd/2018.v31n3/e1382/en HTTP/1.1'
        self.assertEqual(self.ac._pdf_or_html_access(request), u'PDF')

        request = u'GET /pdf/abcd/2018.v31n3/e1382/en HTTP/1.1'
        self.assertEqual(self.ac._pdf_or_html_access(request), u'PDF')

    def test_pdf_or_html_access_identifies_urls_of_documents_in_pdf_v2(self):
        request = u'GET http://www.scielo.br/pdf/isz/v96n2/a18v96n2.pdf HTTP/1.1'
        self.assertEqual(self.ac._pdf_or_html_access(request), u'PDF')

        request = u'GET /pdf/isz/v96n2/a18v96n2.pdf HTTP/1.1'
        self.assertEqual(self.ac._pdf_or_html_access(request), u'PDF')

    def test_pdf_or_html_access_identifies_urls_of_documents_in_pdf_v3(self):
        request = u'GET http://www.scielo.br/j/abdc/a/MYJY5Rgw5gc7mBpqYzBCVJR?format=pdf HTTP/1.1'
        self.assertEqual(self.ac._pdf_or_html_access(request), u'PDF')

        request = u'GET /j/abdc/a/MYJY5Rgw5gc7mBpqYzBCVJR?format=pdf HTTP/1.1'
        self.assertEqual(self.ac._pdf_or_html_access(request), u'PDF')

    def test_pdf_or_html_access_for_files_on_new_site(self):
        request = u'GET http://www.scielo.br/static/img/favicon.ico HTTP/1.1'
        self.assertEqual(self.ac._pdf_or_html_access(request), None)

        request = u'GET /static/img/favicon.ico HTTP/1.1'
        self.assertEqual(self.ac._pdf_or_html_access(request), None)

    def test_pdf_or_html_access_for_files(self):
        request = u'GET http://www.scielo.br/css/screen/styles.css HTTP/1.1'
        self.assertEqual(self.ac._pdf_or_html_access(request), None)

        request = u'GET /css/screen/styles.css HTTP/1.1'
        self.assertEqual(self.ac._pdf_or_html_access(request), None)

    def test_parse_line_with_apache_line(self):
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

        self.assertEqual(self.ac._parse_line(line), expected)

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

        self.assertEqual(self.ac._parse_line(line), expected)

    def test_parse_line_invalid_line(self):
        self.assertEqual(self.ac._parse_line(''), None)

    def test_access_date(self):
        access_date = u'[30/Dec/2012:23:59:57 -0200]'
        self.assertEqual(self.ac._access_date(access_date).date().isoformat(), u'2012-12-30')

    def test_access_datetime(self):
        access_date = u'[30/Dec/2012:23:59:57 -0200]'
        self.assertEqual(self.ac._access_date(access_date).isoformat(), u'2012-12-30T23:59:57')

    def test_access_date_with_invalid_month(self):
        access_date = u'[30/xxx/2012:23:59:57 -0200]'
        self.assertEqual(self.ac._access_date(access_date), None)

    def test_access_date_with_invalid_day(self):
        access_date = u'[xx/Dec/2012:23:59:57 -0200]'
        self.assertEqual(self.ac._access_date(access_date), None)

    def test_access_date_with_invalid_year(self):
        access_date = u'[12/Dec/x012:23:59:57 -0200]'
        self.assertEqual(self.ac._access_date(access_date), None)

    def test_access_date_with_invalid_date(self):
        self.assertEqual(self.ac._access_date(u''), None)

    def test_query_string_with_parameters(self):
        url = u'GET http://www.scielo.br/scielo.php?pid=S0100-736X2000000300007&script=sci_arttext HTTP/1.1'
        self.assertEqual(self.ac._query_string(url), {u'pid': u'S0100-736X2000000300007', u'script': u'sci_arttext'})

        url = u'GET /scielo.php?pid=S0100-736X2000000300007&script=sci_arttext HTTP/1.1'
        self.assertEqual(self.ac._query_string(url), {u'pid': u'S0100-736X2000000300007', u'script': u'sci_arttext'})

    def test_query_string_without_parameters(self):
        url = u'GET http://www.scielo.br/scielo.php HTTP/1.1'
        self.assertEqual(self.ac._query_string(url), None)

    def test_pid_is_valid_not_allowed_issn(self):
        self.assertEqual(self.ac._is_valid_html_request('sci_arttext', 'XXXX-XXXX2012000100001'), False)

    def test_pid_is_valid_script_sci_arttext_invalid_pid(self):
        self.assertEqual(self.ac._is_valid_html_request('sci_arttext', '123443212012000100001'), False)

    def test_pid_is_valid_script_sci_arttext_valid_pid(self):
        self.assertEqual(self.ac._is_valid_html_request('sci_arttext', '1414-431X2012000100001'), True)

    def test_pid_is_valid_script_sci_arttext_valid_pid_fbpe(self):
        self.assertEqual(self.ac._is_valid_html_request('sci_arttext', '1414-431X(12)00100001'), True)

    def test_pid_is_valid_script_sci_abstract_invalid_pid(self):
        self.assertEqual(self.ac._is_valid_html_request('sci_abstract', '1414-431X201200100001'), False)

    def test_pid_is_valid_script_sci_abstract_valid_pid(self):
        self.assertEqual(self.ac._is_valid_html_request('sci_abstract', '1414-431X2012000100001'), True)

    def test_pid_is_valid_script_sci_abstract_valid_pid_fbpe(self):
        self.assertEqual(self.ac._is_valid_html_request('sci_abstract', '1414-431X(12)00100001'), True)

    def test_pid_is_valid_script_sci_pdf_invalid_pid(self):
        self.assertEqual(self.ac._is_valid_html_request('sci_pdf', '1414-431X9012000100001'), False)

    def test_pid_is_valid_script_sci_pdf_valid_pid(self):
        self.assertEqual(self.ac._is_valid_html_request('sci_pdf', '1414-431X2012000100001'), True)

    def test_pid_is_valid_script_sci_pdf_valid_pid_fbpe(self):
        self.assertEqual(self.ac._is_valid_html_request('sci_pdf', '1414-431X(12)00100001'), True)

    def test_pid_is_valid_script_sci_serial_valid_pid(self):
        self.assertEqual(self.ac._is_valid_html_request('sci_serial', '1414-431X'), True)

    def test_pid_is_valid_script_sci_issuetoc_valid_pid(self):
        self.assertEqual(self.ac._is_valid_html_request('sci_issuetoc', '1414-431X20120001'), True)

    def test_pid_is_valid_script_sci_issuetoc_invalid_pid(self):
        self.assertEqual(self.ac._is_valid_html_request('sci_issuetoc', '1234432120120001'), False)

    def test_pid_is_valid_script_sci_issues_valid_pid(self):
        self.assertEqual(self.ac._is_valid_html_request('sci_issues', '1414-431X'), True)

    def test_pid_is_valid_pdf_request(self):
        request = u'GET http://www.scielo.br/pdf/zool/v96n2/a18v96n2.pdf HTTP/1.1'
        self.assertEqual(self.ac._is_valid_pdf_request(request), {'pdf_issn': u'1984-4670', 'pdf_path': u'/pdf/zool/v96n2/a18v96n2.pdf'})

    def test_pid_is_valid_pdf_request_GET_without_domain(self):
        request = u'GET /pdf/zool/v29n4/18781.pdf HTTP/1.1'
        self.assertEqual(self.ac._is_valid_pdf_request(request), {'pdf_issn': u'1984-4670', 'pdf_path': u'/pdf/zool/v29n4/18781.pdf'})

    def test_pid_is_valid_pdf_request_new_site(self):
        request = u'GET https://www.scielo.br/pdf/bjmbr/2018.v51n11/e7704/en HTTP/1.1'
        self.assertEqual(self.ac._is_valid_pdf_request(request), {'pdf_issn': u'1414-431X', 'pdf_path': u'/pdf/bjmbr/2018.v51n11/e7704/'})

    def test_pid_is_valid_pdf_request_GET_without_domain_new_site(self):
        request = u'GET /pdf/bjmbr/2018.v51n11/e7704/en HTTP/1.1'
        self.assertEqual(self.ac._is_valid_pdf_request(request), {'pdf_issn': u'1414-431X', 'pdf_path': u'/pdf/bjmbr/2018.v51n11/e7704/'})

    def test_pid_is_valid_pdf_request_empty_file_path(self):
        self.assertEqual(self.ac._is_valid_pdf_request(u''), None)

    def test_pid_is_valid_pdf_request_invalid_request_not_allowed_acronym(self):
        request = u'GET http://www.scielo.br/pdf/not_allowed_acronym/v96n2/a18v96n2.xxx HTTP/1.1'
        self.assertEqual(self.ac._is_valid_pdf_request(request), None)


class OPACURLParsingTests(unittest.TestCase):
    def setUp(self):
        self.ac = AccessChecker(
            collection="scl", 
            allowed_collections=lambda: [u"scl", u"arg"],
            acronym_to_issn_dict=lambda col: {u'zool': u'1984-4670', u'bjmbr': u'1414-431X'},
        )

    def test_document_url_v1(self):
        """URL de artigo em HTML no padrão do novo site. Este padrão já foi
        suplantado, mas podem haver instâncias que o utilizam. 
        """
        line = '187.19.211.179 - - [30/May/2013:00:01:01 -0300] "GET https://www.scielo.br/article/bjmbr/2018.v51n11/e7704/en/ HTTP/1.1" 200 25084 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'

        expected = {
                        'ip': '187.19.211.179',
                        'code': '/article/bjmbr/2018.v51n11/e7704/',
                        'access_type': 'HTML',
                        'iso_date': '2013-05-30',
                        'iso_datetime': '2013-05-30T00:01:01',
                        'year': '2013',
                        'query_string': None,
                        'day': '30',
                        'http_code': '200',
                        'original_agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
                        'original_date': '[30/May/2013:00:01:01 -0300]',
                        'script': '',
                        'month': '05'
                    }

        self.assertEqual(self.ac.parsed_access(line), expected)

    def test_document_url_v2(self):
        """URL de artigo em HTML no padrão do novo site.
        """
        line = '187.19.211.179 - - [30/May/2013:00:01:01 -0300] "GET https://www.scielo.br/j/bjmbr/a/F5Zr9TrzfmMgz9kvGZL3rZB HTTP/1.1" 200 25084 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'

        expected = {
                        'ip': '187.19.211.179',
                        'code': 'F5Zr9TrzfmMgz9kvGZL3rZB',
                        'access_type': 'HTML',
                        'iso_date': '2013-05-30',
                        'iso_datetime': '2013-05-30T00:01:01',
                        'year': '2013',
                        'query_string': None,
                        'day': '30',
                        'http_code': '200',
                        'original_agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
                        'original_date': '[30/May/2013:00:01:01 -0300]',
                        'script': '',
                        'month': '05'
                    }

        self.assertEqual(self.ac.parsed_access(line), expected)

    def test_document_url_v3(self):
        """URL de artigo em HTML no padrão do novo site.
        """
        line = '187.19.211.179 - - [30/May/2013:00:01:01 -0300] "GET https://www.scielo.br/j/bjmbr/a/F5Zr9TrzfmMgz9kvGZL3rZB?format=html HTTP/1.1" 200 25084 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'

        expected = {
                        'ip': '187.19.211.179',
                        'code': 'F5Zr9TrzfmMgz9kvGZL3rZB',
                        'access_type': 'HTML',
                        'iso_date': '2013-05-30',
                        'iso_datetime': '2013-05-30T00:01:01',
                        'year': '2013',
                        'query_string': {"format": "html"},
                        'day': '30',
                        'http_code': '200',
                        'original_agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
                        'original_date': '[30/May/2013:00:01:01 -0300]',
                        'script': '',
                        'month': '05'
                    }

        self.assertEqual(self.ac.parsed_access(line), expected)

    def test_document_relative_url(self):
        """URL de artigo em HTML no padrão do novo site. Trata-se da mesma URL
        do caso `test_document_url` mas com a URL relativa e não absoluta.
        """
        line = '187.19.211.179 - - [30/May/2013:00:01:01 -0300] "GET /article/bjmbr/2018.v51n11/e7704/en/ HTTP/1.1" 200 25084 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'

        expected = {
                        'ip': '187.19.211.179',
                        'code': '/article/bjmbr/2018.v51n11/e7704/',
                        'access_type': 'HTML',
                        'iso_date': '2013-05-30',
                        'iso_datetime': '2013-05-30T00:01:01',
                        'year': '2013',
                        'query_string': None,
                        'day': '30',
                        'http_code': '200',
                        'original_agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
                        'original_date': '[30/May/2013:00:01:01 -0300]',
                        'script': '',
                        'month': '05'
                    }
        self.assertEqual(self.ac.parsed_access(line), expected)

    def test_pdf_url_v1(self):
        """URL de artigo em PDF no padrão do novo site. Este padrão já foi
        suplantado, mas podem haver instâncias que o utilizam. 
        """
        line = '201.14.120.2 - - [30/May/2013:00:01:01 -0300] "GET https://www.scielo.br/pdf/bjmbr/2018.v51n11/e7704/en HTTP/1.1" 200 4608 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'
        expected = {
                        'ip': '201.14.120.2',
                        'code': '/pdf/bjmbr/2018.v51n11/e7704/',
                        'access_type': 'PDF',
                        'iso_date': '2013-05-30',
                        'iso_datetime': '2013-05-30T00:01:01',
                        'year': '2013',
                        'day': '30',
                        'month': '05',
                        'http_code': '200',
                        'original_agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
                        'original_date': '[30/May/2013:00:01:01 -0300]',
                        'query_string': None,
                        'pdf_issn': u'1414-431X',
                        'script': '',
                        'pdf_path': '/pdf/bjmbr/2018.v51n11/e7704/'
                    }
        self.assertEqual(self.ac.parsed_access(line), expected)

    def test_pdf_url_v2(self):
        """URL de artigo em HTML no padrão do novo site.
        """
        line = '187.19.211.179 - - [30/May/2013:00:01:01 -0300] "GET https://www.scielo.br/j/bjmbr/a/F5Zr9TrzfmMgz9kvGZL3rZB?format=pdf HTTP/1.1" 200 25084 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'

        expected = {
                        'ip': '187.19.211.179',
                        'code': 'F5Zr9TrzfmMgz9kvGZL3rZB_pdf',
                        'access_type': 'PDF',
                        'iso_date': '2013-05-30',
                        'iso_datetime': '2013-05-30T00:01:01',
                        'year': '2013',
                        'query_string': {"format": "pdf"},
                        'day': '30',
                        'http_code': '200',
                        'original_agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
                        'original_date': '[30/May/2013:00:01:01 -0300]',
                        'script': '',
                        'month': '05'
                    }

        self.assertEqual(self.ac.parsed_access(line), expected)

    def test_pdf_relative_url_v1(self):
        """URL de artigo em PDF no padrão do novo site. Trata-se da mesma URL
        do caso `test_pdf_url` mas com a URL relativa e não absoluta.
        """
        line = '201.14.120.2 - - [30/May/2013:00:01:01 -0300] "GET /pdf/bjmbr/2018.v51n11/e7704/en HTTP/1.1" 200 4608 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'
        expected = {
                        'ip': '201.14.120.2',
                        'code': '/pdf/bjmbr/2018.v51n11/e7704/',
                        'access_type': 'PDF',
                        'iso_date': '2013-05-30',
                        'iso_datetime': '2013-05-30T00:01:01',
                        'year': '2013',
                        'day': '30',
                        'month': '05',
                        'http_code': '200',
                        'original_agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
                        'original_date': '[30/May/2013:00:01:01 -0300]',
                        'query_string': None,
                        'pdf_issn': u'1414-431X',
                        'script': '',
                        'pdf_path': '/pdf/bjmbr/2018.v51n11/e7704/'
                    }
        self.assertEqual(self.ac.parsed_access(line), expected)


class ClassicSiteURLParsingTests(unittest.TestCase):
    def setUp(self):
        self.ac = AccessChecker(
            collection="scl", 
            allowed_collections=lambda: [u"scl", u"arg"],
            acronym_to_issn_dict=lambda col: {u'zool': u'1984-4670', u'bjmbr': u'1414-431X'},
        )

    def test_404_responses_must_return_None(self):
        line = '187.19.211.179 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/scielo.php?pid=S1414-431X2000000300007&script=sci_arttext HTTP/1.1" 404 25084 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'
        self.assertEqual(self.ac.parsed_access(line), None)

    def test_site_assets_must_return_None(self):
        line = '177.191.212.233 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/img/pt/author.gif HTTP/1.1" 304 0 "http://www.scielo.br/scielo.php?script=sci_serial&pid=1415-4757&nrm=iso&rep=&lng=pt" "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36"'
        self.assertEqual(self.ac.parsed_access(line), None)

    def test_document_url(self):
        """URL de artigo em HTML no padrão do site clássico.
        """
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
                        'http_code': '200',
                        'original_agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
                        'original_date': '[30/May/2013:00:01:01 -0300]',
                        'script': 'sci_arttext',
                        'month': '05'
                    }

        self.assertEqual(self.ac.parsed_access(line), expected)

    def test_document_url_missing_script(self):
        line = '187.19.211.179 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/scielo.php?pid=S1414-431X2000000300007 HTTP/1.1" 200 25084 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'
        self.assertEqual(self.ac.parsed_access(line), None)

    def test_document_url_missing_pid(self):
        line = '187.19.211.179 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/scielo.php?script=sci_arttext HTTP/1.1" 200 25084 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'
        self.assertEqual(self.ac.parsed_access(line), None)

    def test_main_module_without_querystring(self):
        line = '187.19.211.179 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/scielo.php HTTP/1.1" 200 25084 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'
        self.assertEqual(self.ac.parsed_access(line), None)

    def test_document_pdf_relative_url(self):
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
                        'http_code': '200',
                        'original_agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
                        'original_date': '[30/May/2013:00:01:01 -0300]',
                        'query_string': None,
                        'pdf_issn': u'1414-431X',
                        'script': '',
                        'pdf_path': '/pdf/bjmbr/v29n4/18781.pdf'
                    }
        self.assertEqual(self.ac.parsed_access(line), expected)

    def test_document_pdf_url(self):
        line = '201.14.120.2 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/pdf/bjmbr/v14n4/03.pdf HTTP/1.1" 200 4608 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'
        expected = {
                        'ip': '201.14.120.2',
                        'code': '/pdf/bjmbr/v14n4/03.pdf',
                        'access_type': 'PDF',
                        'iso_date': '2013-05-30',
                        'iso_datetime': '2013-05-30T00:01:01',
                        'year': '2013',
                        'day': '30',
                        'month': '05',
                        'http_code': '200',
                        'original_agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
                        'original_date': '[30/May/2013:00:01:01 -0300]',
                        'query_string': None,
                        'pdf_issn': u'1414-431X',
                        'script': '',
                        'pdf_path': '/pdf/bjmbr/v14n4/03.pdf'
                    }
        self.assertEqual(self.ac.parsed_access(line), expected)

    def test_document_pdf_url_v2(self):
        line = '201.14.120.2 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/scielo.php?pid=S0044-59672020000100012&script=sci_pdf&tlng=en HTTP/1.1" 200 4608 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'
        self.assertEqual(self.ac.parsed_access(line), None)

    def test_journal_homepage(self):
        line = '201.14.120.2 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/scielo.php?script=sci_serial&pid=0100-879X&lng=en&nrm=iso HTTP/1.1" 200 4608 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'
        self.assertEqual(self.ac.parsed_access(line), None)

    def test_document_pdf_with_unknown_journal_acronym(self):
        line = '201.14.120.2 - - [30/May/2013:00:01:01 -0300] "GET http://www.scielo.br/pdf/not_allowed_acronym/v14n4/03.pdf HTTP/1.1" 200 4608 "-" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"'
        self.assertEqual(self.ac.parsed_access(line), None)


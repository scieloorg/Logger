import unittest
from mock import patch, ANY

from logger import ratchet


class RatchetBulkTests(unittest.TestCase):

    def setUp(self):

        self.rb = ratchet.Local('fakeapiuri', 'scl')

    @patch("logger.ratchet.pid_v3_to_pid_v2")
    @patch("logger.ratchet.Local.register_html_accesses")
    def test_register_access_for_new_website_pdf(self, mock_register_html_accesses, mock_v3_to_v2):
        parsed_line = {
            'ip': '187.19.211.179',
            'code': 'F5Zr9TrzfmMgz9kvGZL3rZB',
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
            'page_v3': 'pdf',
            'month': '05'
        }
        mock_v3_to_v2.return_value = "S1519-38292013000200004"
        self.rb.register_access(parsed_line)
        mock_register_html_accesses.assert_called_once_with(
            'pdf',
            ANY,
            '2013-05-30',
            '187.19.211.179',
        )

    @patch("logger.ratchet.pid_v3_to_pid_v2")
    @patch("logger.ratchet.Local.register_html_accesses")
    def test_register_access_for_new_website_article(self, mock_register_html_accesses, mock_v3_to_v2):
        parsed_line = {
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
            'page_v3': 'article',
            'month': '05'
        }
        mock_v3_to_v2.return_value = "S1519-38292013000200004"
        self.rb.register_access(parsed_line)
        mock_register_html_accesses.assert_called_once_with(
            'article',
            ANY,
            '2013-05-30',
            '187.19.211.179',
        )

    @patch("logger.ratchet.pid_v3_to_pid_v2")
    @patch("logger.ratchet.Local.register_html_accesses")
    def test_register_access_for_new_website_abstract(self, mock_register_html_accesses, mock_v3_to_v2):
        parsed_line = {
            'ip': '187.19.211.179',
            'code': 'F5Zr9TrzfmMgz9kvGZL3rZB',
            'access_type': 'HTML',
            'iso_date': '2013-05-30',
            'iso_datetime': '2013-05-30T00:01:01',
            'year': '2013',
            'query_string': {"lang": "pt"},
            'day': '30',
            'http_code': '200',
            'original_agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
            'original_date': '[30/May/2013:00:01:01 -0300]',
            'script': '',
            'page_v3': 'abstract',
            'month': '05'
        }

        mock_v3_to_v2.return_value = "S1519-38292013000200004"
        self.rb.register_access(parsed_line)
        mock_register_html_accesses.assert_called_once_with(
            'abstract',
            ANY,
            '2013-05-30',
            '187.19.211.179',
        )

    #####
    @patch("logger.ratchet.pid_v3_to_pid_v2")
    @patch("logger.ratchet.Local.register_v3_page_accesses")
    def test_register_access_for_new_website_pdf(self, mock_register_v3_page_accesses, mock_v3_to_v2):
        parsed_line = {
            'ip': '187.19.211.179',
            'code': 'F5Zr9TrzfmMgz9kvGZL3rZB',
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
            'page_v3': 'pdf',
            'month': '05'
        }
        mock_v3_to_v2.return_value = None
        self.rb.register_access(parsed_line)
        mock_register_v3_page_accesses.assert_called_once_with(
            'pdf',
            ANY,
            '2013-05-30',
        )

    @patch("logger.ratchet.pid_v3_to_pid_v2")
    @patch("logger.ratchet.Local.register_v3_page_accesses")
    def test_register_access_for_new_website_article(self, mock_register_v3_page_accesses, mock_v3_to_v2):
        parsed_line = {
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
            'page_v3': 'article',
            'month': '05'
        }
        mock_v3_to_v2.return_value = None
        self.rb.register_access(parsed_line)
        mock_register_v3_page_accesses.assert_called_once_with(
            'article',
            ANY,
            '2013-05-30'
        )

    @patch("logger.ratchet.pid_v3_to_pid_v2")
    @patch("logger.ratchet.Local.register_v3_page_accesses")
    def test_register_access_for_new_website_abstract(self, mock_register_v3_page_accesses, mock_v3_to_v2):
        parsed_line = {
            'ip': '187.19.211.179',
            'code': 'F5Zr9TrzfmMgz9kvGZL3rZB',
            'access_type': 'HTML',
            'iso_date': '2013-05-30',
            'iso_datetime': '2013-05-30T00:01:01',
            'year': '2013',
            'query_string': {"lang": "pt"},
            'day': '30',
            'http_code': '200',
            'original_agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
            'original_date': '[30/May/2013:00:01:01 -0300]',
            'script': '',
            'page_v3': 'abstract',
            'month': '05'
        }
        mock_v3_to_v2.return_value = None
        self.rb.register_access(parsed_line)
        mock_register_v3_page_accesses.assert_called_once_with(
            'abstract',
            ANY,
            '2013-05-30',
        )

    def test_register_download_access_keys(self):

        self.rb.register_download_access(
            '/pdf/bjmbr/v14n4/03.pdf', '1414-431X', '2013-05-29'
        )

        self.rb.register_download_access(
            '/pdf/bjmbr/v14n4/03.pdf', '1414-431X', '2013-05-30'
        )

        expected = [
            '/PDF/BJMBR/V14N4/03.PDF', '1414-431X', 'scl'
        ]

        self.assertEqual(sorted(self.rb.bulk_data.keys()), expected)

    def test_register_download_access_total(self):

        self.rb.register_download_access(
            '/pdf/bjmbr/v14n4/03.pdf', '1414-431X', '2013-05-29'
        )

        self.rb.register_download_access(
            '/pdf/bjmbr/v14n4/03.pdf', '1414-431X', '2013-05-30'
        )

        expected = [
            '/PDF/BJMBR/V14N4/03.PDF', '1414-431X', 'scl'
        ]

        self.assertEqual(
            self.rb.bulk_data['/PDF/BJMBR/V14N4/03.PDF']['total'], 2
        )

        self.assertEqual(
            self.rb.bulk_data['scl']['total'], 2
        )

        self.assertEqual(
            self.rb.bulk_data['1414-431X']['total'], 2
        )

    def test_register_download_access_keys_values_journal(self):

        self.rb.register_download_access(
            '/pdf/bjmbr/v14n4/03.pdf', '1414-431X', '2013-05-29'
        )

        self.rb.register_download_access(
            '/pdf/bjmbr/v14n4/03.pdf', '1414-431X', '2013-05-30'
        )

        expected = [
            'code:1414-431X',
            'pdf.total:2',
            'pdf.y2013.m05.d29:1',
            'pdf.y2013.m05.d30:1',
            'pdf.y2013.m05.total:2',
            'pdf.y2013.total:2',
            'total:2',
            'type:journal',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['1414-431X'].items()]), expected
        )

    def test_register_download_access_keys_values_website(self):

        self.rb.register_download_access(
            '/pdf/bjmbr/v14n4/03.pdf', '1414-431X', '2013-05-29'
        )

        self.rb.register_download_access(
            '/pdf/bjmbr/v14n4/03.pdf', '1414-431X', '2013-05-30'
        )

        expected = [
            'code:scl',
            'pdf.total:2',
            'pdf.y2013.m05.d29:1',
            'pdf.y2013.m05.d30:1',
            'pdf.y2013.m05.total:2',
            'pdf.y2013.total:2',
            'total:2',
            'type:website',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['scl'].items()]), expected
        )

    def test_register_download_access_keys_values_pdf(self):

        self.rb.register_download_access(
            '/pdf/bjmbr/v14n4/03.pdf', '1414-431X', '2013-05-29'
        )

        self.rb.register_download_access(
            '/pdf/bjmbr/v14n4/03.pdf', '1414-431X', '2013-05-30'
        )

        expected = [
            'code:/PDF/BJMBR/V14N4/03.PDF',
            'pdf.total:2',
            'pdf.y2013.m05.d29:1',
            'pdf.y2013.m05.d30:1',
            'pdf.y2013.m05.total:2',
            'pdf.y2013.total:2',
            'total:2',
            'type:pdf',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['/PDF/BJMBR/V14N4/03.PDF'].items()]), expected
        )

    def test_register_alpha_access_keys_values_website(self):

        self.rb.register_alpha_access(
            'scl', '2013-05-29'
        )

        self.rb.register_alpha_access(
            'scl', '2013-05-30'
        )

        expected = [
            'alpha.total:2',
            'alpha.y2013.m05.d29:1',
            'alpha.y2013.m05.d30:1',
            'alpha.y2013.m05.total:2',
            'alpha.y2013.total:2',
            'code:scl',
            'total:2',
            'type:website',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['scl'].items()]), expected
        )

    def test_register_issues_access_key_values(self):

        self.rb.register_issues_access(
            '1414-431X', '2013-05-29'
        )

        self.rb.register_issues_access(
            '1414-431X', '2013-05-30'
        )

        expected = [
            'code:1414-431X',
            'issues.total:2',
            'issues.y2013.m05.d29:1',
            'issues.y2013.m05.d30:1',
            'issues.y2013.m05.total:2',
            'issues.y2013.total:2',
            'total:2',
            'type:journal',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['1414-431X'].items()]), expected
        )

    def test_register_issues_access_keys_values(self):

        self.rb.register_issues_access(
            '1414-431X', '2013-05-29'
        )

        self.rb.register_issues_access(
            '1414-431X', '2013-05-30'
        )

        expected = [
            'code:scl',
            'issues.total:2',
            'issues.y2013.m05.d29:1',
            'issues.y2013.m05.d30:1',
            'issues.y2013.m05.total:2',
            'issues.y2013.total:2',
            'total:2',
            'type:website',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['scl'].items()]), expected
        )

    def test_register_home_access_keys_values(self):

        self.rb.register_home_access(
            'scl', '2013-05-29'
        )

        self.rb.register_home_access(
            'scl', '2013-05-30'
        )

        expected = [
            'code:scl',
            'home.total:2',
            'home.y2013.m05.d29:1',
            'home.y2013.m05.d30:1',
            'home.y2013.m05.total:2',
            'home.y2013.total:2',
            'total:2',
            'type:website',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['scl'].items()]), expected
        )

    def test_register_journal_access_keys_values(self):

        self.rb.register_journal_access(
            '1414-431X', '2013-05-29'
        )

        self.rb.register_journal_access(
            '1414-431X', '2013-05-30'
        )

        expected = [
            'code:1414-431X',
            'journal.total:2',
            'journal.y2013.m05.d29:1',
            'journal.y2013.m05.d30:1',
            'journal.y2013.m05.total:2',
            'journal.y2013.total:2',
            'total:2',
            'type:journal',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['1414-431X'].items()]), expected
        )

    def test_register_journal_access_keys_values_website(self):

        self.rb.register_journal_access(
            '1414-431X', '2013-05-29'
        )

        self.rb.register_journal_access(
            '1414-431X', '2013-05-30'
        )

        expected = [
            'code:scl',
            'journal.total:2',
            'journal.y2013.m05.d29:1',
            'journal.y2013.m05.d30:1',
            'journal.y2013.m05.total:2',
            'journal.y2013.total:2',
            'total:2',
            'type:website',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['scl'].items()]), expected
        )

    def test_register_toc_access_keys_values_website(self):

        self.rb.register_toc_access(
            '1414-431X20140001', '2013-05-29'
        )

        self.rb.register_toc_access(
            '1414-431X20140001', '2013-05-30'
        )

        expected = [
            'code:scl',
            'toc.total:2',
            'toc.y2013.m05.d29:1',
            'toc.y2013.m05.d30:1',
            'toc.y2013.m05.total:2',
            'toc.y2013.total:2',
            'total:2',
            'type:website',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['scl'].items()]), expected
        )

    def test_register_toc_access_keys_values_journal(self):

        self.rb.register_toc_access(
            '1414-431X20140001', '2013-05-29'
        )

        self.rb.register_toc_access(
            '1414-431X20140001', '2013-05-30'
        )

        expected = [
            'code:1414-431X',
            'toc.total:2',
            'toc.y2013.m05.d29:1',
            'toc.y2013.m05.d30:1',
            'toc.y2013.m05.total:2',
            'toc.y2013.total:2',
            'total:2',
            'type:journal',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['1414-431X'].items()]), expected
        )

    def test_register_toc_access_keys_values(self):

        self.rb.register_toc_access(
            '1414-431X20140001', '2013-05-29'
        )

        self.rb.register_toc_access(
            '1414-431X20140001', '2013-05-30'
        )

        expected = [
            'code:1414-431X20140001',
            'journal:1414-431X',
            'toc.total:2',
            'toc.y2013.m05.d29:1',
            'toc.y2013.m05.d30:1',
            'toc.y2013.m05.total:2',
            'toc.y2013.total:2',
            'total:2',
            'type:issue',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['1414-431X20140001'].items()]), expected
        )

    def test_register_article_access_keys_values_website(self):

        self.rb.register_article_access(
            'S1414-431X2014000100005', '2013-05-29'
        )

        self.rb.register_article_access(
            'S1414-431X2014000100005', '2013-05-30'
        )

        expected = [
            'code:scl',
            'html.total:2',
            'html.y2013.m05.d29:1',
            'html.y2013.m05.d30:1',
            'html.y2013.m05.total:2',
            'html.y2013.total:2',
            'total:2',
            'type:website',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['scl'].items()]), expected
        )

    def test_register_article_access_keys_values_journal(self):

        self.rb.register_article_access(
            'S1414-431X2014000100005', '2013-05-29'
        )

        self.rb.register_article_access(
            'S1414-431X2014000100005', '2013-05-30'
        )

        expected = [
            'code:1414-431X',
            'html.total:2',
            'html.y2013.m05.d29:1',
            'html.y2013.m05.d30:1',
            'html.y2013.m05.total:2',
            'html.y2013.total:2',
            'total:2',
            'type:journal',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['1414-431X'].items()]), expected
        )

    def test_register_article_access_keys_values_toc(self):

        self.rb.register_article_access(
            'S1414-431X2014000100005', '2013-05-29'
        )

        self.rb.register_article_access(
            'S1414-431X2014000100005', '2013-05-30'
        )

        expected = [
            'code:1414-431X20140001',
            'html.total:2',
            'html.y2013.m05.d29:1',
            'html.y2013.m05.d30:1',
            'html.y2013.m05.total:2',
            'html.y2013.total:2',
            'total:2',
            'type:issue',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['1414-431X20140001'].items()]), expected
        )

    def test_register_article_access_keys_values(self):

        self.rb.register_article_access(
            'S1414-431X2014000100005', '2013-05-29'
        )

        self.rb.register_article_access(
            'S1414-431X2014000100005', '2013-05-30'
        )

        expected = [
            'code:S1414-431X2014000100005',
            'html.total:2',
            'html.y2013.m05.d29:1',
            'html.y2013.m05.d30:1',
            'html.y2013.m05.total:2',
            'html.y2013.total:2',
            'issue:1414-431X20140001',
            'journal:1414-431X',
            'total:2',
            'type:article',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['S1414-431X2014000100005'].items()]), expected
        )

    def test_register_abstract_access_keys_values_website(self):

        self.rb.register_abstract_access(
            'S1414-431X2014000100005', '2013-05-29'
        )

        self.rb.register_abstract_access(
            'S1414-431X2014000100005', '2013-05-30'
        )

        expected = [
            'abstract.total:2',
            'abstract.y2013.m05.d29:1',
            'abstract.y2013.m05.d30:1',
            'abstract.y2013.m05.total:2',
            'abstract.y2013.total:2',
            'code:scl',
            'total:2',
            'type:website',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['scl'].items()]), expected
        )

    def test_register_abstract_access_keys_values_journal(self):

        self.rb.register_abstract_access(
            'S1414-431X2014000100005', '2013-05-29'
        )

        self.rb.register_abstract_access(
            'S1414-431X2014000100005', '2013-05-30'
        )

        expected = [
            'abstract.total:2',
            'abstract.y2013.m05.d29:1',
            'abstract.y2013.m05.d30:1',
            'abstract.y2013.m05.total:2',
            'abstract.y2013.total:2',
            'code:1414-431X',
            'total:2',
            'type:journal',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['1414-431X'].items()]), expected
        )

    def test_register_abstract_access_keys_values_toc(self):

        self.rb.register_abstract_access(
            'S1414-431X2014000100005', '2013-05-29'
        )

        self.rb.register_abstract_access(
            'S1414-431X2014000100005', '2013-05-30'
        )

        expected = [
            'abstract.total:2',
            'abstract.y2013.m05.d29:1',
            'abstract.y2013.m05.d30:1',
            'abstract.y2013.m05.total:2',
            'abstract.y2013.total:2',
            'code:1414-431X20140001',
            'total:2',
            'type:issue',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['1414-431X20140001'].items()]), expected
        )

    def test_register_abstract_access_keys_values(self):

        self.rb.register_abstract_access(
            'S1414-431X2014000100005', '2013-05-29'
        )

        self.rb.register_abstract_access(
            'S1414-431X2014000100005', '2013-05-30'
        )

        expected = [
            'abstract.total:2',
            'abstract.y2013.m05.d29:1',
            'abstract.y2013.m05.d30:1',
            'abstract.y2013.m05.total:2',
            'abstract.y2013.total:2',
            'code:S1414-431X2014000100005',
            'issue:1414-431X20140001',
            'journal:1414-431X',
            'total:2',
            'type:article',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['S1414-431X2014000100005'].items()]), expected
        )

    def test_register_opdf_access_keys_values_website(self):

        self.rb.register_pdf_access(
            'S1414-431X2014000100005', '2013-05-29'
        )

        self.rb.register_pdf_access(
            'S1414-431X2014000100005', '2013-05-30'
        )

        expected = [
            'code:scl',
            'other.pdfsite.total:2',
            'other.pdfsite.y2013.m05.d29:1',
            'other.pdfsite.y2013.m05.d30:1',
            'other.pdfsite.y2013.m05.total:2',
            'other.pdfsite.y2013.total:2',
            'total:2',
            'type:website',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['scl'].items()]), expected
        )

    def test_register_opdf_access_keys_values_journal(self):

        self.rb.register_pdf_access(
            'S1414-431X2014000100005', '2013-05-29'
        )

        self.rb.register_pdf_access(
            'S1414-431X2014000100005', '2013-05-30'
        )

        expected = [
            'code:1414-431X',
            'other.pdfsite.total:2',
            'other.pdfsite.y2013.m05.d29:1',
            'other.pdfsite.y2013.m05.d30:1',
            'other.pdfsite.y2013.m05.total:2',
            'other.pdfsite.y2013.total:2',
            'total:2',
            'type:journal',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['1414-431X'].items()]), expected
        )

    def test_register_opdf_access_keys_values_toc(self):

        self.rb.register_pdf_access(
            'S1414-431X2014000100005', '2013-05-29'
        )

        self.rb.register_pdf_access(
            'S1414-431X2014000100005', '2013-05-30'
        )

        expected = [
            'code:1414-431X20140001',
            'other.pdfsite.total:2',
            'other.pdfsite.y2013.m05.d29:1',
            'other.pdfsite.y2013.m05.d30:1',
            'other.pdfsite.y2013.m05.total:2',
            'other.pdfsite.y2013.total:2',
            'total:2',
            'type:issue',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['1414-431X20140001'].items()]), expected
        )

    def test_register_opdf_access_keys_values(self):

        self.rb.register_pdf_access(
            'S1414-431X2014000100005', '2013-05-29'
        )

        self.rb.register_pdf_access(
            'S1414-431X2014000100005', '2013-05-30'
        )

        expected = [
            'code:S1414-431X2014000100005',
            'issue:1414-431X20140001',
            'journal:1414-431X',
            'other.pdfsite.total:2',
            'other.pdfsite.y2013.m05.d29:1',
            'other.pdfsite.y2013.m05.d30:1',
            'other.pdfsite.y2013.m05.total:2',
            'other.pdfsite.y2013.total:2',
            'total:2',
            'type:article',
            'y2013.m05.d29:1',
            'y2013.m05.d30:1',
            'y2013.m05.total:2',
            'y2013.total:2'
        ]

        self.assertEqual(
            sorted(['%s:%s' % (k, v) for k, v in self.rb.bulk_data['S1414-431X2014000100005'].items()]), expected
        )

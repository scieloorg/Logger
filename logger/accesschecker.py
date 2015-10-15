# coding: utf-8

import os
import urllib2
import json
import datetime
import urlparse
import re

import apachelog

from logger import utils

MONTH_DICT = {
    'JAN': '01',
    'FEB': '02',
    'MAR': '03',
    'APR': '04',
    'MAY': '05',
    'JUN': '06',
    'JUL': '07',
    'AUG': '08',
    'SEP': '09',
    'OCT': '10',
    'NOV': '11',
    'DEC': '12',
}

config = utils.Configuration.from_env()
settings = dict(config.items())['app:main']

ROBOTS = [i.strip() for i in open(settings.get('robots_file', 'robots.txt'))]
APACHE_LOG_FORMAT = settings.get('log_format', r'= %h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"')
COMPILED_ROBOTS = [re.compile(i.lower()) for i in ROBOTS]
REGEX_ISSN = re.compile("^[0-9]{4}-[0-9]{3}[0-9xX]$")
REGEX_ISSUE = re.compile("^[0-9]{4}-[0-9]{3}[0-9xX][0-2][0-9]{3}[0-9]{4}$")
REGEX_ARTICLE = re.compile("^[0-9]{4}-[0-9]{3}[0-9xX][0-2][0-9]{3}[0-9]{4}[0-9]{5}$")
REGEX_FBPE = re.compile("^[0-9]{4}-[0-9]{3}[0-9xX]\([0-9]{2}\)[0-9]{8}$")


class AccessChecker(object):

    def __init__(self, collection=None, counter_compliant=False):
        self._parser = apachelog.parser(APACHE_LOG_FORMAT)
        allowed_collections = self._allowed_collections()

        if not collection in allowed_collections:
            raise ValueError('Invalid collection id ({0}), you must select one of these {1}'.format(collection, str(allowed_collections)))

        self.collection = collection
        self.acronym_to_issn_dict = self._acronym_to_issn_dict()
        self.allowed_issns = self._allowed_issns(self.acronym_to_issn_dict)

    def _allowed_collections(self):
        allowed_collections = []

        query_url = 'http://articlemeta.scielo.org/api/v1/collection/identifiers'
        try:
            json_network = urllib2.urlopen(query_url, timeout=10).read()
        except:
            raise urllib2.URLError('Was not possible to connect to articlemeta api (%s), try again later!' % query_url)

        network = json.loads(json_network)

        for collection in network:
            allowed_collections.append(collection['acron'])

        return allowed_collections

    def _acronym_to_issn_dict(self):
        """
        Create a acronym dictionay with valid issns. The issn's are the issn's
        used as id in the SciELO Website.
        """
        query_url = 'http://articlemeta.scielo.org/api/v1/journal?collection=%s' % self.collection

        try:
            titles_json = urllib2.urlopen(query_url, timeout=10).read()
        except:
            raise urllib2.URLError('Was not possible to connect to articlemeta api (%s), try again later!' % query_url)

        titles = json.loads(titles_json)

        title_dict = {}
        for title in titles:
            title_dict[title['v68'][0]['_']] = title['v400'][0]['_']

        return title_dict

    def _allowed_issns(self, acronym_to_issn):
        issns = []
        for issn in acronym_to_issn.values():
            issns.append(issn)

        return issns

    def _parse_line(self, raw_line):
        try:
            return self._parser.parse(raw_line)
        except:
            return None

    def _query_string(self, url):
        """
        Given a request from a access log line in these formats:
            'GET /scielo.php?script=sci_nlinks&ref=000144&pid=S0103-4014200000020001300010&lng=pt HTTP/1.1'
            'GET http://www.scielo.br/scielo.php?script=sci_nlinks&ref=000144&pid=S0103-4014200000020001300010&lng=pt HTTP/1.1'
        The method must retrieve the query_string dictionary.

        """
        try:
            url = url.split(' ')[1]
        except IndexError:
            return None

        qs = dict((k,v[0]) for k,v in urlparse.parse_qs(urlparse.urlparse(url).query).items())

        if len(qs) > 0:
            return qs

    def _access_date(self, access_date):
        """
        Given a date from a access log line in this format: [30/Dec/2012:23:59:57 -0200]
        The method must retrieve a valid iso date 2012-12-30 or None
        """

        try:
            return datetime.datetime.strptime(access_date[1:21], '%d/%b/%Y:%H:%M:%S')
        except:
            return None

    def _pdf_or_html_access(self, get):
        if "GET" in get and ".pdf" in get:
            return "PDF"

        if "GET" in get and "scielo.php" in get and "script" in get and "pid" in get:
            return "HTML"

        return None

    def _is_valid_html_request(self, script, pid):

        pid = pid.upper().replace('S', '')

        try:
            if not pid[0:9] in self.allowed_issns:
                return False
        except:
            return False

        if script == "sci_arttext" and (REGEX_ARTICLE.search(pid) or REGEX_FBPE.search(pid)):
            return True

        if script == "sci_abstract" and (REGEX_ARTICLE.search(pid) or REGEX_FBPE.search(pid)):
            return True

        if script == "sci_pdf" and (REGEX_ARTICLE.search(pid) or REGEX_FBPE.search(pid)):
            return True

        if script == "sci_serial" and REGEX_ISSN.search(pid):
            return True

        if script == "sci_issuetoc" and REGEX_ISSUE.search(pid):
            return True

        if script == "sci_issues" and REGEX_ISSN.search(pid):
            return True

        return False

    def _is_valid_pdf_request(self, filepath):
        """
        This method checks if the pdf path represents a valid pdf request. If it is valid, this
        methof will retrieve a dictionary with the filepath and the journal issn.
        """
        data = {}

        if not filepath.strip():
            return None

        url = filepath.split(" ")[1]
        data['pdf_path'] = urlparse.urlparse(url).path

        if not data['pdf_path'][-3:].lower() == 'pdf':
            return None

        try:
            data['pdf_issn'] = self.acronym_to_issn_dict[data['pdf_path'].split('/')[2]]
        except (KeyError, IndexError):
            return None

        return data

    def is_robot(self, user_agent):
        for robot in COMPILED_ROBOTS:
            if robot.search(user_agent):
                return True

        return False

    def parsed_access(self, raw_line):

        parsed_line = self._parse_line(raw_line)

        if not parsed_line:
            return None

        if self.is_robot(parsed_line['%{User-Agent}i']):
            return None

        access_date = self._access_date(parsed_line['%t'])

        if not access_date:
            return None

        data = {}
        data['ip'] = parsed_line['%h'].strip()
        data['original_date'] = parsed_line['%t']
        data['original_agent'] = parsed_line['%{User-Agent}i']
        data['access_type'] = self._pdf_or_html_access(parsed_line['%r'])
        data['iso_date'] = access_date.date().isoformat()
        data['iso_datetime'] = access_date.isoformat()
        data['query_string'] = self._query_string(parsed_line['%r'])
        data['day'] = data['iso_date'][8:10]
        data['month'] = data['iso_date'][5:7]
        data['year'] = data['iso_date'][0:4]

        if not data['access_type']:
            return None

        if not data['iso_date']:
            return None

        if data['access_type'] == u'HTML':

            if not data['query_string']:
                return None

            if not 'script' in data['query_string'] or not 'pid' in data['query_string']:
                return None

            if not self._is_valid_html_request(data['query_string']['script'],
                                               data['query_string']['pid']):
                return None

            data['code'] = data['query_string']['pid']
            data['script'] = data['query_string']['script']

        pdf_request = self._is_valid_pdf_request(parsed_line['%r'])

        if data['access_type'] == u'PDF':
            if not pdf_request:
                return None

            data['code'] = pdf_request['pdf_path'].lower()
            data['script'] = ''

            data.update(pdf_request)

        return data

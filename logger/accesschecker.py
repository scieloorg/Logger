import urllib2
import json
import datetime
import urlparse
import re
from logaccess_config import *
import apachelog

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

COMPILED_ROBOTS = [re.compile(i.lower()) for i in STOP_WORDS]
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
        self.allowed_issns = set([v for k,v in self.acronym_to_issn_dict.items()])
        

    def _allowed_collections(self):        
        allowed_collections = []
        try:
            json_network = urllib2.urlopen('http://webservices.scielo.org/scieloorg/_design/couchdb/_view/network', timeout=3).read()
        except urllib2.URLError:
            raise urllib2.URLError('Was not possible to connect to webservices.scielo.org, try again later!')

        network = json.loads(json_network)

        for collection in network['rows']:
            allowed_collections.append(collection['id'])
        
        return allowed_collections

    def _acronym_to_issn_dict(self):        
        query_url = 'http://webservices.scielo.org/scieloorg/_design/couchdb/_view/title_collectionstitle_keys?startkey=["%s",{}]&endkey=["%s"]&descending=true&limit=2000&include_docs=true' % (self.collection, self.collection)

        try:
            titles_json = urllib2.urlopen(query_url, timeout=3).read()
        except urllib2.URLError:
            raise urllib2.URLError('Was not possible to connect to webservices.scielo.org, try again later!')

        titles = json.loads(titles_json)

        title_dict = {}
        for title in titles['rows']:
            title_dict[title['doc']['v68'][0]['_']] = title['doc']['v400'][0]['_']

        return title_dict

    def _allowed_issns(self, acronym_to_issn):
        issns = set()
        for issn in acronym_to_issn:
            issns.add(issn)

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
            dt = access_date[1:12].split('/')
            day = int(dt[0])
            month = int(MONTH_DICT[dt[1].upper()])
            year = int(dt[2])
        except ValueError:
            return None
        except KeyError:
            return None


        return datetime.date(year, month, day).isoformat()

    def _pdf_or_html_access(self, get):
        if "GET" in get and ".pdf" in get:
            return "PDF"

        if "GET" in get and "scielo.php" in get and "script" in get and "pid" in get:
            return "HTML"

        return None

    def _is_valid_html_request(self, script, pid):

        pid = pid.upper().replace('S','')

        if not pid[0:9] in self.allowed_issns:
            return None

        if script == u"sci_arttext" and (REGEX_ARTICLE.search(pid) or REGEX_FBPE.search(pid)):
            return True

        if script == u"sci_abstract" and (REGEX_ARTICLE.search(pid) or REGEX_FBPE.search(pid)):
            return True

        if script == u"sci_pdf" and (REGEX_ARTICLE.search(pid) or REGEX_FBPE.search(pid)):
            return True

        if script == u"sci_serial" and REGEX_ISSN.search(pid):
            return True

        if script == u"sci_issuetoc" and REGEX_ISSUE.search(pid):
            return True

        if script == u"sci_issues" and REGEX_ISSN.search(pid):
            return True

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
        except KeyError:
            return None

        return data

    def is_robot(self, raw_line):
        for robot in COMPILED_ROBOTS:
            if robot.search(raw_line):
                return True

    def parsed_access(self, raw_line):

        if self.is_robot(raw_line):
            return None

        parsed_line = self._parse_line(raw_line)

        if not parsed_line:
            return None

        data = {}
        data['ip'] = parsed_line['%h'].strip()
        data['access_type'] = self._pdf_or_html_access(parsed_line['%r'])
        data['iso_date'] = self._access_date(parsed_line['%t'])
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

            if not self._is_valid_html_request(data['query_string']['script'], data['query_string']['pid']):
                return None

        pdf_request = self._is_valid_pdf_request(parsed_line['%r'])
        if data['access_type'] == u'PDF': 
            if not pdf_request:
                return None
        
            data.update(pdf_request)

        return data

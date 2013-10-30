import urllib2
import json
import datetime
import urlparse

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

class AccessChecker(object):

    def __init__(self, collection=None):
        self._parser = apachelog.parser(APACHE_LOG_FORMAT)
        allowed_collections = self._allowed_collections()
        
        if not collection in allowed_collections:
            raise ValueError('Invalid collection id, you must select one of these %s' % str(allowed_collections)) 

        self.collection = collection
        self.allowed_issns = self._allowed_issns()

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

    def _allowed_issns(self):        
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

    def _parse_line(self, raw_line):
        try:
            return self._parser.parse(raw_line)
        except:
            return None

    def query_string(self, url):
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

    def access_date(self, access_date):
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

    def pdf_or_html_access(self, get):
        if "GET" in get and ".pdf" in get:
            return "PDF"

        if "GET" in get and "scielo.php" in get and "script" in get and "pid" in get:
            return "HTML"

        return None


    def parsed_access(self, raw_line):

        parsed_line = self._parse_line(raw_line)

        if not parsed_line:
            return None

        access_date = self.access_date(parsed_line['%t'])
        access_type = self.pdf_or_html_access(parsed_line['%r'])
        query_string = self.query_string(parsed_line['%r'])

        if access_type == u'HTML' and access_date and valid_html_request(query_string):
            pass

        if access_type == u'PDF' and valid_pdf_request(parsed_line['%r']):
            pass

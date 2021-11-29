# coding: utf-8

import datetime
import urlparse
import re
import logging

import apachelog

from logger import utils
from articlemeta.client import ThriftClient

logger = logging.getLogger(__name__)

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

ROBOTS = [i.strip() for i in open(utils.settings.get('robots_file', 'robots.txt'))]
APACHE_LOG_FORMAT = utils.settings.get(
    'log_format',
    r'= %h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"')
COMPILED_ROBOTS = [re.compile(i.lower()) for i in ROBOTS]
REGEX_ISSN = re.compile(
    "^[0-9]{4}-[0-9]{3}[0-9xX]$")
REGEX_ISSUE = re.compile(
    "^[0-9]{4}-[0-9]{3}[0-9xX][0-2][0-9]{3}[0-9]{4}$")
REGEX_ARTICLE = re.compile(
    "^[0-9]{4}-[0-9]{3}[0-9xX][0-2][0-9]{3}[0-9]{4}[0-9]{5}$")
REGEX_FBPE = re.compile(
    "^[0-9]{4}-[0-9]{3}[0-9xX]\([0-9]{2}\)[0-9]{8}$")

am_client = ThriftClient(domain='articlemeta.scielo.org:11621')
COLLECTIONS = utils.Collections()


# abordagem para facilitar os testes
def _allowed_collections():
    return COLLECTIONS.website_ids


def _get_collection_id(website_id):
    return COLLECTIONS.get_website(website_id).collection_id


def _acronym_to_issn_dict(collection_id):
    """Produz um dicionário que mapeia acrônimo de periódico para seu ISSN 
    SciELO
    """
    try:
        logger.info('Getting the journals of %s' % collection_id)
        journals = am_client.journals(collection_id)
    except Exception as e:
        logger.error(
            'Fail to retrieve journals issns (%s) from thrift server: %s' %
            (collection_id, str(e)))
    else:
        return {i.acronym: i.scielo_issn for i in journals}


class AccessChecker(object):

    def __init__(
            self, 
            collection=None, 
            counter_compliant=False, 
            allowed_collections=_allowed_collections, 
            acronym_to_issn_dict=_acronym_to_issn_dict
        ):
        self._parser = apachelog.parser(APACHE_LOG_FORMAT)
        allowed_collections = allowed_collections()

        # o argumento `collection` corresponde ao `website_id`:
        # 'nbr' para novo site br e 'scl' para old.scielo.br
        if collection not in allowed_collections:
            raise ValueError('Invalid collection id ({0}), you must select one of these {1}'.format(collection, str(allowed_collections)))

        self.collection = collection

        # `collection_id` - acronimo da colecao no AM, é scl,
        # tanto para o site novo como para o site clássico
        collection_id = _get_collection_id(collection)
        self.acronym_to_issn_dict = acronym_to_issn_dict(collection_id)

        self.allowed_issns = list(self.acronym_to_issn_dict.values())
        logger.info(
            'Journals (%s): %i' % (collection, len(self.allowed_issns)))

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

        qs = dict((k, v[0]) for k, v in urlparse.parse_qs(urlparse.urlparse(url).query).items())

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
        if "GET" in get:
            if re.search(r"[\./(format=)]pdf", get):
                return "PDF"

            elif (
                    "scielo.php" in get \
                    and "script" in get \
                    and "pid" in get
                ) \
                or "format=html" in get \
                or "/article/" in get \
                or "/a/" in get:

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
        This method checks if the pdf path represents a valid pdf request.
        If it is valid, this method will retrieve a dictionary with the filepath
        and the journal issn.
        """
        data = {}

        if not filepath.strip():
            return None

        match = re.search(r'/pdf/.+?/.+?/.+?(?=\s)', filepath)
        if match:
            url = match.group()
            if not url.lower().endswith('.pdf'):
                url = re.sub(r'/(\D\D)?$', r'/', url)
        else:
             match = re.search(r'/a/([a-zA-Z0-9]{23})', filepath)
             if match:
                url= match.group()
             else:
                 return None

        data['pdf_path'] = urlparse.urlparse(url).path

        if 'pdf' not in data['pdf_path'].lower():
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
            logger.debug('cannot parse log line "%s"', raw_line)
            return None

        if self.is_robot(parsed_line['%{User-Agent}i']):
            logger.debug('cannot count log line "%s": the user-agent is blacklisted', raw_line)
            return None

        access_date = self._access_date(parsed_line['%t'])

        if not access_date:
            logger.debug('cannot count log line "%s": missing access date', raw_line)
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
        data['http_code'] = parsed_line['%>s']

        if not data['http_code'] or data['http_code'] not in ['200', '304']:
            logger.debug('cannot count log line "%s": unsupported html status code', raw_line)
            return None
 
        if not data['access_type']:
            logger.debug('cannot count log line "%s": missing document type', raw_line)
            return None

        if not data['iso_date']:
            logger.debug('cannot count log line "%s": missing iso date', raw_line)
            return None

        if data['access_type'] == u'HTML':
            return self._match_access_type_html(data, parsed_line, raw_line)

        if data['access_type'] == u'PDF':
            return self._match_access_type_pdf(data, parsed_line, raw_line)

        return data

    def _match_access_type_html(self, data, parsed_line, raw_line):
        match = re.search(r'/article/.+?/.+?/.+?/', parsed_line['%r'])
        if match:
            data['code'] = match.group()
            data['script'] = ''

        else:
            match = re.search(r'/a/(?P<pid>[a-zA-Z0-9]{23})', parsed_line['%r'])
            if match:
                # URLs do OPAC
                data['code'] = match.groupdict()['pid']
                data['script'] = ''
            else:
                # URLs do site clássico
                if not data['query_string']:
                    logger.debug('cannot count log line "%s": missing querystring', raw_line)
                    return None

                if 'script' not in data['query_string'] or 'pid' not in data['query_string']:
                    logger.debug('cannot count log line "%s": missing script or pid in querystring', raw_line)
                    return None

                if not self._is_valid_html_request(data['query_string']['script'],
                                                   data['query_string']['pid']):
                    logger.debug('cannot count log line "%s": request is invalid', raw_line)
                    return None

                data['code'] = data['query_string']['pid']
                data['script'] = data['query_string']['script']
        return data

    def _match_access_type_pdf(self, data, parsed_line, raw_line):
        pdf_request = self._is_valid_pdf_request(parsed_line['%r'])
        if pdf_request:
            data['code'] = pdf_request['pdf_path']
            data['script'] = ''
            data.update(pdf_request)
        else:
            match = re.search(r'/a/(?P<pid>[a-zA-Z0-9]{23})', parsed_line['%r'])
            if match:
                # URLs do OPAC
                data['code'] = match.groupdict()['pid'] + "_pdf"
                data['script'] = ''
            else:
                logger.debug('cannot count log line "%s": request is invalid', raw_line)
                return None
        return data

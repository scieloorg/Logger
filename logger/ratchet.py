# coding: utf-8
import json
import datetime
import logging
import traceback
import time
import urlparse

import requests
from requests import exceptions
import pymongo


_logger = logging.getLogger(__name__)


def dorequest(url):

    attempts = 0
    while attempts <= 10:
        if attempts > 1:
            _logger.warning('Retry %s' % url)
        attempts += 1

        try:
            x = requests.post('http://'+url, allow_redirects=False)
            _logger.debug('Request %s' % url)
            x.close()
            x.connection.close()
            break
        except exceptions.ConnectionError as e:
            if attempts > 10:
                _logger.error('ConnectionError {0}, {1}: {2}'.format(e.errno, e.strerror, url))
        except exceptions.HTTPError as e:
            if attempts > 10:
                _logger.error('HTTPError {0}, {1}: {2}'.format(e.errno, e.strerror, url))
        except exceptions.TooManyRedirects as e:
            if attempts > 10:
                _logger.error('ToManyRedirections {0}, {1}: {2}'.format(e.errno, e.strerror, url))
        except exceptions.Timeout as e:
            if attempts > 10:
                _logger.error('Timeout {0}, {1}: {2}'.format(e.errno, e.strerror, url))
        except:
            if attempts > 10:
                _logger.error('Unexpected error: {0} : URL: {1}'.format(traceback.format_exc(), url))


class RatchetBulk(object):

    def _load_to_bulk(self, code, access_date, page, issue=None, journal=None, type_doc=None):
        self.bulk_data.setdefault(code, {})
        self.bulk_data[code]['code'] = code

        if issue:
            self.bulk_data[code]['issue'] = issue

        if journal:
            self.bulk_data[code]['journal'] = journal

        if type_doc:
            self.bulk_data[code]['type'] = type_doc

        day = '.'.join('%s%s' % t for t in zip(['y', 'm', 'd'], access_date.split('-')[0:]))
        month = '.'.join('%s%s' % t for t in zip(['y', 'm'], access_date.split('-')[:2]))
        year = 'y%s' % access_date.split('-')[0]

        field_day_total = day
        field_month_total = '%s.total' % month
        field_year_total = '%s.total' % year
        self.bulk_data[code].setdefault(field_day_total, 0)
        self.bulk_data[code][field_day_total] += 1
        self.bulk_data[code].setdefault(field_month_total, 0)
        self.bulk_data[code][field_month_total] += 1
        self.bulk_data[code].setdefault(field_year_total, 0)
        self.bulk_data[code][field_year_total] += 1

        field_page_day_total = '.'.join([page, field_day_total])
        field_page_month_total = '.'.join([page, field_month_total])
        field_page_year_total = '.'.join([page, field_year_total])
        field_page_total = '.'.join([page, 'total'])
        self.bulk_data[code].setdefault(field_page_day_total, 0)
        self.bulk_data[code][field_page_day_total] += 1
        self.bulk_data[code].setdefault(field_page_month_total, 0)
        self.bulk_data[code][field_page_month_total] += 1
        self.bulk_data[code].setdefault(field_page_year_total, 0)
        self.bulk_data[code][field_page_year_total] += 1
        self.bulk_data[code].setdefault(field_page_total, 0)
        self.bulk_data[code][field_page_total] += 1
        self.bulk_data[code].setdefault('total', 0)
        self.bulk_data[code]['total'] += 1

    def register_download_access(self, code, issn, access_date):
        page = 'pdf'
        code = code.upper()
        issn = issn.upper()
        self._load_to_bulk(code=code, access_date=access_date, page=page, type_doc='pdf')
        # # Register PDF direct download access for a specific journal register
        self._load_to_bulk(code=issn, access_date=access_date, page=page, type_doc='journal')
        # # Register PDF direct download access for a collection register
        self._load_to_bulk(code=self._collection, access_date=access_date, page=page, type_doc='website')

    def register_readcube_access(self, code, access_date):
        page = 'readcube'
        code = code.upper()
        self._load_to_bulk(code=code, access_date=access_date, page=page, type_doc='readcube')
        # # Register PDF direct download access for a collection register
        self._load_to_bulk(code=self._collection, access_date=access_date, page=page, type_doc='website')

    def register_journal_access(self, code, access_date):
        page = 'journal'
        code = code.upper()
        # Register access for journal page
        self._load_to_bulk(code=code, access_date=access_date, page=page, type_doc='journal')
        # Register access inside collection record for page sci_serial
        self._load_to_bulk(code=self._collection, access_date=access_date, page=page, type_doc='website')

    def register_article_access(self, code, access_date):
        page = 'html'
        code = code.upper()
        # Register access for a specific article
        self._load_to_bulk(code=code, access_date=access_date, journal=code[1:10], issue=code[1:18], page=page, type_doc='article')
        # Register access inside toc record for page sci_arttext
        self._load_to_bulk(code=code[1:18], access_date=access_date, page=page, type_doc='issue')
        # Register access inside journal record for page sci_arttext
        self._load_to_bulk(code=code[1:10], access_date=access_date, page=page, type_doc='journal')
        # Register access inside collection record for page sci_arttext
        self._load_to_bulk(code=self._collection, access_date=access_date, page=page, type_doc='website')

    def register_abstract_access(self, code, access_date):
        page = 'abstract'
        code = code.upper()
        # Register access for a specific article
        self._load_to_bulk(code=code, access_date=access_date, journal=code[1:10], issue=code[1:18], page=page, type_doc='article')
        # Register access inside toc record for page sci_abstract
        self._load_to_bulk(code=code[1:18], access_date=access_date, page=page, type_doc='issue')
        # Register access inside journal record for page sci_abstract
        self._load_to_bulk(code=code[1:10], access_date=access_date, page=page, type_doc='journal')
        # Register access inside collection record for page sci_abstract
        self._load_to_bulk(code=self._collection, access_date=access_date, page=page, type_doc='website')

    def register_pdf_access(self, code, access_date):
        page = 'other.pdfsite'
        code = code.upper()
        # Register access for a specific article
        self._load_to_bulk(code=code, access_date=access_date, journal=code[1:10], issue=code[1:18], page=page, type_doc='article')
        # Register access inside toc record for page pdf
        self._load_to_bulk(code=code[1:18], access_date=access_date, page=page, type_doc='issue')
        # Register access inside journal record for page pdf
        self._load_to_bulk(code=code[1:10], access_date=access_date, page=page, type_doc='journal')
        # Register access inside collection record for page pdf
        self._load_to_bulk(code=self._collection, access_date=access_date, page=page, type_doc='website')

    def register_toc_access(self, code, access_date):
        page = 'toc'
        code = code.upper()
        # Register access for a specific issue
        self._load_to_bulk(code=code, access_date=access_date, journal=code[0:9], page=page, type_doc='issue')
        # Register access inside journal record for page sci_issuetoc
        self._load_to_bulk(code=code[0:9], access_date=access_date, page=page, type_doc='journal')
        # Register access inside collection record for page sci_issuetoc
        self._load_to_bulk(code=self._collection, access_date=access_date, page=page, type_doc='website')

    def register_home_access(self, code, access_date):
        page = 'home'
        code = code.upper()
        # Register access inside collection record for page sci_home
        self._load_to_bulk(code=self._collection, access_date=access_date, page=page, type_doc='website')

    def register_issues_access(self, code, access_date):
        page = 'issues'
        code = code.upper()
        # Register access inside journal record for page issues
        self._load_to_bulk(code=code[0:9], access_date=access_date, page=page, type_doc='journal')
        # Register access inside collection record for page issues
        self._load_to_bulk(code=self._collection, access_date=access_date, page=page, type_doc='website')

    def register_alpha_access(self, code, access_date):
        page = 'alpha'
        code = code.upper()
        # Register access inside collection record for page alphabetic list
        self._load_to_bulk(code=self._collection, access_date=access_date, page=page, type_doc='website')

    def register_v3_page_accesses(self, page, code, access_date):
        # Register access for a specific article
        self._load_to_bulk(code=code, access_date=access_date, page=page, type_doc='article')

        # Register access inside collection record for page sci_arttext
        self._load_to_bulk(code=self._collection, access_date=access_date, page=page, type_doc='website')


class ReadCube(RatchetBulk):

    def __init__(self, mongodb_uri, scielo_collection):

        db_url = urlparse.urlparse(mongodb_uri)
        conn = pymongo.MongoClient(host=db_url.hostname, port=db_url.port)
        db = conn[db_url.path[1:]]
        if db_url.username and db_url.password:
            db.authenticate(db_url.username, db_url.password)

        self.db_collection = db['accesses']
        self.bulk_data = {}
        self._collection = scielo_collection

    def send(self, slp=0):

        total = str(len(self.bulk_data))
        _logger.info('%s Records to bulk' % total)
        i = 0

        for key, value in self.bulk_data.items():
            i += 1
            _logger.debug('bulking %s of %s' % (str(i), str(total)))

            code = value['code']
            include_set = {}
            if 'journal' in value:
                include_set['journal'] = value['journal']
                del(value['journal'])

            if 'issue' in value:
                include_set['issue'] = value['issue']
                del(value['issue'])

            if 'page' in value:
                include_set['page'] = value['page']
                del(value['page'])

            if 'type' in value:
                include_set['type'] = value['type']
                del(value['type'])

            del value['code']

            data = {}
            if include_set:
                data['$set'] = include_set

            if value:
                data['$inc'] = value

            try:
                self.db_collection.update({'code': code}, data, safe=False, upsert=True)
            except:
                _logger.error('Unexpected error: {0}'.format(traceback.format_exc()))
            
            time.sleep(slp)

        self.bulk_data = None


class Local(RatchetBulk):

    def __init__(self, mongodb_uri, scielo_collection):
        self._db_url = urlparse.urlparse(mongodb_uri)
        self._collection = scielo_collection
        self.bulk_data = {}

    # sera substituido por logger.pid_manager.PidManager.pid_v3_to_pid_v2
    # em tempo de execucao
    def pid_v3_to_pid_v2(self, v3):
        return v3

    def __enter__(self):
        self._conn = pymongo.MongoClient(host=self._db_url.hostname, port=self._db_url.port)
        self._db = self._conn[self._db_url.path[1:]]
        if self._db_url.username and self._db_url.password:
            self._db.authenticate(self._db_url.username, self._db_url.password)

        self.db_collection = self._db['accesses']
        self.bulk_data = {}
        
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._conn.close()
        self._collection = None
        docs = []
        for document, items in self.bulk_data.items():
            for item in items:
                docs.append([document, item])

        for item in docs:
            del(self.bulk_data[item[0]][item[1]])

        for item in self.bulk_data.keys():
            del(self.bulk_data[item])

        self.bulk_data.clear()

    def send(self, slp=0):

        total = str(len(self.bulk_data))
        _logger.info('%s Records to bulk' % total)
        i = 0
        include_set = {}
        data = {}
        for key, value in self.bulk_data.items():
            i += 1
            _logger.debug('bulking %s of %s' % (str(i), str(total)))

            code = value['code']
            
            if 'journal' in value:
                include_set['journal'] = value['journal']
                del(value['journal'])

            if 'issue' in value:
                include_set['issue'] = value['issue']
                del(value['issue'])

            if 'page' in value:
                include_set['page'] = value['page']
                del(value['page'])

            if 'type' in value:
                include_set['type'] = value['type']
                del(value['type'])

            del value['code']

            if include_set:
                data['$set'] = include_set

            if value:
                data['$inc'] = value

            try:
                self.db_collection.update({'code': code}, data, safe=False, upsert=True)
            except:
                _logger.error('Unexpected error: {0}'.format(traceback.format_exc()))

            include_set.clear()
            value.clear()

            time.sleep(slp)

    def register_pdf_download_accesses(self, issn, pdfid, date, ip):

        self.register_download_access(pdfid, issn, date)

    def register_html_accesses(self, script, pid, date, ip):

        if script == "sci_serial":
            self.register_journal_access(pid, date)
        elif script in ["sci_abstract", "abstract"]:
            self.register_abstract_access(pid, date)
        elif script == "sci_issuetoc":
            self.register_toc_access(pid, date)
        elif script in ["sci_arttext", "article"]:
            self.register_article_access(pid, date)
        elif script in ["sci_pdf", "pdf"]:
            self.register_pdf_access(pid, date)
        elif script == "sci_home":
            self.register_home_access(pid, date)
        elif script == "sci_issues":
            self.register_issues_access(pid, date)
        elif script == "sci_alphabetic":
            self.register_alpha_access(pid, date)

    def register_access(self, parsed_line):
        if parsed_line.get("page_v3"):
            pid = self.pid_v3_to_pid_v2(parsed_line['code'])
            if pid in [parsed_line['code'], None]:
                # nao conseguiu obter o pid v2, mas
                # registra acesso para o pid v3
                # para futuramente recuperar a contagem
                self.register_v3_page_accesses(
                    parsed_line["page_v3"],
                    parsed_line['code'],
                    parsed_line['iso_date']
                )
                return
            # conseguiu obter o pid v2
            self.register_html_accesses(
                parsed_line["page_v3"],
                pid,
                parsed_line['iso_date'],
                parsed_line['ip']
            )
            return

        if parsed_line['access_type'] == "PDF":
            pdfid = parsed_line['pdf_path']
            issn = parsed_line['pdf_issn']
            self.register_pdf_download_accesses(issn, pdfid, 
                parsed_line['iso_date'], parsed_line['ip']
            )
        if parsed_line['access_type'] == "HTML":
            script = parsed_line['query_string']['script']
            pid = parsed_line['query_string']['pid']
            self.register_html_accesses(script, pid, parsed_line['iso_date'],
                parsed_line['ip']
            )

# coding: utf-8
import json
import datetime
import logging
import traceback
import time

import requests
from requests import exceptions
from pymongo import Connection

from logger.logaccess_config import *

def dorequest(url):

    attempts = 0
    while attempts <= 10:
        if attempts > 1:
            logging.warning('Retry %s' % url)
        attempts += 1

        try:
            x = requests.post('http://'+url, allow_redirects=False)
            logging.debug('Request %s' % url)
            x.close()
            x.connection.close()
            break
        except exceptions.ConnectionError as e:
            if attempts > 10:
                logging.error('ConnectionError {0}, {1}: {2}'.format(e.errno, e.strerror, url))
        except exceptions.HTTPError as e:
            if attempts > 10:
                logging.error('HTTPError {0}, {1}: {2}'.format(e.errno, e.strerror, url))
        except exceptions.TooManyRedirects as e:
            if attempts > 10:
                logging.error('ToManyRedirections {0}, {1}: {2}'.format(e.errno, e.strerror, url))
        except exceptions.Timeout as e:
            if attempts > 10:
                logging.error('Timeout {0}, {1}: {2}'.format(e.errno, e.strerror, url))
        except:
            if attempts > 10:
                logging.error('Unexpected error: {0} : URL: {1}'.format(traceback.format_exc(), url))


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

class Remote(RatchetBulk):

    def __init__(self, api_url, scielo_collection, manager_token=''):
        self._api_url = api_url
        self._manager_token = manager_token
        self.bulk_data = {}
        self._collection = scielo_collection

    def _prepare_url(self, **kwargs):

        qs = ['api_token=%s' % self._manager_token]
        if 'code' in kwargs:
            qs.append("code={0}".format(kwargs['code']))

        if 'access_date' in kwargs:
            qs.append("access_date={0}".format(kwargs['access_date']))

        if 'page' in kwargs:
            qs.append("page={0}".format(kwargs['page']))

        if 'type_doc' in kwargs:
            qs.append("type_doc={0}".format(kwargs['type_doc']))

        if 'journal' in kwargs:
            qs.append("journal={0}".format(kwargs['journal']))

        if 'issue' in kwargs:
            qs.append("issue={0}".format(kwargs['issue']))

        if 'data' in kwargs:
            qs.append("data={0}".format(kwargs['data']))

        qrs = "&".join(qs)

        url = "{0}/api/v1/{1}?{2}".format(self._api_url, kwargs['endpoint'], qrs)

        return url


    def send(self, slp=0):
        total = str(len(self.bulk_data))
        logging.info('%s Records to bulk' % total)
        i = 0
        for key, value in self.bulk_data.items():
            i += 1
            logging.debug('bulking %s of %s' % (str(i), str(total)))
            try:
                data = json.dumps(value)
            except UnicodeDecodeError:
                logging.error('Data encode error')
                continue
            url = self._prepare_url(endpoint='general/bulk', data=data)
            dorequest(url)
            time.sleep(slp)

        self.bulk_data = None


class Local(RatchetBulk):

    def __init__(self, mongodb_url, mongodb_database, scielo_collection):

        self.db_collection = Connection(mongodb_url)[mongodb_database]['accesses']
        self.bulk_data = {}
        self._collection = scielo_collection

    def send(self, slp=0):

        total = str(len(self.bulk_data))
        logging.info('%s Records to bulk' % total)
        i = 0
        for key, value in self.bulk_data.items():
            i += 1
            logging.debug('bulking %s of %s' % (str(i), str(total)))

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
                logging.error('Unexpected error: {0}'.format(traceback.format_exc()))
            
            time.sleep(slp)

        self.bulk_data = None

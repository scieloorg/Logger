# coding: utf-8

from logaccess_config import *
import requests
import datetime


class RatchetQueue(object):

    def __init__(self, api_url, manager_token='', error_log_file=None):
        error_log_file = error_log_file or '%s_error.log' % datetime.datetime.today().isoformat()[0:10]
        self._error_log_file = open(error_log_file, 'a')
        self._api_url = api_url
        self._manager_token = manager_token

    def _request(self, url):
        try:
            x = requests.post('http://'+url)
            x.close()
        except:
            self._error_log_file.write("{0}\r\n".format(url))

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

        qrs = "&".join(qs)
        url = "{0}/api/v1/{1}?{2}".format(self._api_url, kwargs['endpoint'], qrs)

        self._request(url)

    def register_download_access(self, code, issn, access_date):
        page = 'pdf'
        code = code.upper()
        issn = issn.upper()
        # Register PDF direct download access
        self._prepare_url(endpoint='general', code=code, access_date=access_date, page=page, type_doc='download')
        # Register PDF direct download access for a specific journal register
        self._prepare_url(endpoint='general', code=issn, access_date=access_date, page=page, type_doc='journal')
        # Register PDF direct download access for a collection register
        self._prepare_url(endpoint='general', code='WEBSITE', access_date=access_date, page=page)

    def register_journal_access(self, code, access_date):
        page = 'journal'
        code = code.upper()
        # Register access for journal page
        self._prepare_url(endpoint='general', code=code, access_date=access_date, page=page, type_doc='journal')
        # Register access inside collection record for page sci_serial
        self._prepare_url(endpoint='general', code='WEBSITE', access_date=access_date, page=page)

    def register_article_access(self, code, access_date):
        page = 'html'
        code = code.upper()
        # Register access for a specific article
        self._prepare_url(endpoint='general', code=code, access_date=access_date, journal=code[1:10], issue=code[1:18], page=page, type_doc='article')
        # Register access inside toc record for page sci_arttext
        self._prepare_url(endpoint='general', code=code[1:18], access_date=access_date, page=page, type_doc='toc')
        # Register access inside journal record for page sci_arttext
        self._prepare_url(endpoint='general', code=code[1:10], access_date=access_date, page=page, type_doc='journal')
        # Register access inside collection record for page sci_arttext
        self._prepare_url(endpoint='general', code='WEBSITE', access_date=access_date, page=page)

    def register_abstract_access(self, code, access_date):
        page = 'abstract'
        code = code.upper()
        # Register access for a specific article
        self._prepare_url(endpoint='general', code=code, access_date=access_date, journal=code[1:10], issue=code[1:18], page=page, type_doc='article')
        # Register access inside toc record for page sci_abstract
        self._prepare_url(endpoint='general', code=code[1:18], access_date=access_date, page=page, type_doc='toc')
        # Register access inside journal record for page sci_abstract
        self._prepare_url(endpoint='general', code=code[1:10], access_date=access_date, page=page, type_doc='journal')
        # Register access inside collection record for page sci_abstract
        self._prepare_url(endpoint='general', code='WEBSITE', access_date=access_date, page=page)

    def register_pdf_access(self, code, access_date):
        page = 'other.pdfsite'
        code = code.upper()
        # Register access for a specific article
        self._prepare_url(endpoint='general', code=code, access_date=access_date, journal=code[1:10], issue=code[1:18], page=page, type_doc='article')
        # Register access inside toc record for page pdf
        self._prepare_url(endpoint='general', code=code[1:18], access_date=access_date, page=page, type_doc='toc')
        # Register access inside journal record for page pdf
        self._prepare_url(endpoint='general', code=code[1:10], access_date=access_date, page=page, type_doc='journal')
        # Register access inside collection record for page pdf
        self._prepare_url(endpoint='general', code='WEBSITE', access_date=access_date, page=page)

    def register_toc_access(self, code, access_date):
        page = 'toc'
        code = code.upper()
        # Register access for a specific issue
        self._prepare_url(endpoint='general', code=code, access_date=access_date, journal=code[0:9], page=page, type_doc='toc')
        # Register access inside journal record for page sci_issuetoc
        self._prepare_url(endpoint='general', code=code[0:9], access_date=access_date, page=page, type_doc='journal')
        # Register access inside collection record for page sci_issuetoc
        self._prepare_url(endpoint='general', code='WEBSITE', access_date=access_date, page=page)

    def register_home_access(self, code, access_date):
        page = 'home'
        code = code.upper()
        # Register access inside collection record for page sci_home
        self._prepare_url(endpoint='general', code='WEBSITE', access_date=access_date, page=page)

    def register_issues_access(self, code, access_date):
        page = 'issues'
        code = code.upper()
        # Register access inside journal record for page issues
        self._prepare_url(endpoint='general', code=code[0:9], access_date=access_date, page=page, type_doc='journal')
        # Register access inside collection record for page issues
        self._prepare_url(endpoint='general', code='WEBSITE', access_date=access_date, page=page)

    def register_alpha_access(self, code, access_date):
        page = 'alpha'
        code = code.upper()
        # Register access inside collection record for page alphabetic list
        self._prepare_url(endpoint='general', code='WEBSITE', access_date=access_date, page=page)

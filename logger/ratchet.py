from logaccess_config import *
import gevent
from gevent import monkey
monkey.patch_all()
import urllib2

api_url = "http://{0}:{1}/".format(RATCHET_DOMAIN, RATCHET_PORT)
site_domain = SITE_DOMAIN


class RatchetQueue(object):

    def __init__(self, limit=10):
        self._queue = []
        self._queue_size = 0
        self._queue_limit = limit

    def _request(self, url):
        qrs = url.split('?')
        req = urllib2.Request("{0}".format(qrs[0]), qrs[1])
        urllib2.urlopen(req)

    def _send(self):
        gevent.joinall(self._queue)

    def add_url(self, **kwargs):

        qs = []
        if 'code' in kwargs:
            qs.append("code={0}".format(kwargs['code']))

        if 'access_date' in kwargs:
            qs.append("access_date={0}".format(kwargs['access_date']))

        if 'page' in kwargs:
            qs.append("page={0}".format(kwargs['page']))

        if 'journal' in kwargs:
            qs.append("journal={0}".format(kwargs['journal']))

        if 'issue' in kwargs:
            qs.append("issue={0}".format(kwargs['issue']))

        qrs = "&".join(qs)
        url = "{0}api/v1/{1}?{2}".format(api_url, kwargs['endpoint'], qrs)

        self._queue.append(gevent.spawn(self._request, url))
        if self._queue_size > self._queue_limit:
            self._queue_size = 0
            self._send()
        else:
            self._queue_size += 1

    def register_download_access(self, code, issn, access_date):
        page = 'download'
        # Register PDF direct download access
        self.add_url(endpoint='general', code=code, access_date=access_date)
        # Register PDF direct download access for a specific journal register
        self.add_url(endpoint='general', code=issn, access_date=access_date, page=page)
        # Register PDF direct download access for a collection register
        self.add_url(endpoint='general', code=site_domain, access_date=access_date, page=page)

    def register_journal_access(self, code, access_date):
        page = 'journal'
        # Register access for a specific journal
        self.add_url(endpoint='journal', code=code, access_date=access_date)
        # Register access for journal page
        self.add_url(endpoint='general', code=code, access_date=access_date, page=page)
        # Register access inside collection record for page sci_serial
        self.add_url(endpoint='general', code=site_domain, access_date=access_date, page=page)

    def register_article_access(self, code, access_date):
        page = 'fulltext'
        # Register access for a specific article
        self.add_url(endpoint='article', code=code, access_date=access_date, journal=code[0:9], issue=code[0:17])
        # Register access inside journal record for page sci_arttext
        self.add_url(endpoint='general', code=code[0:9], access_date=access_date, page=page)
        # Register access inside collection record for page sci_arttext
        self.add_url(endpoint='general', code=site_domain, access_date=access_date, page=page)

    def register_abstract_access(self, code, access_date):
        page = 'abstract'
        # Register access for a specific article
        self.add_url(endpoint='article', code=code, access_date=access_date, journal=code[0:9], issue=code[0:17])
        # Register access inside journal record for page sci_abstract
        self.add_url(endpoint='general', code=code[0:9], access_date=access_date, page=page)
        # Register access inside collection record for page sci_abstract
        self.add_url(endpoint='general', code=site_domain, access_date=access_date, page=page)

    def register_pdf_access(self, code, access_date):
        page = 'pdf'
        # Register access for a specific article
        self.add_url(endpoint='pdf', code=code, access_date=access_date, journal=code[0:9], issue=code[0:17])
        # Register access inside journal record for page pdf
        self.add_url(endpoint='general', code=code[0:9], access_date=access_date, page=page)
        # Register access inside collection record for page pdf
        self.add_url(endpoint='general', code=site_domain, access_date=access_date, page=page)

    def register_toc_access(self, code, access_date):
        page = 'toc'
        # Register access for a specific issue
        self.add_url(endpoint='issue', code=code, access_date=access_date, journal=code[0:9])
        # Register access inside journal record for page sci_issuetoc
        self.add_url(endpoint='general', code=code[0:9], access_date=access_date, page=page)
        # Register access inside collection record for page sci_issuetoc
        self.add_url(endpoint='general', code=site_domain, access_date=access_date, page=page)

    def register_home_access(self, code, access_date):
        page = 'home'
        # Register access inside collection record for page sci_home
        self.add_url(endpoint='general', code=site_domain, access_date=access_date, page=page)

    def register_issues_access(self, code, access_date):
        page = 'issues'
        # Register access inside journal record for page issues
        self.add_url(endpoint='general', code=code[0:9], access_date=access_date, page=page)
        # Register access inside collection record for page issues
        self.add_url(endpoint='general', code=site_domain, access_date=access_date, page=page)

    def register_alpha_access(self, code, access_date):
        page = 'alpha'
        # Register access inside collection record for page alphabetic list
        self.add_url(endpoint='general', code=site_domain, access_date=access_date, page=page)

from logaccess_config import *

import urllib2

api_url = "http://{0}:{1}/".format(RATCHET_DOMAIN, RATCHET_PORT)
site_domain = SITE_DOMAIN


def ratchet_post(**kwargs):

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
    req = urllib2.Request("{0}api/v1/{1}?".format(api_url, kwargs['endpoint']), qrs)
    urllib2.urlopen(req)


def register_download_access(code, issn, access_date):
    page = 'download'
    # Register PDF direct download access
    ratchet_post(endpoint='general', code=code, access_date=access_date)
    # Register PDF direct download access for a specific journal register
    ratchet_post(endpoint='general', code=issn, access_date=access_date, page=page)
    # Register PDF direct download access for a collection register
    ratchet_post(endpoint='general', code=site_domain, access_date=access_date, page=page)


def register_journal_access(code, access_date):
    page = 'journal'
    # Register access for a specific journal
    ratchet_post(endpoint='journal', code=code, access_date=access_date)
    # Register access for journal page
    ratchet_post(endpoint='general', code=code, access_date=access_date, page=page)
    # Register access inside collection record for page sci_serial
    ratchet_post(endpoint='general', code=site_domain, access_date=access_date, page=page)


def register_article_access(code, access_date):
    page = 'fulltext'
    # Register access for a specific article
    ratchet_post(endpoint='article', code=code, access_date=access_date, journal=code[0:9], issue=code[0:17])
    # Register access inside journal record for page sci_arttext
    ratchet_post(endpoint='general', code=code[0:9], access_date=access_date, page=page)
    # Register access inside collection record for page sci_arttext
    ratchet_post(endpoint='general', code=site_domain, access_date=access_date, page=page)


def register_abstract_access(code, access_date):
    page = 'abstract'
    # Register access for a specific article
    ratchet_post(endpoint='article', code=code, access_date=access_date, journal=code[0:9], issue=code[0:17])
    # Register access inside journal record for page sci_abstract
    ratchet_post(endpoint='general', code=code[0:9], access_date=access_date, page=page)
    # Register access inside collection record for page sci_abstract
    ratchet_post(endpoint='general', code=site_domain, access_date=access_date, page=page)


def register_pdf_access(code, access_date):
    page = 'pdf'
    # Register access for a specific article
    ratchet_post(endpoint='pdf', code=code, access_date=access_date, journal=code[0:9], issue=code[0:17])
    # Register access inside journal record for page pdf
    ratchet_post(endpoint='general', code=code[0:9], access_date=access_date, page=page)
    # Register access inside collection record for page pdf
    ratchet_post(endpoint='general', code=site_domain, access_date=access_date, page=page)


def register_toc_access(code, access_date):
    page = 'toc'
    # Register access for a specific issue
    ratchet_post(endpoint='issue', code=code, access_date=access_date, journal=code[0:9])
    # Register access inside journal record for page sci_issuetoc
    ratchet_post(endpoint='general', code=code[0:9], access_date=access_date, page=page)
    # Register access inside collection record for page sci_issuetoc
    ratchet_post(endpoint='general', code=site_domain, access_date=access_date, page=page)


def register_home_access(code, access_date):
    page = 'home'
    # Register access inside collection record for page sci_home
    ratchet_post(endpoint='general', code=site_domain, access_date=access_date, page=page)


def register_issues_access(code, access_date):
    page = 'issues'
    # Register access inside journal record for page issues
    ratchet_post(endpoint='general', code=code[0:9], access_date=access_date, page=page)
    # Register access inside collection record for page issues
    ratchet_post(endpoint='general', code=site_domain, access_date=access_date, page=page)


def register_alpha_access(code, access_date):
    page = 'alpha'
    # Register access inside collection record for page alphabetic list
    ratchet_post(endpoint='general', code=site_domain, access_date=access_date, page=page)

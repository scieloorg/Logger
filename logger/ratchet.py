from logaccess_config import *

import urllib2

api_url = "http://{0}:{1}/".format(RATCHET_DOMAIN, RATCHET_PORT)
site_domain = SITE_DOMAIN


def register_journal_page_access(code, access_date):
    qrs = "code={0}&access_date={1}".format(code, access_date)
    req = urllib2.Request("{0}api/v1/journal".format(api_url), qrs)
    urllib2.urlopen(req)
    qrs = "code={0}&page=sci_serial&access_date={1}".format(code[0:9], access_date)
    req = urllib2.Request("{0}api/v1/general".format(api_url), qrs)
    urllib2.urlopen(req)
    qrs = "code={0}&page=sci_serial&access_date={1}".format(site_domain, access_date)
    req = urllib2.Request("{0}api/v1/general".format(api_url), qrs)
    urllib2.urlopen(req)


def register_article_page_access(code, access_date):
    qrs = "code={0}&journal={1}&issue={2}&access_date={3}".format(code, code[0:9], code[0:17], access_date)
    req = urllib2.Request("{0}api/v1/article".format(api_url), qrs)
    urllib2.urlopen(req)
    qrs = "code={0}&page=sci_arttext&access_date={1}".format(code[0:9], access_date)
    req = urllib2.Request("{0}api/v1/general".format(api_url), qrs)
    urllib2.urlopen(req)
    qrs = "code={0}&page=sci_arttext&access_date={1}".format(site_domain, access_date)
    req = urllib2.Request("{0}api/v1/general".format(api_url), qrs)
    urllib2.urlopen(req)

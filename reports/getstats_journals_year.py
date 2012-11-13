#!/usr/bin/env python
from logaccess_config import *
from pymongo import Connection
import urllib2
import json
from collections import defaultdict


def dsum(*dicts):
    ret = defaultdict(int)
    for d in dicts:
        for k, v in d.items():
            ret[k] += v
    return dict(ret)


def sumarize_by_year(stats, accesses):

    for key, value in stats.items():

        year = key[4:8]

        if key[:3] == 'art':
            html_stats = accesses.setdefault('html', {})
            html_stats.setdefault(year, 0)
            html_stats[year] += value

        if key[:3] == 'dwn':
            pdf_stats = accesses.setdefault('pdf', {})
            pdf_stats.setdefault(year, 0)
            pdf_stats[year] += value


def get_allowed_issns(collections):

    allowed = {}
    for coll_code in collections:
        url = 'http://webservices.scielo.org/scieloorg/_design/couchdb/_view/title?startkey=["%s"]&endkey=["%s",{}]' % (coll_code, coll_code)
        titles = json.loads(urllib2.urlopen(url).read())

        for title in titles['rows']:
            allowed.setdefault(title['value']['issn'].upper(), title['value']['title'])

    return allowed

conn = Connection('192.168.1.85', MONGODB_PORT)

collections = ['scl', 'sss', 'spa']

allowed_issns = get_allowed_issns(collections)
stats_dict = {}
for coll_code in collections:
    db = conn[coll_code + "_accesslog"]
    analytics = db[coll_code + "_analytics"]

    journals_stats = analytics.find({'serial': {'$exists': True}})

    for stat in journals_stats:
        issn = stat['serial'].upper()

        if issn in allowed_issns:
            serial = stats_dict.setdefault(issn, {})
            collection = serial.setdefault(coll_code, {})
            sumarize_by_year(stat, stats_dict[issn][coll_code])

for journal, collections in stats_dict.items():
    for collection, doc_types in collections.items():
        for doc_type, years in doc_types.items():
            for year, accesses in years.items():
                print u"{0}|{1}|{2}|{3}|{4}|{5}".format(journal, allowed_issns[journal], collection, doc_type, year, accesses).encode("iso-8859-1")

#!/usr/bin/env python
from logaccess_config import *
from pymongo import Connection


def sumarize_by_month(stats):
    sumarized = {}
    for key, value in stats.items():

        month = key[4:10]
        if month:
            if key[:3] == 'htm':
                html_stats = sumarized.setdefault('html', {})
                html_stats.setdefault(month, 0)
                html_stats[month] += value

            if key[:3] == 'pdf':
                pdf_stats = sumarized.setdefault('pdf', {})
                pdf_stats.setdefault(month, 0)
                pdf_stats[month] += value

            if key[:3] == 'epu':
                pdf_stats = sumarized.setdefault('epu', {})
                pdf_stats.setdefault(month, 0)
                pdf_stats[month] += value

    return sumarized

conn = Connection('192.168.1.85', MONGODB_PORT)

collections = ['bks']

stats_dict = {}
for coll_code in collections:
    db = conn[coll_code + "_accesslog"]
    analytics = db[coll_code + "_analytics"]

    books_stats = analytics.find({'context': 'book'})

    for stat in books_stats:
        book = stat['code'].lower()
        stats_dict[book] = sumarize_by_month(stat)

for book, doc_types in stats_dict.items():
    for doc_type, months in doc_types.items():
        for month, accesses in months.items():
            print u"{0}|{1}|{2}|{3}".format(book, doc_type, month, accesses).encode("utf-8")

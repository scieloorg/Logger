#!/usr/bin/env python
from logaccess_config import *
from pymongo import Connection
import urllib2
import json


def get_books():
    query1 = urllib2.urlopen('http://192.168.1.12:5984/scielobooks_1a/_design/scielobooks/_view/books')
    jsondocs = json.loads(query1.read())

    books = {}
    for reg in jsondocs['rows']:  # rows e uma array (lista) de registros no JSON
        book = books.setdefault(reg['id'], {})
        book['editor'] = reg['value']['publisher']
        book['year'] = 'not defined'
        if 'year' in reg['value']:
            book['year'] = reg['value']['year'][0:10]

        book['creation_date'] = 'not defined'
        if 'creation_date' in reg['value']:
            book['creation_date'] = reg['value']['creation_date'][0:10]

    return books


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

books = get_books()

conn = Connection('192.168.1.85', MONGODB_PORT)

collections = ['bks']


stats_dict = {}
for coll_code in collections:
    db = conn[coll_code + "_accesslog"]
    analytics = db[coll_code + "_analytics"]

    books_stats = analytics.find({'context': 'book'})

    for stat in books_stats:
        book_code = stat['code'].lower()
        stats_dict[book_code] = sumarize_by_month(stat)

print "code|publicated at|created at|editor|access type|month access|accesses"
for book_code, doc_types in stats_dict.items():
    if book_code in books:
        for doc_type, months in doc_types.items():
            for month, accesses in months.items():
                print u"{0}|{1}|{2}|{3}|{4}|{5}|{6}".format(book_code,
                                                        books[book_code]['year'],
                                                        books[book_code]['creation_date'],
                                                        books[book_code]['editor'],
                                                        doc_type,
                                                        month,
                                                        accesses).encode("utf-8")

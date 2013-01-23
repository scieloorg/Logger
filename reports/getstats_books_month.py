#!/usr/bin/env python
from logaccess_config import *
from pymongo import Connection
import urllib2
import json
import argparse


def get_books(api_host='localhost', api_port='5984'):
    query1 = urllib2.urlopen('http://{0}:{1}/scielobooks_1a/_design/scielobooks/_view/books'.format(api_host, api_port))
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


def get_collection(mongodb_host='localhost',
               mongodb_port=27017,
               mongodb_database='bks',
               mongodb_collection='bks'):

    conn = Connection(mongodb_host, mongodb_port)
    db = conn[mongodb_database + "_accesslog"]
    coll = db[mongodb_collection + "_analytics"]

    return coll


def main(*args, **xargs):

    books = get_books(api_host=xargs['api_host'],
                      api_port=int(xargs['api_port']))

    analytics = get_collection(mongodb_host=xargs['mongodb_host'],
                               mongodb_port=int(xargs['mongodb_port']))

    books_stats = analytics.find({'context': 'book'})

    stats_dict = {}
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

parser = argparse.ArgumentParser(description="Create an access report")
parser.add_argument('--api_host', default='localhost', help='The CouchDB API hostname')
parser.add_argument('--api_port', default='5984', help='The CouchDB API port')
parser.add_argument('--mongodb_host', default='localhost', help='The MongoDB accesslog database hostname')
parser.add_argument('--mongodb_port', default='27017', help='The MongoDB accesslog database port')

args = parser.parse_args()

if __name__ == "__main__":
    main(api_host=args.api_host,
         api_port=args.api_port,
         mongodb_host=args.mongodb_host,
         mongodb_port=args.mongodb_port)

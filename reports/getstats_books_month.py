#!/usr/bin/env python
import os
import urllib2
import json
import argparse

import pymongo


def get_books(api_host='localhost', api_port='5984'):
    try:
        query1 = urllib2.urlopen('http://{0}:{1}/scielobooks_1a/_design/scielobooks/_view/books'.format(api_host, api_port))
    except urllib2.URLError:
        print "API connection refused, please check the script configurations running ./{0} -h".format(os.path.basename(__file__))
        raise

    jsondocs = json.loads(query1.read())

    books = {}
    for reg in jsondocs['rows']:  # rows e uma array (lista) de registros no JSON
        book = books.setdefault(reg['id'], {})
        book['editor'] = reg['value']['publisher']
        book['title'] = reg['value']['title']

        creators = []
        if 'creators' in reg['value']:
            for creator in reg['value']['creators']:
                creators.append(creator[1][1])
        book['creators'] = '; '.join(creators)

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

    try:
        conn = pymongo.Connection(mongodb_host, mongodb_port)
    except pymongo.errors.AutoReconnect:
        print "MongoDB connection refused, please check the script configurations running ./{0} -h".format(os.path.basename(__file__))
        raise

    db = conn[mongodb_database + "_accesslog"]
    coll = db[mongodb_collection + "_analytics"]

    return coll


def main(*args, **xargs):

    books = get_books(api_host=xargs['api_host'],
                      api_port=int(xargs['api_port']))

    analytics = get_collection(mongodb_host=xargs['mongodb_host'],
                               mongodb_port=int(xargs['mongodb_port']))

    report = open(xargs['output_file'], 'w')
    books_stats = analytics.find({'context': 'book'})

    stats_dict = {}
    for stat in books_stats:
        book_code = stat['code'].lower()
        stats_dict[book_code] = sumarize_by_month(stat)

    report.write(u"code|title|authors|publicated at|created at|editor|access type|month access|accesses\r\n")

    for book_code, doc_types in stats_dict.items():
        if book_code in books:
            for doc_type, months in doc_types.items():
                for month, accesses in months.items():
                    report.write(u"{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|{8}\r\n".format(book_code,
                                                            books[book_code]['title'],
                                                            books[book_code]['creators'],
                                                            books[book_code]['year'],
                                                            books[book_code]['creation_date'],
                                                            books[book_code]['editor'],
                                                            doc_type,
                                                            month,
                                                            accesses).encode("utf-8"))

parser = argparse.ArgumentParser(description="Create an access report")
parser.add_argument('--api_host', default='localhost', help='The CouchDB API hostname')
parser.add_argument('--api_port', default='5984', help='The CouchDB API port')
parser.add_argument('--mongodb_host', default='localhost', help='The MongoDB accesslog database hostname')
parser.add_argument('--mongodb_port', default='27017', help='The MongoDB accesslog database port')
parser.add_argument('--output_file', default='report.txt', help='File name where the report will be stored')

args = parser.parse_args()

if __name__ == "__main__":
    main(api_host=args.api_host,
         api_port=args.api_port,
         mongodb_host=args.mongodb_host,
         mongodb_port=args.mongodb_port,
         output_file=args.output_file)

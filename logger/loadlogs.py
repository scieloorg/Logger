#!/usr/bin/env python
# coding: utf-8
import os
import argparse

from pymongo import Connection

from ratchet import *
from accesschecker import AccessChecker, TimedSet, checkdatelock

def get_proc_collection():
    """
    The proc collection is a mongodb database that keeps the name of each
    processed file, to avoid processing these files again.
    """
    conn = Connection(LOGGER_DATABASE_DOMAIN, LOGGER_DATABASE_PORT)
    db = conn['proc_files']
    coll = db[LOGGER_DATABASE_COLLECTION]
    coll.ensure_index('file_name')

    return coll


def get_proc_robots_collection():
    """
    The robots collection is a mongodb database that keeps the count of each
    robots occurences record for each url + ip address.
    """
    conn = Connection(LOGGER_DATABASE_DOMAIN, LOGGER_DATABASE_PORT)
    db = conn['robots']
    coll = db[LOGGER_DATABASE_COLLECTION]
    coll.ensure_index('code')

    return coll


def register_pdf_download_accesses(ratchet_queue, issn, pdfid, date, ip):
    ratchet_queue.register_download_access(pdfid, ','.join(issn), date)


def register_html_accesses(ratchet_queue, script, pid, date, ip):

    if script == "sci_serial":
        ratchet_queue.register_journal_access(','.join(pid), date)
    elif script == "sci_abstract":
        ratchet_queue.register_abstract_access(pid, date)
    elif script == "sci_issuetoc":
        ratchet_queue.register_toc_access(pid, date)
    elif script == "sci_arttext":
        ratchet_queue.register_article_access(pid, date)
    elif script == "sci_pdf":
        ratchet_queue.register_pdf_access(pid, date)
    elif script == "sci_home":
        ratchet_queue.register_home_access(pid, date)
    elif script == "sci_issues":
        ratchet_queue.register_issues_access(pid, date)
    elif script == "sci_alphabetic":
        ratchet_queue.register_alpha_access(pid, date)


def main(*args, **xargs):
    ts = TimedSet(expired=checkdatelock)
    ac = AccessChecker(xargs['collection'])
    proc_coll = get_proc_collection()
    proc_robots_coll = get_proc_robots_collection()

    for logfile in os.popen('ls %s/*' % LOG_DIR):

        logfile = logfile.strip()

        # Verifica se arquivo já foi processado.
        if proc_coll.find({'file_name': logfile}).count() > 0:
            continue

        # Registra em base de dados de arquivos processados o novo arquivo.
        print "processing: {0}".format(logfile)
        proc_coll.insert({'file_name': logfile})

        with open(logfile, 'rb') as f:
            rq = RatchetQueue(error_log_file=xargs['error_log_file'])
            for raw_line in f:
                parsed_line = ac.parsed_access(raw_line)

                if not parsed_line:
                    continue

                locktime = 10
                if parsed_line['access_type'] == "PDF":
                    locktime = 30

                if xargs['ttl']:
                    try:
                        lockid = parsed_line['code']+parsed_line['script']
                        ts.add(lockid,
                               parsed_line['iso_datetime'], locktime)
                    except ValueError:
                        continue

                if parsed_line['access_type'] == "PDF":
                    pdfid = parsed_line['pdf_path']
                    issn = parsed_line['pdf_issn']
                    register_pdf_download_accesses(rq,
                                                   issn,
                                                   pdfid,
                                                   parsed_line['iso_date'],
                                                   parsed_line['ip'])

                if parsed_line['access_type'] == "HTML":
                    script = parsed_line['query_string']['script']
                    pid = parsed_line['query_string']['pid']
                    register_html_accesses(rq,
                                           script,
                                           pid,
                                           parsed_line['iso_date'],
                                           parsed_line['ip'])

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Run the processing to read the access log files and register accesses into Ratchet")
    parser.add_argument('-t',
                        '--ttl',
                        action='store_true',
                        default=False,
                        help='Indicates if the processing will use a lock controller to control the acccesses according to Counter Project')
    parser.add_argument('-c',
                        '--collection',
                        default=None,
                        help='Three letters collection id')
    parser.add_argument('-l',
                        '--error_log_file',
                        default=None,
                        help='error log filename')
    args = parser.parse_args()

    main(ttl=bool(args.ttl),
         collection=args.collection,
         error_log_file=args.error_log_file)

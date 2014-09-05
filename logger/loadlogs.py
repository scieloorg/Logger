#!/usr/bin/env python
# coding: utf-8
import os
import argparse
import requests
import datetime

from pymongo import Connection

from ratchet import *
from accesschecker import AccessChecker, TimedSet, checkdatelock


def _config_logging(logging_level='INFO', logging_file=None):

    allowed_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    logging_config = {
        'level': allowed_levels.get(logging_level, 'INFO'),
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    }

    if logging_file:
        logging_config['filename'] = logging_file

    logging.basicConfig(**logging_config)


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


def register_pdf_download_accesses(interface, issn, pdfid, date, ip):

    interface.register_download_access(pdfid, issn, date)


def register_html_accesses(interface, script, pid, date, ip):

    if script == "sci_serial":
        interface.register_journal_access(pid, date)
    elif script == "sci_abstract":
        interface.register_abstract_access(pid, date)
    elif script == "sci_issuetoc":
        interface.register_toc_access(pid, date)
    elif script == "sci_arttext":
        interface.register_article_access(pid, date)
    elif script == "sci_pdf":
        interface.register_pdf_access(pid, date)
    elif script == "sci_home":
        interface.register_home_access(pid, date)
    elif script == "sci_issues":
        interface.register_issues_access(pid, date)
    elif script == "sci_alphabetic":
        interface.register_alpha_access(pid, date)


def register_access(interface, parsed_line):

    if parsed_line['access_type'] == "PDF":
        pdfid = parsed_line['pdf_path']
        issn = parsed_line['pdf_issn']
        register_pdf_download_accesses(interface,
                                       issn,
                                       pdfid,
                                       parsed_line['iso_date'],
                                       parsed_line['ip'])

    if parsed_line['access_type'] == "HTML":
        script = parsed_line['query_string']['script']
        pid = parsed_line['query_string']['pid']
        register_html_accesses(interface,
                               script,
                               pid,
                               parsed_line['iso_date'],
                               parsed_line['ip'])


def ratchet_is_working(url):

    try:
        response = requests.get('http://'+url)
    except:
        return None

    if not response.text == 'Ratchet API':
        return None

    return True


def are_valid_api_urls(ratchet_api_counter_url, ratchet_api_url):

    if ratchet_api_counter_url == ratchet_api_url:
        return None

    if ratchet_api_counter_url and not ratchet_is_working(ratchet_api_counter_url):
        return None

    if ratchet_api_url and not ratchet_is_working(ratchet_api_url):
        return None

    return True


def onebyone(*args, **xargs):
    error_log_file = xargs['error_log_file']
    ratchet_api_counter_url = xargs['ratchet_api_counter_url']
    ratchet_api_url = xargs['ratchet_api_url']
    ratchet_api_manager_token = xargs['ratchet_api_manager_token']

    if not are_valid_api_urls(ratchet_api_counter_url, ratchet_api_url):
        print "Error: Check the Ratchet api urls for TTL and Normal access."
        return None

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
            if ratchet_api_url:
                rq_all = RatchetOneByOne(
                    ratchet_api_url,
                    xargs['collection'],
                    manager_token=ratchet_api_manager_token,
                )

            if ratchet_api_counter_url:
                rq_ttl = RatchetOneByOne(
                    ratchet_api_counter_url,
                    xargs['collection'],
                    manager_token=ratchet_api_manager_token,
                )

            for raw_line in f:
                parsed_line = ac.parsed_access(raw_line)

                if not parsed_line:
                    continue

                if ratchet_api_url:
                    register_access(rq_all, parsed_line)

                if ratchet_api_counter_url:
                    locktime = 10
                    if parsed_line['access_type'] == "PDF":
                        locktime = 30
                    try:
                        lockid = '_'.join([parsed_line['ip'],
                                           parsed_line['code'],
                                           parsed_line['script']])
                        ts.add(lockid, parsed_line['iso_datetime'], locktime)
                        register_access(rq_ttl, parsed_line)
                    except ValueError:
                        continue


def bulk(*args, **xargs):
    error_log_file = xargs['error_log_file']
    ratchet_api_counter_url = xargs['ratchet_api_counter_url']
    ratchet_api_url = xargs['ratchet_api_url']
    ratchet_api_manager_token = xargs['ratchet_api_manager_token']

    if not are_valid_api_urls(ratchet_api_counter_url, ratchet_api_url):
        print "Error: Check the Ratchet api urls for TTL and Normal access."
        return None

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

        if ratchet_api_url:
            rq_all = RatchetBulk(
                ratchet_api_url,
                xargs['collection'],
                manager_token=ratchet_api_manager_token
            )

        if ratchet_api_counter_url:
            rq_ttl = RatchetBulk(
                ratchet_api_counter_url,
                xargs['collection'],
                manager_token=ratchet_api_manager_token
            )

        with open(logfile, 'rb') as f:

            for raw_line in f:
                parsed_line = ac.parsed_access(raw_line)

                if not parsed_line:
                    continue

                if ratchet_api_url:
                    register_access(rq_all, parsed_line)

                if ratchet_api_counter_url:
                    locktime = 10
                    if parsed_line['access_type'] == "PDF":
                        locktime = 30
                    try:
                        lockid = '_'.join([parsed_line['ip'],
                                           parsed_line['code'],
                                           parsed_line['script']])
                        ts.add(lockid, parsed_line['iso_datetime'], locktime)
                        register_access(rq_ttl, parsed_line)
                    except ValueError:
                        continue

        if ratchet_api_url:
            rq_all.send()
        if ratchet_api_counter_url:
            rq_ttl.send()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Run the processing to read the access log files and register accesses into Ratchet"
    )
    parser.add_argument(
        '-t',
        '--ttl',
        default=None,
        help='Ratchet API URL (localhost:8081) to register accesses according to Counter rules.'
    )
    parser.add_argument(
        '-r',
        '--ratchet_api_url',
        default=None,
        help='Ratchet API URL (localhost:8080) to register accesses.'
    )
    parser.add_argument(
        '-a',
        '--ratchet_api_manager_token',
        default=None,
        help='Ratchet API Manager Token.'
    )
    parser.add_argument(
        '-c',
        '--collection',
        default=None,
        help='Three letters collection id'
    )
    parser.add_argument(
        '-m',
        '--register_mode',
        default='bulk',
        choices=['bulk', 'onebyone'],
        help='Define how to send the accesses to ratchet API'
    )
    parser.add_argument(
        '--logging_file',
        '-o',
        default='/tmp/logger_%s.log' % datetime.datetime.now().isoformat()[0:10],
        help='Full path to the log file'
    )
    parser.add_argument(
        '--logging_level',
        '-l',
        default='DEBUG',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logggin level'
    )

    args = parser.parse_args()

    _config_logging(args.logging_level, args.logging_file)

    if args.register_mode == 'bulk':
        main = bulk
    elif args.register_mode == 'onebyone':
        main = onebyone

    main(ratchet_api_counter_url=args.ttl,
         ratchet_api_url=args.ratchet_api_url,
         ratchet_api_manager_token=args.ratchet_api_manager_token,
         collection=args.collection,
         error_log_file=args.error_log_file)

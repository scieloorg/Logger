#!/usr/bin/env python
# coding: utf-8
import os
import argparse
import requests
import datetime
import logging
import urlparse

import pymongo

from logger.ratchet import Remote, Local
from logger.accesschecker import AccessChecker, TimedSet, checkdatelock
from logger import utils

_logger = logging.getLogger(__name__)

config = utils.Configuration.from_env()
settings = dict(config.items())['app:main']

SLEEP = float(settings.get('sleep', 0))
COUNTER_COMPLIANT = int(settings.get('counter_compliant', 0))
MONGO_URI = settings.get('mongo_uri', 'mongodb://127.0.0.1:27017/database_name')
MONGO_URI_COUNTER = settings.get('mongo_uri_counter', 'mongodb://127.0.0.1:27017/database_name')
LOG_DIR = settings['log_dir']

def _config_logging(logging_level='INFO', logging_file=None):

    allowed_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _logger.setLevel(allowed_levels.get(logging_level, 'INFO'))

    if logging_file:
        hl = logging.FileHandler(logging_file, mode='a')
    else:
        hl = logging.StreamHandler()

    hl.setFormatter(formatter)
    hl.setLevel(allowed_levels.get(logging_level, 'INFO'))

    _logger.addHandler(hl)


def mongodb_connect(collection):

    db_url = urlparse.urlparse(MONGO_URI)
    conn = pymongo.MongoClient(host=db_url.hostname, port=db_url.port)
    db = conn[db_url.path[1:]]
    if db_url.username and db_url.password:
        db.authenticate(db_url.username, db_url.password)

    return db[collection]

def get_proc_collection():
    """
    The proc collection is a mongodb database that keeps the name of each
    processed file, to avoid processing these files again.
    """
    coll =  mongodb_connect('proc_files')
    coll.ensure_index('file_name')

    return coll


def get_proc_robots_collection():
    """
    The robots collection is a mongodb database that keeps the count of each
    robots occurences record for each url + ip address.
    """
    coll =  mongodb_connect('robots')
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


def bulk(collection=None):
    _logger.info('Running as bulk')

    if COUNTER_COMPLIANT:
        ts = TimedSet(expired=checkdatelock)

    ac = AccessChecker(collection)

    proc_coll = get_proc_collection()
    proc_robots_coll = get_proc_robots_collection()

    for logfile in os.popen('ls %s/*' % LOG_DIR):

        logfile = logfile.strip()

        # Verifica se arquivo já foi processado.
        if proc_coll.find({'file_name': logfile}).count() > 0:
            _logger.debug('File already processe %s' % logfile)
            continue

        # Registra em base de dados de arquivos processados o novo arquivo.
        _logger.info("Processing: %s" % logfile)
        proc_coll.insert({'file_name': logfile})

        rq = Local(MONGO_URI, collection)

        with open(logfile, 'rb') as f:

            log_file_line = 0
            for raw_line in f:
                log_file_line += 1
                _logger.debug("Reading line {0} from file {1}".format(str(log_file_line), logfile))
                parsed_line = ac.parsed_access(raw_line)

                if not parsed_line:
                    continue

                if COUNTER_COMPLIANT:
                    # Counter Mode Accesses
                    locktime = 10
                    if parsed_line['access_type'] == "PDF":
                        locktime = 30
                    try:
                        lockid = '_'.join([parsed_line['ip'],
                                           parsed_line['code'],
                                           parsed_line['script']])
                        ts.add(lockid, parsed_line['iso_datetime'], locktime)
                        register_access(rq, parsed_line)
                    except ValueError:
                        continue
                else:
                    # SciELO Mode Accesses
                    register_access(rq, parsed_line)


        rq.send(slp=SLEEP)
        del(rq)

def main():

    parser = argparse.ArgumentParser(
        description="Run the processing to read the access log files and register accesses into Ratchet"
    )

    parser.add_argument(
        '-c',
        '--collection',
        default=None,
        help='Three letters collection id'
    )

    parser.add_argument(
        '--logging_file',
        '-o',
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

    bulk(collection=args.collection)

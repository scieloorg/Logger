#!/usr/bin/env python
# coding: utf-8
import os
import argparse
import requests
import datetime
import logging
import urlparse

import pymongo

from logger.ratchet import Local
from logger.accesschecker import AccessChecker, TimedSet, checkdatelock
from logger import utils

logger = logging.getLogger(__name__)

config = utils.Configuration.from_env()
settings = dict(config.items())['app:main']

COUNTER_COMPLIANT = int(settings.get('counter_compliant', 0))
COUNTER_COMPLIANT_SKIPPED_LOG_DIR = settings.get('counter_compliant_skipped_log_dir', None)
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

    logger.setLevel(allowed_levels.get(logging_level, 'INFO'))

    if logging_file:
        hl = logging.FileHandler(logging_file, mode='a')
    else:
        hl = logging.StreamHandler()

    hl.setFormatter(formatter)
    hl.setLevel(allowed_levels.get(logging_level, 'INFO'))

    logger.addHandler(hl)


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


class Bulk(object):

    def __init__(self, mongo_uri, collection, counter_compliant=None, skipped_log_dir=None):
        self._mongo_uri = mongo_uri
        self._proc_coll = self.get_proc_collection()
        self._collection = collection
        self._counter_compliant = counter_compliant
        self._skipped_log_dir = None
        if skipped_log_dir:
            now = datetime.datetime.now().isoformat()
            skipped_log = '/'.join([skipped_log_dir, now]).replace('//', '/')
            try:
                self._skipped_log_dir = open(skipped_log, 'w')
            except ValueError:
                raise "Invalid directory or file name: %s" % skipped_log

    def _mongodb_connect(self, mdb_database):

        db_url = urlparse.urlparse(self._mongo_uri)
        conn = pymongo.MongoClient(host=db_url.hostname, port=db_url.port)
        db = conn[db_url.path[1:]]
        if db_url.username and db_url.password:
            db.authenticate(db_url.username, db_url.password)

        return db['scielo']

    def get_proc_collection(self):
        """
        The proc collection is a mongodb database that keeps the name of each
        processed file, to avoid processing these files again.
        """
        coll =  self._mongodb_connect('proc_files')
        coll.ensure_index('file_name')

        return coll

    def write_skipped_log_dir(self, line):
        if self._skipped_log_dir:
            self._skipped_log_dir.write("%s \r\n" % line)
    
    def run(self):
        if self._counter_compliant:
            ts = utils.TimedSet(expired=utils.checkdatelock)

        ac = AccessChecker(self._collection)

        for logfile in os.popen('ls %s/*' % LOG_DIR):

            logfile = logfile.strip()

            # Verifica se arquivo já foi processado.
            if self._proc_coll.find({'file_name': logfile}).count() > 0:
                logger.debug('File already processe %s' % logfile)
                continue

            # Registra em base de dados de arquivos processados o novo arquivo.
            logger.info("Processing: %s" % logfile)
            self._proc_coll.insert({'file_name': logfile})

            rq = Local(self._mongo_uri, self._collection)

            with open(logfile, 'rb') as f:

                log_file_line = 0
                for raw_line in f:
                    log_file_line += 1
                    logger.debug("Reading line {0} from file {1}".format(str(log_file_line), logfile))
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
                            self.write_skipped_log_dir('; '.join([lockid, parsed_line['original_date'], parsed_line['original_agent']]))
                            continue
                    else:
                        # SciELO Mode Accesses
                        register_access(rq, parsed_line)


            rq.send()
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

    bk = Bulk(
        MONGO_URI,
        collection=args.collection,
        counter_compliant=COUNTER_COMPLIANT,
        skipped_log_dir=COUNTER_COMPLIANT_SKIPPED_LOG_DIR
    )
    bk.run()

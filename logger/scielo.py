#!/usr/bin/env python
# coding: utf-8
import os
import argparse
import requests
import datetime
import logging
import urlparse
import codecs
import gzip

import pymongo

from logger.ratchet import Local
from logger.accesschecker import AccessChecker
from logger import utils

logger = logging.getLogger(__name__)

config = utils.Configuration.from_env()
settings = dict(config.items())['app:main']

COUNTER_COMPLIANT = int(settings.get('counter_compliant', 1))
COUNTER_COMPLIANT_SKIPPED_LOG_DIR = settings.get('counter_compliant_skipped_log_dir', None)
MONGO_URI = settings.get('mongo_uri', 'mongodb://127.0.0.1:27017/database_name')
MONGO_URI_COUNTER = settings.get('mongo_uri_counter', 'mongodb://127.0.0.1:27017/database_name')
LOGS_SOURCE = settings('logs_source', '.')

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

class Bulk(object):

    def __init__(self, collection, mongo_uri=MONGO_URI, logs_source=LOGS_SOURCE, counter_compliant=None, skipped_log_dir=None):
        self._mongo_uri = "%s_%s" % (mongo_uri, collection)
        self._proc_coll = self.get_proc_collection()
        self._collection = collection
        self._logs_source = logs_source
        self._counter_compliant = counter_compliant
        self._ts = utils.TimedSet(expired=utils.checkdatelock)
        self._skipped_log_dir = skipped_log_dir
        self._skipped_log = None
        self._ac = AccessChecker(self._collection)

    def __enter__(self):
        if self._skipped_log_dir:
            now = datetime.datetime.now().isoformat()
            skipped_log = '/'.join([self._skipped_log_dir, now]).replace('//', '/')
            try:
                self._skipped_log = open(skipped_log, 'w')
            except ValueError:
                raise "Invalid directory or file name: %s" % skipped_log

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._ts = None
        self._ac = None
        if self._skipped_log:
            self._skipped_log.close()

    def _mongodb_connect(self, mdb_database):

        db_url = urlparse.urlparse(self._mongo_uri)
        conn = pymongo.MongoClient(host=db_url.hostname, port=db_url.port)
        db = conn[db_url.path[1:]]
        if db_url.username and db_url.password:
            db.authenticate(db_url.username, db_url.password)

        return db[mdb_database]

    def get_proc_collection(self):
        """
        The proc collection is a mongodb database that keeps the name of each
        processed file, to avoid processing these files again.
        """
        coll =  self._mongodb_connect('proc_files')
        coll.ensure_index('file_name')

        return coll

    def write_skipped_log(self, line):
        if self._skipped_log:
            self._skipped_log.write("%s \r\n" % line)
    
    def read_log(self, logfile):
        logfile = logfile.strip()

        # Verifica se arquivo já foi processado.
        if self._proc_coll.find({'file_name': logfile}).count() > 0:
            logger.info('File already processed %s' % logfile)
            return None

        reader = codecs
        if utils.check_file_format(logfile) == 'gzip':
            reader = gzip

        # Registra em base de dados de arquivos processados o novo arquivo.
        logger.info("Processing: %s" % logfile)
        self._proc_coll.insert({'file_name': logfile})

        with reader.open(logfile, 'rb') as f:
            with Local(self._mongo_uri, self._collection) as rq:
                log_file_line = 0
                for raw_line in f:
                    log_file_line += 1
                    logger.debug("Reading line {0} from file {1}".format(str(log_file_line), logfile))
                    logger.debug(raw_line)

                    try:
                        parsed_line = self._ac.parsed_access(raw_line)
                    except ValueError as e:
                        logger.error("%s: %s" % (e.message, raw_line))
                        continue
                    
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
                            self._ts.add(lockid, parsed_line['iso_datetime'], locktime)
                            rq.register_access(parsed_line)
                        except ValueError:
                            self.write_skipped_log('; '.join([lockid, parsed_line['original_date'], parsed_line['original_agent']]))
                            continue
                    else:
                        pass
                        # SciELO Mode Accesses
                        rq.register_access(parsed_line)
                rq.send()

    def run(self):
        for logfile in os.popen('ls %s/*' % self._logs_source):
            self.read_log(logfile)

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
        '--logs_source',
        '-s',
        help='Full path to the directory with apache log files'
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
        collection = args.collection,
        mongo_uri = MONGO_URI,
        logs_source = args.logs_source,
        counter_compliant = COUNTER_COMPLIANT,
        skipped_log_dir = COUNTER_COMPLIANT_SKIPPED_LOG_DIR
    )

    bk.run()

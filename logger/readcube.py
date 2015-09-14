#!/usr/bin/env python
# coding: utf-8
import logging
import argparse
import time
import datetime
import urlparse
import codecs

import pymongo

from logger.ratchet import ReadCube
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler
import utils

logger = logging.getLogger(__name__)

config = utils.Configuration.from_env()
settings = dict(config.items())['app:main']

COUNTER_COMPLIANT = int(settings.get('counter_compliant', 0))
COUNTER_COMPLIANT_SKIPPED_LOG_DIR = settings.get('counter_compliant_skipped_log_dir', None)
MONGO_URI = settings.get('mongo_uri', 'mongodb://127.0.0.1:27017/database_name')
MONGO_URI_COUNTER = settings.get('mongo_uri_counter', 'mongodb://127.0.0.1:27017/database_name')
LOG_DIR = settings['readcube_log_dir']

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

class AccessMap(object):

    def __init__(self, line):
        if len(line) != 13:
            raise ValueError('Log line does not have 13 itens')
        self._data = line

        try:
            self._date = datetime.datetime.strptime(self._data[0][0:10], '%Y-%m-%d')
        except:
            raise ValueError('Invalid date: %s' % self._data[0])


    @property
    def access_date(self):
        return self._date.strftime('%Y-%m-%d')

    @property
    def access_timestamp(self):
        return self._data[0]

    @property
    def access_day(self):
        return "%02d" % self._date.day

    @property
    def access_month(self):
        return "%02d" % self._date.month

    @property
    def access_year(self):
        return str(self._date.year)

    @property
    def doi(self):
        return self._data[1]

    @property
    def issn(self):
        return self._data[2]

    @property
    def user_email(self):
        return self._data[3]

    @property
    def user_institution(self):
        return self._data[4]

    @property
    def user_role(self):
        return self._data[5]

    @property
    def duration(self):
        return self._data[6]

    @property
    def annotation(self):
        return self._data[7]

    @property
    def highlights(self):
        return self._data[8]

    @property
    def platform(self):
        return self._data[9]

    @property
    def ip(self):
        return self._data[10]

    @property
    def country(self):
        return self._data[11]

    @property
    def downloaded(self):
        return self._data[12]

def get_lines(filename):
    with codecs.open(filename, 'r', encoding="utf-8", errors="replace") as csvfile:
        for line in csvfile:
            try:
                am = AccessMap([i.strip() for i in line.split('\t')])
                yield am
            except ValueError as e:
                logger.error(e.message)

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

        return db[mdb_database]

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

    def run(self, filename):

        if self._counter_compliant:
            ts = utils.TimedSet(expired=utils.checkdatelock)

        # Verifica se arquivo já foi processado.
        if self._proc_coll.find({'file_name': filename}).count() > 0:
            logger.debug('File already processe %s' % filename)
            return None

        # Registra em base de dados de arquivos processados o novo arquivo.
        logger.debug("Processing: %s" % filename)
        self._proc_coll.insert({'file_name': filename})

        rq = ReadCube(self._mongo_uri, self._collection)
        
        log_file_line = 0
        for parsed_line in get_lines(filename):
            log_file_line += 1
            logger.debug("Reading line {0} from file {1}".format(str(log_file_line), filename))
            if COUNTER_COMPLIANT:
                # Counter Mode Accesses
                locktime = 30 # Always ePDF's
                try:
                    lockid = '_'.join([parsed_line.ip, parsed_line.doi])
                    ts.add(lockid, parsed_line.access_timestamp, locktime)
                    rq.register_readcube_access(parsed_line.doi, parsed_line.access_date)
                except ValueError:
                    self.write_skipped_log_dir('; '.join([lockid, parsed_line.access_timestamp, 'readcube']))
                    continue
            else:
                # SciELO Mode Accesses
                rq.register_readcube_access(parsed_line.doi, parsed_line.access_date)

        logger.info('Bulking data')
        rq.send()
        logger.info('Bulking data finished')
        del(rq)

class EventHandler(FileSystemEventHandler):

    def __init__(self, collection=None):
        self._collection = collection

    def on_created(self, event):
        bk = Bulk(
            '%s_%s' % (MONGO_URI, self._collection),
            collection = self._collection,
            counter_compliant = COUNTER_COMPLIANT,
            skipped_log_dir = COUNTER_COMPLIANT_SKIPPED_LOG_DIR
        )
        logger.debug('New file available: %s' % event.src_path)
        bk.run(event.src_path)
        del(bk)

def watcher(collection, logs_source=LOG_DIR):

    event_handler = EventHandler(collection=collection)
    observer = Observer()
    observer.schedule(event_handler, logs_source, recursive=True)
    observer.start()
    logger.info('Starting listening directory: %s' % logs_source)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def main():

    parser = argparse.ArgumentParser(
        description="Run the processing to read the access log files from readcube to register accesses into Ratchet"
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

    watcher(args.collection)

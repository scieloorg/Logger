"""
This tool inspects the FTP directories that will receive the apache log files
from the SciELO Network.
"""
#!/usr/bin/env python
# coding: utf-8
import logging
import argparse
import requests
import re
import datetime
import time
import os
import traceback
import sys

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler

from logger import utils
from tasks import readlog

logger = logging.getLogger(__name__)

REGEX_FILENAME = re.compile(r'^(?P<date>\d+4?-\d+2?-\d+2?)_scielo\.(?P<collection>.*?)\.log\.gz$')

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

def collections():
    url = "http://articlemeta.scielo.org/api/v1/collection/identifiers/"
    try:
        collections = requests.get(url).json()
    except:
        logger.error('Fail to retrieve collections from: %s' % url)

    return {i['acron2']:i for i in collections}

COLLECTIONS = collections()

class Inspector(object):

    def __init__(self, filename):

        logger.info('Inspecting file: %s' % filename)
        self._file = filename
        self._filename = filename.split('/')[-1]
        self._parsed_fn = REGEX_FILENAME.match(self._filename)

    def _is_valid_filename(self):
        if not self._parsed_fn:
            logger.warning('Invalid filename: %s' % self._filename)
            return False

        return True

    def _is_valid_source_directory(self):

        if not self._is_valid_filename:
            return False

        if not self._file.split('/')[-2] in self._filename:
            logger.warning('Invalid source directory: %s' % self._file)
            return False

        return True

    def _is_valid_date(self):

        if not self._is_valid_filename:
            return False

        try:
            datetime.datetime.strptime(self.datelog,'%Y-%m-%d')
        except:
            logger.warning('Invalid date in filename: %s' % self._filename)
            return False

        return True

    def _is_valid_collection(self):

        if not self._is_valid_filename:
            return False

        if not self.collection in COLLECTIONS:
            logger.warning('Invalid collection in filename: %s' % self._filename)
            return False

        return True

    def _is_valid_gzip(self):
        if not utils.check_file_format(self._file) == 'gzip':
            logger.warning('Invalid gzip file: %s' % self._file)
            return False

        return True

    @property
    def filename(self):
        return self._filename

    @property
    def datelog(self):
        return self._parsed_fn.groupdict().get('date', None)

    @property
    def collection(self):
        return self._parsed_fn.groupdict().get('collection', None)

    @property
    def collection_acron_3(self):
        return COLLECTIONS.get(self._parsed_fn.groupdict().get('collection', None), {'code': None})['code']

    def is_valid(self):

        if not self._is_valid_filename():
            return False

        if not self._is_valid_date():
            return False

        if not self._is_valid_collection():
            return False

        if not self._is_valid_source_directory():
            return False

        if not self._is_valid_gzip():
            return False

        return True

class EventHandler(FileSystemEventHandler):

    logfilename = 'report.log'

    def write_log(self, logpath, message):

        logpath = logpath.split('/')
        logpath[-1] = self.logfilename
        logfile = '/'.join(logpath)

        message = datetime.datetime.now().isoformat()[:19] + ' - ' + message

        with open(logfile, 'a') as f:
            line = '%s\r\n' % message
            f.write(line)

    def on_created(self, event):
        slp_time = 3
        if self.logfilename in event.src_path:
            return False

        try:
            if event.is_directory:
                msg = 'New directory detected: %s' % event.src_path
                logger.debug(msg)
                self.write_log(event.src_path, msg)
                os.rmdir(event.src_path)
                msg = 'Directory removed: %s' % event.src_path
                logger.debug(msg)
                self.write_log(event.src_path, msg)
                return False

            msg = 'New file detected: %s' % event.src_path
            logger.info(msg)
            self.write_log(event.src_path, msg)

            attempt = 0
            while True:
                attempt += 1
                inspector = Inspector(event.src_path)
                msg = "File is valid: %s" % str(inspector.is_valid())
                logger.debug(msg)
                if not inspector.is_valid():
                    msg = "File is not valid, attempt (%d/10) will try again in %d seconds: %s" % (attempt, slp_time, event.src_path)
                    logger.debug(msg)
                    self.write_log(event.src_path, msg)
                    if attempt < 10:
                        time.sleep(slp_time)
                        continue
                    else:
                        os.remove(event.src_path)
                        msg = "File is not valid, removed from server: %s" % event.src_path
                        logger.debug(msg)
                        self.write_log(event.src_path, msg)
                        return None

                msg = "File is valid, sending for processing: %s" % event.src_path
                logger.debug(msg)
                self.write_log(event.src_path, msg)
                readlog.delay(event.src_path, inspector.collection_acron_3)
                break

        except Exception, err:
            logger.exception(sys.exc_info()[0])

def watcher(logs_source):

    event_handler = EventHandler()
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
        description="Run the monitor of the apache logs directory"
    )

    parser.add_argument(
        '--logs_source',
        '-s',
        help='Full path to the directory with the apache log files'
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

    watcher(args.logs_source)
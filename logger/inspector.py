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

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

REGEX_FILENAME = re.compile(r'^(?P<date>\d+4?-\d+2?-\d+2?)_scielo\.(?P<collection>.*?)\.log.gz$')

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
        self._filename = filename
        self._parsed_fn = REGEX_FILENAME.match(self._filename)

    def _is_valid_filename(self):
        if not self._parsed_fn:
            logger.warning('Invalid filename: %s' % self._filename)
            return False

        return True

    def _is_valid_date(self):

        if not self._is_valid_filename:
            return False

        date = self._parsed_fn.groupdict().get('date', None)

        try:
            datetime.datetime.strptime(date,'%Y-%m-%d')
        except:
            logger.warning('Invalid date in filename: %s' % self._filename)
            return False

        return True

    def _is_valid_collection(self):

        if not self._is_valid_filename:
            return False

        collection = self._parsed_fn.groupdict().get('collection', None)

        if not collection in COLLECTIONS:
            logger.warning('Invalid collection in filename: %s' % self._filename)
            return False

        return True

    def is_valid(self):

        if not self._is_valid_filename():
            return False

        if not self._is_valid_date():
            return False

        if not self._is_valid_collection():
            return False

        return True

class EventHandler(FileSystemEventHandler):

    def on_created(self, event):
        logger.info('New file detected: %s' % event.src_path)
        filename = event.src_path.split('/')[-1]
        inspector = Inspector(filename)
        
        logger.debug("File is valid: %s" % str(inspector.is_valid()))

        if not inspector.is_valid():
            os.remove(event.src_path)
            logger.debug("File removed from server: %s" % event.src_path)

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
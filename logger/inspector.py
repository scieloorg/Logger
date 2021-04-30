# coding: utf-8
"""
This tool inspects the FTP directories that will receive the apache log files
from the SciELO Network.
"""
import logging
import argparse
import requests
import re
import datetime
import time
import os
import traceback
import sys
import shutil

from watchdog.observers.polling import PollingObserverVFS
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler

from logger import utils
from logger.tasks import readlog
from articlemeta.client import ThriftClient

logger = logging.getLogger(__name__)

REGEX_FILENAME = re.compile(
    r'^(?P<date>\d+4?-\d+2?-\d+2?)_scielo\.(?P<collection>.*?)\.*[0-9]*\.log\.gz$')


am_client = ThriftClient(domain='articlemeta.scielo.org:11621')


def _config_logging(logging_level='INFO', logging_file=None):

    allowed_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.setLevel(allowed_levels.get(logging_level, 'INFO'))

    if logging_file:
        hl = logging.FileHandler(logging_file, mode='a')
    else:
        hl = logging.StreamHandler()

    hl.setFormatter(formatter)
    hl.setLevel(allowed_levels.get(logging_level, 'INFO'))

    logger.addHandler(hl)


class Inspector(object):

    def __init__(self, filename):

        logger.info('Inspecting file: %s' % filename)
        self._file = filename
        self._filename = filename.split('/')[-1]
        self._parsed_fn = REGEX_FILENAME.match(self._filename)
        self.collections = self.get_collections()

    def get_collections(self):
        collections = {}
        try:
            collections = am_client.collections()
            return {i.acronym2letters: i for i in collections}
        except:
            logger.error('Fail to retrieve collections')
        return {}

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
            datetime.datetime.strptime(self.datelog, '%Y-%m-%d')
        except:
            logger.warning('Invalid date in filename: %s' % self._filename)
            return False

        return True

    def _is_valid_collection(self):

        if not self._is_valid_filename:
            return False

        if self.collection not in self.collections:
            logger.warning(
                'Invalid collection in filename: %s' % self._filename)
            return False

        return True

    def _is_valid_gzip(self):
        if not utils.check_file_format(self._file) == 'gzip':
            logger.warning('Invalid gzip file: %s' % self._file)
            return False

        return True

    def _is_gzip_integrate(self):
        if not utils.is_gzip_integrate(self._file):
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

        collection = self.collections.get(
            self._parsed_fn.groupdict().get('collection', None), None
        )

        return collection.code if collection else None

    def is_valid(self):

        if not self._is_valid_filename():
            return (False, 'invalid file name')

        if not self._is_valid_date():
            return (False, 'invalid date')

        if not self._is_valid_collection():
            return (False, 'invalid collection code')

        if not self._is_valid_source_directory():
            return (False, 'invalid source directory')

        if not self._is_valid_gzip():
            return (False, 'invalid gzip')

        if not self._is_gzip_integrate():
            return (False, 'invalid gzip, integrity error')

        return (True, 'file is valid')


class EventHandler(FileSystemEventHandler):

    def __init__(self, safecopy_dir):
        self.logfilename = 'report.log'
        self.files = {}
        self.safecopy_dir = safecopy_dir

    def is_file_size_stucked(self, logpath):
        status = self.files.setdefault(logpath, 0)
        current = os.path.getsize(logpath)
        if not status == current:
            self.files[logpath] = current
            return False
        del(self.files[logpath])
        return True

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

            time.sleep(600)
            shutil.copy2(event.src_path, self.safecopy_dir)
            logger.info('file "%s" was copied to "%s"', event.src_path, self.safecopy_dir)

            msg = 'New file detected: %s' % event.src_path
            logger.info(msg)
            self.write_log(event.src_path, msg)

            while True:
                msg = 'File being uploaded to the FTP: %s' % event.src_path
                logger.info(msg)
                self.write_log(event.src_path, msg)
                if self.is_file_size_stucked(event.src_path):
                    break
                time.sleep(600)

            inspector = Inspector(event.src_path)
            validated, validation_message = inspector.is_valid()
            msg = "File is valid: %s" % str(validated)
            logger.debug(msg)

            if not validated:
                os.remove(event.src_path)
                msg = "File is not valid (%s), removed from server: %s" % (
                    validation_message, event.src_path)
                logger.debug(msg)
                self.write_log(event.src_path, msg)
                return None

            msg = "File is valid, sending for processing: %s" % event.src_path
            logger.debug(msg)
            self.write_log(event.src_path, msg)
            readlog.delay(event.src_path, inspector.collection_acron_3)

        except Exception, err:
            logger.exception(sys.exc_info()[0])


def watcher(logs_source, safecopy_dir, polling_interval):

    event_handler = EventHandler(safecopy_dir)
    observer = PollingObserverVFS(
        os.stat, 
        os.listdir, 
        polling_interval=polling_interval
    )
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
        '--safecopy_dir',
        '-c',
        help='Full path to the directory to send copies of all received log files'
    )

    parser.add_argument(
        '--polling_interval',
        '-i',
        type=int,
        default=600,
        help='Polling interval in seconds. Defaults to 600 seconds.'
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

    watcher(args.logs_source, args.safecopy_dir, args.polling_interval)

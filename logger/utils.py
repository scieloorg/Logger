#coding: utf-8
import os
import logging
import json
import weakref
import datetime
import gzip
from copy import deepcopy
from time import sleep

from ConfigParser import SafeConfigParser


logger = logging.getLogger(__name__)


def try_get_collections(am_client):
    for i in (1, 2, 5, 10):
        try:
            return am_client.collections()
        except Exception as e:
            print(e)
            sleep(i*60*60)
            logger.info("%s. Tenta novamente após %s." % (str(e), i))


class Collections(object):
    """
    Junta coleções presentes no AM e
    coleções que o site antigo e o novo estão contabilizando acessos
    """

    def __init__(self, am_client, new_websites_config_file_path=None):
        # AM client
        self._am_client = am_client
        # New websites config file_path
        self._new_websites_config_file_path = (
            new_websites_config_file_path or
            "new_websites.json"
        )
        self.__am_collections = None
        self.__new_collections = None
        self._indexed_by_acron_found_in_zip_filename = None
        self._indexed_by_code = None

    @property
    def _am_collections(self):
        self.__am_collections = (
            self.__am_collections or
            try_get_collections(self._am_client)
        )
        return self.__am_collections or []

    @property
    def _new_collections(self):
        if not self.__new_collections:
            self.__new_collections = []
            try:
                with open(self._new_websites_config_file_path, "r") as fp:
                    new_websites_data = json.loads(fp.read())
            except IOError:
                new_websites_data = None
            else:
                indexed = self.index_by_acronym2letters(self._am_collections)
                indexed.update(self.index_by_code(self._am_collections))

                for data in new_websites_data:
                    old = data.get('old')
                    new = data.get("new")
                    if not old or not new:
                        continue
                    col = indexed.get(old)
                    if col:
                        new_col = deepcopy(col)
                        new_col.code = new
                        new_col.acronym = new
                        new_col.acronym2letters = new
                        self.__new_collections.append(new_col)
        return self.__new_collections

    def index_by_code(self, items):
        return {i.code: i for i in items}

    def index_by_acronym2letters(self, items):
        return {i.acronym2letters: i for i in items}

    @property
    def indexed_by_acron_found_in_zip_filename(self):
        if not self._indexed_by_acron_found_in_zip_filename:
            self._indexed_by_acron_found_in_zip_filename = (
                self.index_by_acronym2letters(self.collections)
            )
        return self._indexed_by_acron_found_in_zip_filename or {}

    @property
    def indexed_by_code(self):
        if not self._indexed_by_code:
            self._indexed_by_code = self.index_by_code(self.collections)
        return self._indexed_by_code or {}

    @property
    def collections(self):
        return list(self._am_collections) + self._new_collections

    def get_code(self, acron):
        try:
            return self.indexed_by_acron_found_in_zip_filename.get(acron).code
        except AttributeError:
            raise ValueError("Collection '%s' not found" % acron)

    def codes(self):
        return self.indexed_by_code.keys()


class SingletonMixin(object):
    """
    Adds a singleton behaviour to an existing class.

    weakrefs are used in order to keep a low memory footprint.
    As a result, args and kwargs passed to classes initializers
    must be of weakly refereable types.
    """
    _instances = weakref.WeakValueDictionary()

    def __new__(cls, *args, **kwargs):
        key = (cls, args, tuple(kwargs.items()))

        if key in cls._instances:
            return cls._instances[key]

        new_instance = super(type(cls), cls).__new__(cls, *args, **kwargs)
        cls._instances[key] = new_instance

        return new_instance


class Configuration(SingletonMixin):
    """
    Acts as a proxy to the ConfigParser module
    """
    def __init__(self, fp, parser_dep=SafeConfigParser):
        self.conf = parser_dep()
        self.conf.readfp(fp)

    @classmethod
    def from_env(cls):
        try:
            filepath = os.environ['LOGGER_SETTINGS_FILE']
        except KeyError:
            raise ValueError('missing env variable LOGGER_SETTINGS_FILE')

        return cls.from_file(filepath)

    @classmethod
    def from_file(cls, filepath):
        """
        Returns an instance of Configuration

        ``filepath`` is a text string.
        """
        fp = open(filepath, 'rb')
        return cls(fp)

    def __getattr__(self, attr):
        return getattr(self.conf, attr)

    def items(self):
        """Settings as key-value pair.
        """
        return [(section, dict(self.conf.items(section, raw=True))) for \
            section in [section for section in self.conf.sections()]]

settings = dict(Configuration.from_env().items())['app:main']


def checkdatelock(previous_date=None, next_date=None, locktime=10):

    try:
        pd = datetime.datetime.strptime(previous_date, '%Y-%m-%dT%H:%M:%S')
        nd = datetime.datetime.strptime(next_date, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return None

    delta = nd - pd

    if not delta.total_seconds() <= locktime:
        return nd


def check_file_format(logfile):
    with open(logfile, 'rb') as f:
        if f.read(1024).startswith('\x1f\x8b\x08'):
            f.seek(0)
            return 'gzip'

    return 'txt'


def is_gzip_integrate(logfile):
    try:
        with gzip.open(logfile, 'rb') as f:
            for line in f:
                pass
        return True
    except:
        return False


class TimedSet(object):
    def __init__(self, items=None, expired=None):
        self.expired = expired or (lambda t0, t1, t2: True)
        self._items = {}

    def _add_or_update(self, item, dt, locktime):
        match = self._items.get(item, None)
        return True if match is None else self.expired(
            match, dt, locktime=locktime)

    def add(self, item, dt, locktime=10):
        if self._add_or_update(item, dt, locktime):
            self._items[item] = dt
        else:
            raise ValueError('the item stills valid')

    def __contains__(self, item):
        return item in self._items

#coding: utf-8
import os
import logging
import csv
import weakref
import datetime
import gzip
from time import sleep

from ConfigParser import SafeConfigParser


logger = logging.getLogger(__name__)


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
print(settings)


def read_websites_configuration():
    file_path = settings.get("websites_configuration_path")
    if not file_path:
        raise ValueError("Invalid value for WEBSITES_CONFIGURATION_PATH")
    # lê a configuração de websites
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield row



class Website(object):
    """
    Dados de collection
    """

    def __init__(self, data):
        # collection_id = 'scl', 'scl'
        self.collection_id = data['collection_id']
        # website = 'new', 'classic'
        self.website = data['website']
        # website_id = 'nbr', 'scl'
        self.website_id = data['website_id']
        # acron_in_log_file_name = 'br', 'br'
        self.acron_in_log_file_name = data['acron_in_log_file_name']


class Collections(object):
    """
    Junta coleções presentes no AM e
    coleções que o site antigo e o novo estão contabilizando acessos
    """

    def __init__(self):
        self._items = read_websites_configuration()
        self._websites = [Website(data) for data in self._items]

        self._indexed_by_website_acron_in_filename = {
            website.acron_in_log_file_name: website
            for website in self._websites
        }
        self._indexed_by_website_id = {
            website.website_id: website for website in self._websites
        }

    @property
    def indexed_by_website_acron_in_filename(self):
        return self._indexed_by_website_acron_in_filename

    @property
    def indexed_by_website_id(self):
        return self._indexed_by_website_id

    @property
    def websites(self):
        return self._websites

    def get_website_id(self, website_acron):
        try:
            return self.indexed_by_website_acron_in_filename.get(website_acron).website_id
        except AttributeError:
            raise ValueError("Website searched by acron='%s' not found" % website_acron)

    @property
    def website_ids(self):
        return self.indexed_by_website_id.keys()

    def get_website(self, website_id):
        try:
            return self.indexed_by_website_id[website_id]
        except AttributeError:
            raise ValueError("Website searched by id='%s' not found" % website_id)


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

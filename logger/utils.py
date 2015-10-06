#coding: utf-8
import os
import weakref
import datetime

from ConfigParser import SafeConfigParser


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


class TimedSet(object):
    def __init__(self, items=None, expired=None):
        self.expired = expired or (lambda t0, t1, t2: True)
        self._items = {}

    def _add_or_update(self, item, dt, locktime):
        match = self._items.get(item, None)
        return True if match is None else self.expired(match, dt, locktime=locktime)

    def add(self, item, dt, locktime=10):
        if self._add_or_update(item, dt, locktime):
            self._items[item] = dt
        else:
            raise ValueError('the item stills valid')

    def __contains__(self, item):
        return item in self._items

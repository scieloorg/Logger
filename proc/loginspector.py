# -*- encoding: utf-8 -*-
import logaccess_config
import pymongo

class AccessDatabase(object):

    def __init__(self, domain = logaccess_config.MONGODB_DOMAIN, port = logaccess_config.MONGODB_PORT, 
        dbname = logaccess_config.COLLECTION_CODE+"_accesslog", 
        collection = logaccess_config.COLLECTION_CODE+"_analytics"):

        self._conn = pymongo.Connection(domain, port)
        self._db = self.__conn[dbname]
        self._collection = self._db[collection]

    def getcollection():
        
        return self._collection

class LogInspector(object):

    def __init__(self, allowed_patterns = logaccess_config.ALLOWED_PATTERNS, collection = AccessDatabase):
        self._allowed_patterns = allowed_patterns

        import pdb
        pdb.set_trace()

        self._collection = collection

    def listtypes(self):
        """
        Recover the sorted list of log patterns configured at logaccess_config.py 
        """

        pattern_types = [i for i in sorted(self._allowed_patterns.iterkeys())]

        return pattern_types

    def listtypeindexes(self):
        """
        Recover the sorted list of log patterns and given contexts configured at logaccess_config.py 
        """

        indexes = {}
        for dtype,value in sorted(self._allowed_patterns.items()):
            if value.has_key('index'):
                indexes[dtype] = value['index']

        return indexes

    def getitem(self, code):
        """
        Recover an Item statistics acording to the item code.
        """

        fetch = self._collection.find_one({'code':code})

        return fetch

    def getitemsbypattern(self, pattern):
        """
        Recover an list of item according to a pattern id retrieved by listpatterns method
        """

        return True
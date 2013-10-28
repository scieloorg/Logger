import urllib2
import json

class AccessChecker(object):

    def __init__(self, collection=None):
        allowed_collections = self._allowed_collections()
        
        if not collection in allowed_collections:
            raise ValueError('Invalid collection id, you must select one of these %s' % str(allowed_collections)) 

        self.collection = collection
        self.allowed_issns = self._allowed_issns()

    def _allowed_collections(self):        
        allowed_collections = []
        try:
            json_network = urllib2.urlopen('http://webservices.scielo.org/scieloorg/_design/couchdb/_view/network', timeout=3).read()
        except urllib2.URLError:
            raise urllib2.URLError('Was not possible to connect to webservices.scielo.org, try again later!')

        network = json.loads(json_network)

        for collection in network['rows']:
            allowed_collections.append(collection['id'])
        
        return allowed_collections

    def _allowed_issns(self):        
        query_url = 'http://webservices.scielo.org/scieloorg/_design/couchdb/_view/title_collectionstitle_keys?startkey=["%s",{}]&endkey=["%s"]&descending=true&limit=2000&include_docs=true' % (self.collection, self.collection)

        try:
            titles_json = urllib2.urlopen(query_url, timeout=3).read()
        except urllib2.URLError:
            raise urllib2.URLError('Was not possible to connect to webservices.scielo.org, try again later!')

        titles = json.loads(titles_json)

        title_dict = {}
        for title in titles['rows']:
            title_dict[title['doc']['v68'][0]['_']] = title['doc']['v400'][0]['_']

        return title_dict
import urllib2
import json

class AccessChecker(object):

    def __init__(self, collection=None):
        allowed_collections = self._allowed_collections()
        
        if not collection in allowed_collections:
            raise ValueError('Invalid collection id, you must select one of these %s' % str(allowed_collections)) 

        self.collection = collection

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

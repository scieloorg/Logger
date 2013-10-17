import urllib2

class RequestChecker(object):

    def __init__(self, collection):
        pass

    def _allowed_collections(self):
        
        json_network = urllib2.urlopen('http://webservices.scielo.org/scieloorg/_design/couchdb/_view/network').read()

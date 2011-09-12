from analytics.resources import Root
from pyramid.configuration import Configurator
from pyramid.events import subscriber
from pyramid.events import NewRequest
from pyramid.renderers import JSONP
from pymongo import Connection

import pyramid_zcml

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator()
    config.begin()
    
    db_uri = settings['db_uri']
    conn = Connection(db_uri)
    config.registry.settings['db_conn'] = conn
    config.registry.settings['db_name'] = settings['db_name']
    config.add_subscriber(add_mongo_db, NewRequest)

    config.include('pyramid_zcml')
    config.load_zcml('configure.zcml')
    config.end()

    #add renderer
    #Fixme: try to insert this on zcml file 
    config.add_renderer('jsonp', JSONP(param_name='callback'))
      
    return config.make_wsgi_app()

def add_mongo_db(event):
    settings = event.request.registry.settings
    db = settings['db_conn'][settings['db_name']]
    event.request.db = db
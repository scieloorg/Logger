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
    
    config.add_renderer('jsonp', JSONP(param_name='callback'))
    
    #site
    config.add_route('site', '/analytics/site/{instance}/{output}')
    config.add_view('analytics.views.site', route_name='site', renderer='jsonp')

    #site_option
    config.add_route('site_option', '/analytics/site/{instance}/{option}/{output}')
    config.add_view('analytics.views.site_option', route_name='site_option', renderer='jsonp')

    #site_key
    config.add_route('site_key', '/analytics/site/{instance}/{option}/{key}/{output}')
    config.add_view('analytics.views.site_key', route_name='site_key', renderer='jsonp')

    #site_option_range
    config.add_route('site_option_range', '/analytics/site/{instance}/{option}/range/{range}/{output}')
    config.add_view('analytics.views.site_option_range', route_name='site_option_range', renderer='jsonp')
    
    return config.make_wsgi_app()

def add_mongo_db(event):
    settings = event.request.registry.settings
    db = settings['db_conn'][settings['db_name']]
    event.request.db = db
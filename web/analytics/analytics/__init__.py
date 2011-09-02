from pyramid.config import Configurator
from analytics.resources import Root
from pyramid.configuration import Configurator

import pyramid_zcml

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator()
    config.begin()
    config.include('pyramid_zcml')
    config.load_zcml('configure.zcml')
    config.end()
    return config.make_wsgi_app()

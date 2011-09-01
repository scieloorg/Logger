from pyramid.config import Configurator
from analytics.resources import Root

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root, settings=settings)
    config.add_view('analytics.views.chat_site',
                    context='analytics:resources.Root',
                    renderer='analytics:templates/chat_site.pt')
    config.add_static_view('static', 'analytics:static')
    return config.make_wsgi_app()

from pyramid.renderers import render_to_response
from pyramid.response import Response

def site_client(request):
    
    if not request.matchdict['options']:
        return Response('Set chart options')
   
    return render_to_response('templates/site.pt',
                              {'server_url': request.registry.settings['server_url'],
                              'instance':request.matchdict['instance'],
                              'index':request.matchdict['index'],
                              'chart':request.matchdict['chart'],
                              'y': request.matchdict['year'],
                              'options':request.matchdict['options']},
                              request=request)


def site_client_year(request):

    if not request.matchdict['options']:
        return Response('Set chart options')

    return render_to_response('templates/site_two_year.pt',
                              {'server_url': request.registry.settings['server_url'],
                              'instance':request.matchdict['instance'],
                              'index':request.matchdict['index'],
                              'chart':request.matchdict['chart'],
                              'y1':request.matchdict['year1'],
                              'y2':request.matchdict['year2'],
                              'options':request.matchdict['options']},
                              request=request)
                              
def site_client_index(request):

    if not request.matchdict['options']:
        return Response('Set chart options')

    return render_to_response('templates/site_two_index.pt',
                              {'server_url': request.registry.settings['server_url'],
                              'instance':request.matchdict['instance'],
                              'chart':request.matchdict['chart'],
                              'i1':request.matchdict['index1'],
                              'i2':request.matchdict['index2'],
                              'year':request.matchdict['year'],
                              'options':request.matchdict['options']},
                              request=request)


def site_client_range(request):

    if not request.matchdict['options']:
        return Response('Set chart options')

    return render_to_response('templates/site_two_range.pt',
                              {'server_url': request.registry.settings['server_url'],
                              'instance':request.matchdict['instance'],
                              'index':request.matchdict['index'],
                              'chart':request.matchdict['chart'],
                              'start_key':request.matchdict['start_range'],
                              'end_key':request.matchdict['end_range'],
                              'options':request.matchdict['options']},
                              request=request)

from pyramid.renderers import render_to_response

def site_client(request):
    return render_to_response('templates/chart.pt',
                              {'foo':1, 'bar':2})
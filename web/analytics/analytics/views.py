from pyramid.response import Response
import tool
import json

def site(request):

    db = request.db
    analytics = db.analytics
    
    dictmon = analytics.find_one({'site': request.matchdict['instance']})

    #remove the key '_id'
    del dictmon['_id']
    
    return Response(json.dumps(dictmon, sort_keys=True, indent=4),
        content_type='text/plain', charset='utf8')

def site_key(request):

    db = request.db
    analytics = db.analytics

    dictmon = analytics.find_one({'site': request.matchdict['instance']})

    #remove the key '_id'
    del dictmon['_id']

    return Response(json.dumps(tool.dict_by_key(tool.dict_by_acron(dictmon,
        request.matchdict['option']),request.matchdict['key']),sort_keys=True, indent=4),
        content_type='text/plain', charset='utf8')
        
def site_option(request):

    db = request.db
    analytics = db.analytics

    dictmon = analytics.find_one({'site': request.matchdict['instance']})
    
    #remove the key '_id'
    del dictmon['_id']

    return Response(json.dumps(tool.dict_by_acron(dictmon, request.matchdict['option']),
        sort_keys=True, indent=4), content_type='text/plain', charset='utf8')

def site_option_range(request):

    db = request.db
    analytics = db.analytics

    dictmon = analytics.find_one({'site': request.matchdict['instance']})
    
    #remove the key '_id'
    del dictmon['_id']

    request.matchdict['option']
    
    lst_range = request.matchdict['range'].split('-')

    start_key = lst_range[0]
    end_key = lst_range[1]

    return Response(json.dumps(tool.dict_slice_key(tool.dict_by_acron(dictmon,
        request.matchdict['option']), start_key, end_key), sort_keys=True,indent=4),
        content_type='text/plain', charset='utf8')

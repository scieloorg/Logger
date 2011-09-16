from pyramid.response import Response
import tool
import json

def site(request):

    db = request.db
    analytics = db.scl_analytics
    
    dictmon = analytics.find_one({'site': request.matchdict['instance']})

    #remove the key '_id'
    del dictmon['_id']
    
    return json.dumps(dictmon)

def site_key(request):

    db = request.db
    analytics = db.scl_analytics

    dictmon = analytics.find_one({'site': request.matchdict['instance']})

    #remove the key '_id'
    del dictmon['_id']

    return json.dumps(tool.dict_by_key(tool.dict_by_acron(dictmon,
        request.matchdict['option']),request.matchdict['key']))

def site_option(request):

    db = request.db
    analytics = db.scl_analytics

    dictmon = analytics.find_one({'site': request.matchdict['instance']})
    
    #remove the key '_id'
    del dictmon['_id']

    return json.dumps(tool.dict_by_acron(dictmon, request.matchdict['option']))

def site_option_range(request):

    db = request.db
    analytics = db.scl_analytics

    dictmon = analytics.find_one({'site': request.matchdict['instance']})
    
    #remove the key '_id'
    del dictmon['_id']

    request.matchdict['option']
    
    lst_range = request.matchdict['range'].split('-')

    start_key = lst_range[0]
    end_key = lst_range[1]

    return json.dumps(tool.dict_slice_key(tool.dict_by_acron(dictmon,
        request.matchdict['option']), start_key, end_key))


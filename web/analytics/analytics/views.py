import json
import tool
     

def site(request):
    db = request.db
    analytics = db.scl_analytics
    
    dictmon = analytics.find_one({'site': request.matchdict['instance']})
    
    #remove the key '_id'
    del dictmon['_id']
    
    return json.dumps(tool.dict_order_by_key(dictmon))

def site_key(request):
    db = request.db
    analytics = db.scl_analytics

    dictmon = analytics.find_one({'site': request.matchdict['instance']})

    #remove the key '_id'
    del dictmon['_id']

    if 'language' in request.params:
        language = request.params['language']
    else:
        language = False
            
    return json.dumps(tool.dict_order_by_key(tool.dict_by_key(tool.dict_by_acron(dictmon,
                      request.matchdict['option'], language), request.matchdict['key'])))

def site_option(request):
    db = request.db
    analytics = db.scl_analytics

    dictmon = analytics.find_one({'site': request.matchdict['instance']})
    
    #remove the key '_id'
    del dictmon['_id']

    if 'language' in request.params:
        language = request.params['language']
    else:
        language = False

    return json.dumps(tool.dict_order_by_key(tool.dict_by_acron(dictmon,
                      request.matchdict['option'], language)))

def site_option_range(request):
    db = request.db
    analytics = db.scl_analytics

    dictmon = analytics.find_one({'site': request.matchdict['instance']})
    
    #remove the key '_id'
    del dictmon['_id']

    request.matchdict['option']

    if 'language' in request.params:
        language = request.params['language']
    else:
        language = False

    return json.dumps(tool.dict_order_by_key(tool.dict_slice_key(tool.dict_by_acron(dictmon,
                      request.matchdict['option'], language), request.matchdict['start_range'],
                      request.matchdict['end_range'])))

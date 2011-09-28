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
            
    return json.dumps(tool.dict_order_by_key(tool.dict_by_key(tool.dict_by_index(dictmon,
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

    return json.dumps(tool.dict_order_by_key(tool.dict_by_index(dictmon,
                      request.matchdict['option'], language)))

def site_option_year(request):
    db = request.db
    analytics = db.scl_analytics
    list_ret = list()
    
    dictmon = analytics.find_one({'site': request.matchdict['instance']})

    #remove the key '_id'
    del dictmon['_id']

    y1 = tool.dict_by_year(dictmon, request.matchdict['option'], request.matchdict['year2'])
    y2 = tool.dict_by_year(dictmon, request.matchdict['option'], request.matchdict['year2'])

    print y1

    for i, (a, b) in enumerate(zip(y1, y2)):
        i = i+1
        list_ret.append([tool.dict_months(str(i)), a, (b +1000000)])
        
    print list_ret
    
    return json.dumps(list_ret)

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

    return json.dumps(tool.dict_order_by_key(tool.dict_slice_key(tool.dict_by_index(dictmon,
                      request.matchdict['option'], language), request.matchdict['start_range'],
                      request.matchdict['end_range'])))

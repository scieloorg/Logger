import json
import tool

def site(request):
    db = request.db
    analytics = db.scl_analytics
    
    dictmon = analytics.find_one({'site': request.matchdict['instance']})
    
    #remove the key '_id'
    del dictmon['_id']
    
    return json.dumps(tool.dict_order_by_key(dictmon))

def site_option(request):
    db = request.db
    analytics = db.scl_analytics
    list_ret = list()
    
    dictmon = analytics.find_one({'site': request.matchdict['instance']})
    
    #remove the key '_id'
    del dictmon['_id']

    #swith between pages and dates
    if(request.matchdict['option'] != 'sci'):
        list_ret =  tool.list_month_access(dictmon, request.matchdict['option'],
            request.matchdict['year'])
    else:
        list_ret =  tool.list_pages_access(dictmon, request.matchdict['option'])

    return json.dumps(list_ret)

def site_option_range(request):
    db = request.db
    analytics = db.scl_analytics

    dictmon = analytics.find_one({'site': request.matchdict['instance']})

    #remove the key '_id'
    del dictmon['_id']

    list_ret = tool.list_month_access_range(dictmon, request.matchdict['option'],
        request.matchdict['start_range'], request.matchdict['end_range'])

    return json.dumps(list_ret)


def site_option_two_year(request):
    db = request.db
    analytics = db.scl_analytics
    list_ret = list()
    
    dictmon = analytics.find_one({'site': request.matchdict['instance']})

    #remove the key '_id'
    del dictmon['_id']
        
    list_ret = tool.list_two_year(dictmon, request.matchdict['option'],
        request.matchdict['year1'], request.matchdict['year2'])
    
    return json.dumps(list_ret)

def site_option_two_index(request):
    db = request.db
    analytics = db.scl_analytics
    list_ret = list()

    dictmon = analytics.find_one({'site': request.matchdict['instance']})

    #remove the key '_id'
    del dictmon['_id']

    list_ret = tool.list_two_index(dictmon, request.matchdict['year'],
        request.matchdict['index1'], request.matchdict['index2'])

    return json.dumps(list_ret)

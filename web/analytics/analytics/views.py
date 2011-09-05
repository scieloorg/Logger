from pyramid.response import Response

import json

def site(request):

    db = request.db
    analytics = db.analytics
    
    dictmon = analytics.find_one({'site': request.matchdict['instance']})

    #remove the key '_id'
    del dictmon['_id']

    return Response(json.dumps(dictmon, sort_keys=True, indent=4),
        content_type='text/plain', charset='utf8')
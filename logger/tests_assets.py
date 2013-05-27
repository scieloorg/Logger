# -*- encoding: utf-8 -*-

"""
Collection of domain object factories to make testing easier.
"""
def get_sample_allowed_patterns():
    allowed_patterns = {
    'pdf':{'code':r'GET \/scielobooks\/(?P<code>[a-z0-9]*)\/pdf{1}|GET \/id\/(?P<code1>[a-z0-9]*)\/pdf{1}',
            'index':{'context':'book','dtype':'pdf'}},
    'epub':{'code':r'GET \/scielobooks\/(?P<code>[a-z0-9]*)\/epub{1}|GET \/id\/(?P<code1>[a-z0-9]*)\/epub{1}',
            'index':{'context':'book','dtype':'epub'}},
    'html':{'code':r'GET \/id\/(?P<code>[a-z0-9]*) {1}',
            'index':{'context':'book','dtype':'html'}},
    }

    return allowed_patterns

def get_sample_types():

    pattern_types = ['epub','html','pdf']

    return pattern_types

def get_sample_types_index():

    pattern_types = {'epub':{'context':'book','dtype':'epub'},
                    'html':{'context':'book','dtype':'html'},
                    'pdf':{'context':'book','dtype':'pdf'}}

    return pattern_types

def get_sample_item():

    from bson.objectid import ObjectId

    item = {u'code': u'q5cc4', 
            u'pdf_201206': 52, 
            u'htm': 973, 
            u'htm_201206': 74, 
            u'pdf_201204': 9737, 
            u'pdf_201205': 31718, 
            u'context': 
            u'book', 
            u'pdf': 41507, 
            u'htm_201205': 701, 
            u'htm_201204': 198, 
            u'_id': ObjectId('4fd8ca66807e972b3c6b3d42')}

    return item;
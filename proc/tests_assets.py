# coding: utf-8

"""
Collection of domain object factories to make testing easier.
"""
def get_sample_allowed_patterns():
    allowed_patterns = {
        'pdf':{'code':r'GET \/scielobooks\/(?P<code>[a-z0-9]*)\/pdf{1}|GET \/id\/(?P<code1>[a-z0-9]*)\/pdf{1}',
                'index':{'context':'book'}},
        'epub':{'code':r'GET \/scielobooks\/(?P<code>[a-z0-9]*)\/epub{1}|GET \/id\/(?P<code1>[a-z0-9]*)\/epub{1}',
                'index':{'context':'book'}},
        'html':{'code':r'GET \/id\/(?P<code>[a-z0-9]*) {1}',
                'index':{'context':'book'}},
    }

    return allowed_patterns

def get_sample_pattern_types():

    pattern_types = (i for i in get_sample_allowed_patterns())

    return pattern_types
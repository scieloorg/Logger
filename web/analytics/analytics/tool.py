#Tools for dictionary
from collections import OrderedDict

def dict_by_acron(dictmon, acron, language=False):
    dictacron = {}

    for k, v in dictmon.iteritems():
        acron_split = k.split('_')

        if not language:
            if(acron_split[0] == acron and len(acron_split) == 2):
                dictacron[acron_split[1]] = v

        if language:
            if(acron_split[0] == acron and len(acron_split) == 3):
                
                if(acron_split[2] == language):
                    dictacron[acron_split[1] + "-" + language] = v
                    
                if(language == 'all' and len(acron_split) == 3):
                    dictacron[acron_split[1] + acron_split[2]] = v
                    
    return dictacron

def dict_by_key(dictmon, key):
    return dict((k, v) for k, v in dictmon.items() if k in key)

def dict_slice_key(dictmon, start_key, end_key):
    return dict((k, v) for k, v in dictmon.iteritems() if start_key <= k <= end_key)

def dict_add_total(dictmon):
    total = 0
    for k, v in dictmon.iteritems():
        if isinstance(v, int):
            total = total + int(v)
        
    dictmon['total'] = total

    return dictmon

def dict_order_by_key(dictparam):
    return OrderedDict((k, dictparam[k]) for k in sorted(dictparam))


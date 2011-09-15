#Tools for dictionary

def dict_by_acron(dictmon, acron):
    dictacron = {}
    
    for k,v in dictmon.iteritems():
        acron_split  = k.split('_')

        if(acron_split[0]==acron):
            dictacron[acron_split[1]] = v
    
    return dict_add_total(dictacron)

def dict_by_key(dictmon, key):
    return dict_add_total(dict((k,v) for k,v in dictmon.items() if k in key))

def dict_slice_key(dictmon, start_key, end_key):
    return dict_add_total(dict((k, v) for k, v in dictmon.iteritems() if start_key <= k <= end_key))

def dict_add_total(dictmon):
    total = 0
    for k,v in dictmon.iteritems():
        if isinstance(v, int):
            total = total + int(v)
        
    dictmon['total'] = total

    return dictmon
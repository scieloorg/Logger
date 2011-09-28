#Tools for dictionary
from collections import OrderedDict

def dict_by_index(dictmon, index, language=False):
    dictacron = {}

    for k, v in dictmon.iteritems():
        acron_split = k.split('_')

        if not language:
            if(acron_split[0] == index and len(acron_split) == 2):
                dictacron[acron_split[1]] = v

        if language:
            if(acron_split[0] == index and len(acron_split) == 3):
                
                if(acron_split[2] == language):
                    dictacron[acron_split[1] + "-" + language] = v
                    
                if(language == 'all' and len(acron_split) == 3):
                    dictacron[acron_split[1] + acron_split[2]] = v
    return dictacron

def dict_by_year(dictmon, index, year):
    dict_ret = {}
    list_ret = []
    
    for k, v in dictmon.iteritems():
        split = k.split('_')

        if(split[0] == index and len(split) == 2 and split[1][0:4] == year):
            dict_ret[split[1][4:6]] = v

    for k, v in dict_order_by_key(dict_ret).iteritems():
        list_ret.append(v)

    #return dict_ret
    return list_ret

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

def dict_months(month):
    dict_months = {'1': 'jan',
                   '2': 'fev',
                   '3': 'mar',
                   '4': 'abr',
                   '5': 'mai',
                   '6': 'jun',
                   '7': 'jul',
                   '8': 'ago',
                   '9': 'set',
                   '10': 'out',
                   '11': 'nov',
                   '12': 'dez',
                  }
                      
    return dict_months.get(month)


################################################################################

def mongoo_by_pages(dict_mon):

    '''{u'sci_abstract': 44239800, u'sci_alphabetic': 35656, u'sci_serial': 8325880,
    u'sci_pdf': 20401928, u'sci_arttext': 139169528, u'sci_home': 4936,
    u'sci_issuetoc': 9144629, u'sci_issues': 2747492}'''

    dict_ret = {}

    for k,v in dict_mon.iteritems():
        split = k.split('_')

        if (split[0] == 'sci'):
            dict_index[k] =v

    return dict_ret

def mongoo_by_index_year(dict_mon, index, year):

    '''Exemplo: {u'art': {u'2011': [(u'01', 1959628), (u'02', 2373095),
    (u'03', 2322171),(u'04', 3143795), (u'05', 2646287), (u'06', 1840974),
    (u'07', 1522486), (u'08', 2219722), (u'09', 2369087)]}}'''

    dict_ret = {}
    months = []

    for k,v in dict_mon.iteritems():
        split = k.split('_')

        if (len(split) == 2 and split[0] == index and split[1][0:4] == year):
            months.append((split[1][4:6], v))
            months.sort()

    #insert the index
    dict_ret[index] = {split[1][0:4]:months}

    return dict_ret


def mongoo_by_index_year_lang(dict_mon, index, year, lang):

    '''{u'art': {u'2011pt': [(u'01', 1559206), (u'02', 1424589), (u'03', 1789356),
    (u'04', 3611296), (u'05', 2351421), (u'06', 1509440), (u'07', 1458762),
    (u'08', 1756826), (u'09', 2112764)]}}'''

    dict_ret = {}
    months = []

    for k,v in dict_mon.iteritems():
        split = k.split('_')

        if (len(split) == 3 and split[0] == index and split[1][0:4] == year and split[2] == lang):
            months.append((split[1][4:6], v))
            months.sort()

    #insert the index
    dict_ret[index] = {split[1][0:4]+lang:months}

    return dict_ret


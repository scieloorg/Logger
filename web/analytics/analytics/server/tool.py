#Tools for dictionary
from OrderedDict import *

def dict_order_by_key(dictparam):
    return OrderedDict((k, dictparam[k]) for k in sorted(dictparam))

def dict_slice_key(dictmon, start_key, end_key):
    return dict((k, v) for k, v in dictmon.iteritems() if start_key <= k <= end_key)

def get_months(month):
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

def list_month_access(dictmon, index, year):
    
    '''Exemplo:[["jan", 1959628], ["fev", 2373095], ["mar", 2322171], ...]'''
    
    dict_index = dict()
    list_ret = list()

    #loop on dict returned by mongo
    for k, v in dictmon.iteritems():
        split = k.split('_')
        if(split[0] == index and len(split) == 2 and split[1][0:4] == year):
            dict_index[split[1][4:6][1]] = v
    
    #loop on dict to return list
    for k, v in dict_order_by_key(dict_index).iteritems():
        list_ret.append([get_months(str(k)), v])
        
    return list_ret

def list_month_access_range(dictmon, index, start_range, end_range):

    '''Exemplo:[["jan", 1959628], ["fev", 2373095], ["mar", 2322171], ...]'''

    dict_index = dict()
    list_ret = list()

    #loop on dict returned by mongo
    for k, v in dictmon.iteritems():
        split = k.split('_')
        if(split[0] == index and len(split) == 2):
            dict_index[split[1]] = v

    dict_slice = dict_slice_key(dict_index, start_range, end_range)

    #loop on dict to return list
    for k, v in dict_order_by_key(dict_slice).iteritems():
        list_ret.append([str(k), v])

    return list_ret

def list_pages_access(dictmon, index):

    '''[["abstract", 44386973], ["alphabetic", 35824], ["arttext", 139816316],...]'''

    dict_index = dict()
    list_ret = list()

    #loop on dict returned by mongo
    for k, v in dictmon.iteritems():
        split = k.split('_')
        if(split[0] == index and len(split) == 2):
            dict_index[split[1]] = v

    #loop on dict to return list
    for k, v in dict_order_by_key(dict_index).iteritems():
        list_ret.append([str(k), v])

    return list_ret

def list_access(dictmon, index, year):
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

def list_two_year(dictmon, index, year1, year2):
    list_ret = []
    
    y1 = list_access(dictmon, index, year1)

    y2 = list_access(dictmon, index, year2)
    
    for i, (access_y1,access_y2) in enumerate(zip(y1, y2)):
        i = i+1
        list_ret.append([get_months(str(i)), access_y1, access_y2])
   
    #return dict_ret
    return list_ret


def list_two_index(dictmon, year, index1, index2):
    list_ret = []

    i1 = list_access(dictmon, index1, year)
    
    i2 = list_access(dictmon, index2, year)

    for i, (index_i1,index_i2) in enumerate(zip(i1, i2)):
        i = i+1
        list_ret.append([get_months(str(i)), index_i1, index_i2])

    #return dict_ret
    return list_ret

################################################################################


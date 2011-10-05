#!/usr/bin/python
# -*- encoding: utf-8 -*-

from pymongo import Connection
import tool


conn = Connection("192.168.1.86", 27017)

db = conn.scl_accesslog

analytics = db.scl_analytics

dict_mon = analytics.find_one({'site': 'www.scielo.br'})

print tool.mongoo_by_index_year(dict_mon, 'pdf','2011')

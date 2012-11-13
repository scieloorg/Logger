#!/usr/bin/env python
from logaccess_config import *
from pymongo import Connection

conn = Connection(MONGODB_DOMAIN, MONGODB_PORT)

db = conn[COLLECTION_CODE+"_accesslog"]
analytics = db[COLLECTION_CODE+"_analytics"]

books = [i for i in analytics.find({'context':'book'})]

print 'code;pdf 2012/03; pdf 2012/04;pdf 2012/05;pdf 2012/06;epu 2012/03 epu 2012/04;epu 2012/05;epu 2012/06;htm 2012/03;htm 2012/04;htm 2012/05;htm 2012/06'

for i in books:
  code = i['code']
  pm03 = ''
  pm04 = ''
  pm05 = ''
  pm06 = ''
  em03 = ''
  em04 = ''
  em05 = ''
  em06 = ''
  hm03 = ''
  hm04 = ''
  hm05 = ''
  hm06 = ''

  if i.has_key('pdf_201203'):
    pm03 = i['pdf_201203']

  if i.has_key('pdf_201204'):
    pm04 = i['pdf_201204']

  if i.has_key('pdf_201205'):
    pm05 = i['pdf_201205']

  if i.has_key('pdf_201206'):
    pm06 = i['pdf_201206']

  if i.has_key('epu_201203'):
    em03 = i['epu_201203']

  if i.has_key('epu_201204'):
    em04 = i['epu_201204']

  if i.has_key('epu_201205'):
    em05 = i['epu_201205']

  if i.has_key('epu_201206'):
    em06 = i['epu_201206']

  if i.has_key('htm_201203'):
    hm03 = i['htm_201203']

  if i.has_key('htm_201204'):
    hm04 = i['htm_201204']

  if i.has_key('htm_201205'):
    hm05 = i['htm_201205']

  if i.has_key('htm_201206'):
    hm06 = i['htm_201206']

  print '%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s' % (code,pm03,pm04,pm05,pm06,em03,em04,em05,em06,hm03,hm04,hm05,hm06)

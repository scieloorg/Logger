#!/usr/bin/env python
from logaccess_config import *
from pymongo import Connection
import urllib2
import json

data = urllib2.urlopen(TITLE_QUERY)
titles = json.loads(data.read())

conn = Connection(MONGODB_DOMAIN, MONGODB_PORT)
db = conn[COLLECTION_CODE+"_accesslog"]
analytics = db[COLLECTION_CODE+"_analytics"]

# Fitering all fields that is a serial type
access_serials = analytics.find({'serial':{'$exists':'true'}}).sort('total',-1)

# Creating a dict for each title with their subject areas
title_areas = {}
for title in titles['rows']:
    issn = title['value']['issn'].upper()
    areas = title['value']['subject']
    title_areas.setdefault(issn,areas)

serial_totals = {}
for serial in access_serials:
    ser_issn = serial['serial'].upper()
    ser_total = serial['total']
    serial_totals.setdefault(ser_issn,ser_total)

tot_by_areas = {}
tot_ok = 0
tot_fail = 0
for issn,areas in title_areas.items():
    for area in areas:
        print "ISSN %s %s" % (issn,area)
        tot = tot_by_areas.setdefault(area,0)
        try:
            tot_by_areas.update({area:tot+serial_totals[issn.upper()]})
            tot_ok += 1
        except:
            tot_fail += 1

print tot_by_areas
print tot_ok
print 

for area,total in tot_by_areas.items():
    print "%s|%s" % (area,total)
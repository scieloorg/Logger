#!/usr/bin/env python
from logaccess_config import *
import apachelog
from pymongo import Connection 
import sys
import os
from lib.ip2country.ip2country import IP2Country
from datetime import date
from urlparse import urlparse

conn = Connection('localhost', 27017)

db = conn.accesslog
proc_files = db.processed_files
error_log = db.error_log
analytics = db.analytics
analytics.ensure_index('site')
analytics.ensure_index('serial')
analytics.ensure_index('issuetoc')
analytics.ensure_index('arttext')
analytics.ensure_index('abstract')
analytics.ensure_index('pdf')
analytics.ensure_index('page')
analytics.ensure_index('issn')
analytics.ensure_index('issue')
print "listing log files at: "+LOGS_DIR

logfiles = os.listdir(LOGS_DIR)

for file in logfiles:
    fileloaded = open(LOGS_DIR+"/"+file, 'r')
    cf = "country_"+file
    if proc_files.find({'_id':cf}).count() == 0:
        pfpost = {} 
        pfpost['proc_date'] = date.isoformat(date.today())
        pfpost['_id'] = cf
        proc_files.insert(pfpost)
        print "processing "+file
        count=0
        for line in fileloaded:
            if "GET /scielo.php?script=" in line:
                count=count+1
                p = apachelog.parser(APACHE_LOG_FORMAT)
                try:
                    data = p.parse(line)
                except:
                    sys.stderr.write("Unable to parse %s" % line)

                if MONTH_DICT.has_key(data['%t'][4:7].upper()):
                    month = MONTH_DICT[data['%t'][4:7].upper()]
                else:
                    continue
                
                dat = data['%t'][8:12]+month
                url = data['%r'].split(' ')[1]
                ip = data['%h']
                
                i2pc = IP2Country(verbose=False)
                cc, country = i2pc.lookup(ip)
                country = str(cc).upper()
                #print str(cc)+" "+ip
                
                params = urlparse(url).query.split('&')
                par = {}
                
                for param in params:
                    tmp = param.split('=')
                    if len(tmp) == 2:
                        par[tmp[0]] = tmp[1]
                par['date'] = dat

                #language = ""
                #if par.has_key('tlng'):
                    #if par['tlng'].upper() in ALLOWED_LANGUAGES:
                        #language=par['tlng'].lower()
                    #else:
                        #language='default'
                #else:
                    #language='default'
                    
                if par.has_key('script'):
                    if par['script'].upper() in ALLOWED_SCRIPTS:
                        
                        script=par['script'].lower()
                        analytics.update({"site":"www.scielo.br"}, {"$inc":{"country_"+country:1, "country_"+par['date']+"_"+country:1}},True)
                        # CREATING SERIAL LOG DOCS
                        if par.has_key('pid'):
                            analytics.update({"serial":str(par["pid"]).replace('S','')[0:9]}, {"$inc":{"country_"+country:1, "country_"+par['date']+"_"+country:1}},True)

                        if par['script'].upper() == "SCI_ISSUETOC":
                            if par.has_key('pid'):
                                analytics.update({"issuetoc":par["pid"]}, {"$set":{'page':script,'issn':par["pid"][0:9]}, "$inc":{"country_"+country:1, "country_"+par['date']+"_"+country:1}},True)
                        elif par['script'].upper() == "SCI_ABSTRACT":
                            if par.has_key('pid'):
                                analytics.update({"abstract":par["pid"]}, {"$set":{'page':script,'issn':par["pid"][1:10],'issue':par["pid"][1:18]},"$inc":{"country_"+country:1, "country_"+par['date']+"_"+country:1}},True)
                        elif par['script'].upper() == "SCI_ARTTEXT":
                            if par.has_key('pid'):
                                analytics.update({"arttext":par["pid"]}, {"$set":{'page':script,'issn':par["pid"][1:10],'issue':par["pid"][1:18]},"$inc":{"country_"+country:1, "country_"+par['date']+"_"+country:1}},True)
                        elif par['script'].upper() == "SCI_PDF":
                            if par.has_key('pid'):
                                analytics.update({"pdf":par["pid"]}, {"$set":{'page':script,'issn':par["pid"][1:10],'issue':par["pid"][1:18]},"$inc":{"country_"+country:1, "country_"+par['date']+"_"+country:1}},True)
    else:
        print file+" was already processed"

#proc_files.drop()

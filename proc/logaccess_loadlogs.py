#!/usr/bin/env python
from logaccess_config import *
import apachelog
from pymongo import Connection 
import sys
import os
from datetime import date
from urlparse import urlparse

conn = Connection('localhost', 27017)

db = conn.accesslog
proc_files = db.processed_files
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
    if proc_files.find({'_id':file}).count() == 0:
        pfpost = {} 
        pfpost['proc_date'] = date.isoformat(date.today())
        pfpost['_id'] = file
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

                dat = data['%t'][8:12]+MONTH_DICT[data['%t'][4:7].upper()]
                url = data['%r'].split(' ')[1]
                ip = data['%h']
                
                country = os.system("lib/ip2contry/locateIP "+ip)
                
                params = urlparse(url).query.split('&')
                par = {}
                
                for param in params:
                    tmp = param.split('=')
                    if len(tmp) == 2:
                        par[tmp[0]] = tmp[1]
                par['date'] = dat
                #print par
                language = ""
                if par.has_key('tlng'):
                    if par['tlng'].upper() in ALLOWED_LANGUAGES:
                        language=par['tlng']
                    else:
                        language='default'
                else:
                    language='default'
                if par.has_key('script'):
                    if par['script'].upper() in ALLOWED_SCRIPTS:
                        analytics.update({"site":"www.scielo.br"}, {"$inc":{par["script"]:1,'total':1,par['date']:1}},True)
                        # CREATING SERIAL LOG DOCS
                        
                        analytics.update({"serial":par["pid"].replace('S','')[0:9]}, {"$inc":{'total':1,par['script']:1,par['date']:1,'lng_'+par['date']+'_'+language:1,country:1}},True)
                        
                        #if par['script'].upper() == "SCI_SERIAL":
                            #if par.has_key('pid'):
                                #analytics.update({"serial":par["pid"]}, {"$set":{'page':par['script']},"$inc":{'total':1,par['date']:1}},True)
                            #else:
                                #analytics.update({"site":"www.scielo.br"}, {"$inc":{'sci_serial_error':1}},True)
                        if par['script'].upper() == "SCI_ISSUETOC":
                            if par.has_key('pid'):
                                analytics.update({"issuetoc":par["pid"]}, {"$set":{'page':par['script'],'issn':par["pid"][0:9]},"$inc":{'total':1,par['date']:1,country:1}},True)
                            else:
                                analytics.update({"site":"www.scielo.br"}, {"$inc":{'sci_issuetoc_error':1}},True)
                        elif par['script'].upper() == "SCI_ABSTRACT":
                            if par.has_key('pid'):
                                analytics.update({"abstract":par["pid"]}, {"$set":{'page':par['script'],'issn':par["pid"][1:10],'issue':par["pid"][1:18]},"$inc":{'total':1,par['date']:1,'lng_'+par['date']+'_'+language:1,country:1}},True)
                            else:
                                analytics.update({"site":"www.scielo.br"}, {"$inc":{'sci_abstract_error':1}},True)
                        elif par['script'].upper() == "SCI_ARTTEXT":
                            if par.has_key('pid'):
                                analytics.update({"arttext":par["pid"]}, {"$set":{'page':par['script'],'issn':par["pid"][1:10],'issue':par["pid"][1:18]},"$inc":{'total':1,par['date']:1,'lng_'+par['date']+'_'+language:1,country:1}},True)
                            else:
                                analytics.update({"site":"www.scielo.br"}, {"$inc":{'sci_arttext_error':1}},True)
                        elif par['script'].upper() == "SCI_PDF":
                            if par.has_key('pid'):
                                analytics.update({"pdf":par["pid"]}, {"$set":{'page':par['script'],'issn':par["pid"][1:10],'issue':par["pid"][1:18]},"$inc":{'total':1,par['date']:1,'lng_'+par['date']+'_'+language:1,country:1}},True)
                            else:
                                analytics.update({"site":"www.scielo.br"}, {"$inc":{'sci_pdf_error':1}},True)
                    else:
                        analytics.update({"site":"www.scielo.br"}, {"$inc":{'error':1}},True)
            #if count == 20:
                #break
    else:
        print file+" was already processed"

#proc_files.drop()
#!/usr/bin/env python
from logaccess_config import *
import apachelog
from pymongo import Connection 
import sys
import os
import re
import json
import urllib2
from urlparse import urlparse
from datetime import date

def getTitles():
    try:
        query = urllib2.urlopen(COUCHDB_DATABASE+"/"+COUCHDB_TITLE_QUERY)
    except:
        return False

    titles = json.loads(query.read())

    title_dict = {}
    for title in titles['rows']:
        title_dict[title['doc']['v68'][0]['_']]=title['doc']['v400'][0]['_'];

    return title_dict

def validate_pid(script, pid):   
    if script == "sci_issuetoc":
        if re.search(REGEX_ISSUE,pid):
            return True
    elif script == "sci_abstract" or re.search(REGEX_FBPE,pid):
        if re.search(REGEX_ARTICLE,pid):
            return True
    elif script == "sci_arttext":
        if re.search(REGEX_ARTICLE,pid) or re.search(REGEX_FBPE,pid):
            return True
    elif script == "sci_pdf":
        if re.search(REGEX_ARTICLE,pid) or re.search(REGEX_FBPE,pid):
            return True
    elif script == "sci_serial":
        if re.search(REGEX_ISSN,pid):
            return True
    elif script == "sci_issues":
        if re.search(REGEX_ISSN,pid):
            return True
    return False

def validate_pdf(filepath,acronDict):
    pdf_spl = filepath.split("/")
    if len(pdf_spl) > 2:
        if pdf_spl[1] == 'pdf':
            if pdf_spl[2] != '':
                if pdf_spl[2] in acronDict:
                    return True
    return False
    
def validate_date(dat):
    if len(str(dat)) == 6:
        if int(dat[0:4]) <= int(date.today().year) and (int(dat[4:6]) >= 1 and int(dat[4:6]) <= 12):
            return True
    return False


# Retrieving from CouchDB a Title dictionary as: dict['bjmbr']=XXXX-XXXX
acronDict = getTitles()

if ( acronDict != False):
    conn = Connection(MONGODB_DOMAIN, MONGODB_PORT)

    db = conn[COLLECTION_CODE+"_accesslog"]
    proc_files = db[COLLECTION_CODE+"_processed_files"]
    error_log = db[COLLECTION_CODE+"_error_log"]
    analytics = db[COLLECTION_CODE+"_analytics"]
    analytics.ensure_index('site')
    analytics.ensure_index('serial')
    analytics.ensure_index('issuetoc')
    analytics.ensure_index('arttext')
    analytics.ensure_index('abstract')
    analytics.ensure_index('pdf')
    analytics.ensure_index('dwn')
    analytics.ensure_index('acron')
    analytics.ensure_index('page')
    analytics.ensure_index('issn')
    analytics.ensure_index('issue')
    error_log.ensure_index('file')

    for logdir in LOG_DIRS:
        
        print "listing log files at: "+logdir
        
        logfiles = os.popen('ls '+logdir+'/*access.log')
        for file in logfiles:
            filepath=file.strip()
            fileloaded = open(filepath, 'r')
            if proc_files.find({'_id':filepath}).count() == 0:
                lines = 0
                lines = os.popen('cat '+filepath+' | wc -l').read().strip()
                proc_files.update({"_id":filepath},{'$set':{'proc_date':date.isoformat(date.today()),'status':'processing','lines': lines}},True)
                print "processing "+filepath
                linecount=0
                for line in fileloaded:
                    linecount=linecount+1
                    proc_files.update({"_id":filepath},{'$set':{'line':linecount}},True)                    

                    #PDF FILES DOWNLOAD
                    if "GET" in line and ".pdf" in line:
                        p = apachelog.parser(APACHE_LOG_FORMAT)
                        try:
                            data = p.parse(line)
                        except:
                            sys.stderr.write("Unable to parse %s" % line)
                            analytics.update({"site":COLLECTION_DOMAIN},{"$inc":{'err_total':1,'err_unabletoparser':1}},True)
                            error_log.update({"file":filepath},{"$set":{'lines':linecount},"$inc":{'err_unabletoparser':1}},True)
                            continue
        
                        month=""
                        if MONTH_DICT.has_key(data['%t'][4:7].upper()):
                            month = MONTH_DICT[data['%t'][4:7].upper()]
        
                        dat = data['%t'][8:12]+month
                        
                        if validate_date(dat):

                            stopwordflag = False
                            for stopword in STOP_WORDS:
                                if stopword in line:
                                    analytics.update({"site":COLLECTION_DOMAIN},{"$inc":{'bot_'+dat:1,'bot_total':1}},True)
                                    stopwordflag = True

                            if stopwordflag == True:
                                continue #register as a bot access and skip apachelog lines

                            pdfid = data['%r'][4:data['%r'].find('.pdf')]
                            #cleaning // and %0D/
                            pdfid = pdfid.replace("//","/")
                            pdfid = pdfid.replace("%0D/","")
                            if validate_pdf(pdfid,acronDict):
                                pdf_spl = pdfid.split("/")
                                issn = acronDict[pdf_spl[2]]
                                analytics.update({"site":COLLECTION_DOMAIN}, {"$inc":{'dwn':1,'dwn_'+dat:1,'total':1,"dat_"+dat:1}},True)
                                analytics.update({"serial":issn}, {"$inc":{'total':1,"dwn_"+dat:1}},True)
                                analytics.update({"dwn":pdfid}, {"$set":{'page':'pdf_download','issn':issn},"$inc":{'total':1,"dwn_"+dat:1}},True)
                            else:
                                analytics.update({"dwn":pdfid}, {"$set":{'page':'pdf_download'},"$inc":{"err":1}},True)
                                analytics.update({"site":COLLECTION_DOMAIN},{"$inc":{'err_total':1,'err_dwn':1}},True)
                                
                    #PAGES PATTERN
                    if "GET /scielo.php" in line and "script" in line and "pid" in line:
                        p = apachelog.parser(APACHE_LOG_FORMAT)
                        try:
                            data = p.parse(line)
                        except:
                            sys.stderr.write("Unable to parse %s" % line)
                            analytics.update({"site":COLLECTION_DOMAIN},{"$inc":{'err_total':1,'err_unabletoparser':1}},True)
                            error_log.update({"file":filepath},{"$set":{'lines':linecount},"$inc":{'err_unabletoparser':1}},True)
                            continue #register as a bot access and skip apachelog line
        
                        month=""
                        if MONTH_DICT.has_key(data['%t'][4:7].upper()):
                            month = MONTH_DICT[data['%t'][4:7].upper()]
                            
                        dat = data['%t'][8:12]+month
                        url = data['%r'].split(' ')[1]
        
                        params = urlparse(url).query.split('&')
                        par = {}
                        
                        for param in params:
                            tmp = param.split('=')
                            if len(tmp) == 2:
                                par[tmp[0]] = tmp[1]
        
                        if par.has_key('script'): #Validating if has script
                            script = par['script'].lower()
                            if script in ALLOWED_SCRIPTS: #Validation if the script is allowed
                                if validate_date(dat):

                                    stopwordflag = False
                                    for stopword in STOP_WORDS:
                                        if stopword in line:
                                            analytics.update({"site":COLLECTION_DOMAIN},{"$inc":{'bot_'+dat:1,'bot_total':1}},True)
                                            stopwordflag = True

                                    if stopwordflag == True:
                                        continue #register as a bot access and skip apachelog line

                                    if par.has_key('pid'):
                                        pid = par['pid'].replace('S','').replace('s','').strip()
                                        if validate_pid(script,pid):
                                            # CREATING SERIAL LOG DOCS
                                            analytics.update({"site":COLLECTION_DOMAIN}, {"$inc":{script:1,'total':1,"dat_"+dat:1}},True)
                                            analytics.update({"serial":pid[0:9]}, {"$inc":{'total':1,script:1,"dat_"+dat:1}},True)
                                            if script == "sci_issuetoc":
                                                analytics.update({"issuetoc":pid}, {"$set":{'page':script,'issn':pid[0:9]},"$inc":{'total':1,"dat_"+dat:1}},True)
                                                analytics.update({"serial":pid[0:9]}, {"$inc":{'toc_'+dat:1}},True)
                                                analytics.update({"site":COLLECTION_DOMAIN}, {"$inc":{"toc_"+dat:1}},True)
                                            elif script == "sci_abstract":
                                                analytics.update({"abstract":pid}, {"$set":{'page':script,'issn':pid[0:9],'issue':pid[0:17]},"$inc":{'total':1,"dat_"+dat:1}},True)
                                                analytics.update({"serial":pid[0:9]}, {"$inc":{'abs_'+dat:1}},True)
                                                analytics.update({"site":COLLECTION_DOMAIN}, {"$inc":{"abs_"+dat:1}},True)
                                            elif script == "sci_arttext":
                                                analytics.update({"arttext":pid}, {"$set":{'page':script,'issn':pid[0:9],'issue':pid[0:17]},"$inc":{'total':1,"dat_"+dat:1}},True)
                                                analytics.update({"serial":pid[0:9]}, {"$inc":{'art_'+dat:1}},True)
                                                analytics.update({"site":COLLECTION_DOMAIN}, {"$inc":{"art_"+dat:1}},True)
                                            elif script == "sci_pdf":
                                                analytics.update({"pdf":pid}, {"$set":{'page':script,'issn':pid[1:10],'issue':pid[0:17]},"$inc":{'total':1,"dat_"+dat:1}},True)
                                                analytics.update({"serial":pid[0:9]}, {"$inc":{'pdf_'+dat:1}},True)
                                                analytics.update({"site":COLLECTION_DOMAIN}, {"$inc":{"pdf_"+dat:1}},True)
                                            elif script == "sci_home":
                                                analytics.update({"site":COLLECTION_DOMAIN}, {"$inc":{"hom_"+dat:1}},True)
                                            elif script == "sci_issues":
                                                analytics.update({"serial":pid[0:9]}, {"$inc":{'iss_'+dat:1}},True)
                                                analytics.update({"site":COLLECTION_DOMAIN}, {"$inc":{"iss_"+dat:1}},True)
                                            elif script == "sci_alphabetic":
                                                analytics.update({"site":COLLECTION_DOMAIN}, {"$inc":{"alp_"+dat:1}},True)
                                        else:
                                            #print str(validate_pid(script,pid))+" "+script+" "+pid
                                            analytics.update({"site":COLLECTION_DOMAIN}, {"$inc":{'err_total':1,'err_pid':1}},True)
                                            error_log.update({"file":filepath},{"$set":{'lines':linecount},"$inc":{'err_pid':1}},True)
                                    else:
                                        analytics.update({"site":COLLECTION_DOMAIN}, {"$inc":{'err_total':1,'err_empty_pid':1}},True)
                                        error_log.update({"file":filepath},{"$set":{'lines':linecount},"$inc":{'err_empty_pid':1}},True)
                                else:
                                    #print str(linecount)+" "+str(dat)+" "+str(validate_date(dat))
                                    analytics.update({"site":COLLECTION_DOMAIN}, {"$inc":{'err_total':1,'err_date':1}},True)
                                    error_log.update({"file":filepath},{"$set":{'lines':linecount},"$inc":{'err_date':1}},True)
                            else:
                                analytics.update({"site":COLLECTION_DOMAIN},{"$inc":{'err_total':1,'err_script':1}},True)
                                error_log.update({"file":filepath},{"$set":{'lines':linecount},"$inc":{'err_script':1}},True)
                        else:
                            analytics.update({"site":COLLECTION_DOMAIN}, {"$inc":{'err_total':1,'err_empty_script':1}},True)
                            error_log.update({"file":filepath},{"$set":{'lines':linecount},"$inc":{'err_empty_script':1}},True)
                proc_files.update({"_id":filepath},{'$set':{'status':'processed'}},True)
            else:
                print filepath+" was already processed"
else:
    print "Connection to CouchDB Fail" 

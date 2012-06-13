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
  
def validate_date(data):
  """
    Simple validate each log line date.
    The year must be minor then the actual year
    The month must be between 1 and 12
    Both must be a valid number
  """
  allowed_month = range(1,13)
  today_year = date.today().year

  month=""
  if MONTH_DICT.has_key(data['%t'][4:7].upper()):
    month = MONTH_DICT[data['%t'][4:7].upper()]

  dat = data['%t'][8:12]+month
  
  if len(str(dat)) == 6:
    if int(dat[0:4]) <= int(today_year) and (int(dat[4:6]) in allowed_month):
      return dat
 
  return False

def is_bot(line, date_log):
  """
    Simple validate each log line against the STOP_WORDS defined in the conf file.
  """
  for stopword in STOP_WORDS:
    if stopword in line:
      return True
  return False

def registering_log(line,date_log,compiled_regex):
  """
    Register the log access acording to the ALLOWED_PATTERNS
  """
  for doc_type, pattern in ALLOWED_PATTERNS.iteritems():
      search_results = compiled_regex[doc_type].search(line)
      if search_results:
        doc_type3=doc_type[0:3]
        code = ""
        for i in search_results.groups():
          if i:
            code = i
            break
        analytics.update({"site":COLLECTION_DOMAIN},{"$inc":{doc_type3+'_'+date_log:1,doc_type3+'_total':1}},True)
        analytics.update({"code":code}, {"$set":pattern['index'],"$inc":{doc_type3:1,doc_type3+'_'+date_log:1}},True)

        break # Dont need to keep trying to fetch a pattern one was already found.

# Compiling regex
compiled_regex = {}
for doc_type, pattern in ALLOWED_PATTERNS.iteritems():
  print "compiling regex %s for doctype %s" % (pattern['code'],doc_type)
  compiled_regex[doc_type] = re.compile(pattern['code'])

conn = Connection(MONGODB_DOMAIN, MONGODB_PORT)
db = conn[COLLECTION_CODE+"_accesslog"]
proc_files = db[COLLECTION_CODE+"_processed_files"]
error_log = db[COLLECTION_CODE+"_error_log"]
analytics = db[COLLECTION_CODE+"_analytics"]

# Creating Index according to Allowed Urls defined in the conf file
for page,index in ALLOWED_PATTERNS.iteritems():
  analytics.ensure_index(page)
  for indexkey in index['index']:
    analytics.ensure_index(indexkey)


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
        p = apachelog.parser(APACHE_LOG_FORMAT)
        try:
          data = p.parse(line)
        except:
          sys.stderr.write("Unable to parse %s" % line)
          analytics.update({"site":COLLECTION_DOMAIN},{"$inc":{'err_total':1,'err_unabletoparser':1}},True)
          error_log.update({"file":filepath},{"$set":{'lines':linecount},"$inc":{'err_unabletoparser':1}},True)
          continue
        
        #Validating the log date
        valid_date = validate_date(data)
        if not valid_date:
          continue

        # Validating Agains Bot List
        if is_bot(line,data):
          analytics.update({"site":COLLECTION_DOMAIN},{"$inc":{'bot_'+valid_date:1,'bot_total':1}},True)
          continue

        # Registering Log
        registering_log(line,valid_date,compiled_regex)

      #Changing the status of the log file to processed after all lines was parsed
      proc_files.update({"_id":filepath},{'$set':{'status':'processed'}},True)
    else:
      print filepath+" was already processed"

proc_files.drop()
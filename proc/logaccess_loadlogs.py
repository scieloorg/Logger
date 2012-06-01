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
  month=""
  if MONTH_DICT.has_key(data['%t'][4:7].upper()):
    month = MONTH_DICT[data['%t'][4:7].upper()]

  dat = data['%t'][8:12]+month

  today_year = date.today().year
  if len(str(dat)) == 6:
    if int(dat[0:4]) <= int(today_year) and (int(dat[4:6]) >= 1 and int(dat[4:6]) <= 12):
      return dat
  return False

def is_bot(line, date_log):
  for stopword in STOP_WORDS:
    if stopword in line:
      return True
  return False
 
conn = Connection(MONGODB_DOMAIN, MONGODB_PORT)

db = conn[COLLECTION_CODE+"_accesslog"]
proc_files = db[COLLECTION_CODE+"_processed_files"]
error_log = db[COLLECTION_CODE+"_error_log"]
analytics = db[COLLECTION_CODE+"_analytics"]

# Creating Index according to Allowed Urls defined in the conf file
for index in ALLOWED_PATTERNS:
  analytics.ensure_index(index)

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
        
        valid_date = validate_date(data)
        if not valid_date:
          print "Data Errada!"
          continue

        # REGISTERING LOGS
        if is_bot(line,data):
          print "AAAAHHHH eh um BOT"
          analytics.update({"site":COLLECTION_DOMAIN},{"$inc":{'bot_'+valid_date:1,'bot_total':1}},True)
          continue

      #Changing the status of the log file to processed after all lines was parsed
      proc_files.update({"_id":filepath},{'$set':{'status':'processed'}},True)
    else:
      print filepath+" was already processed"

proc_files.drop()
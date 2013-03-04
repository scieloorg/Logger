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
        query = urllib2.urlopen(COUCHDB_DATABASE + "/" + COUCHDB_TITLE_QUERY)
    except:
        return False

    titles = json.loads(query.read())

    title_dict = {}
    for title in titles['rows']:
        title_dict[title['doc']['v68'][0]['_']] = title['doc']['v400'][0]['_']

    return title_dict


def validate_pid(script, pid):
    if script == "sci_issuetoc":
        if re.search(REGEX_ISSUE, pid):
            return True
    elif script == "sci_abstract" or re.search(REGEX_FBPE, pid):
        if re.search(REGEX_ARTICLE, pid):
            return True
    elif script == "sci_arttext":
        if re.search(REGEX_ARTICLE, pid) or re.search(REGEX_FBPE, pid):
            return True
    elif script == "sci_pdf":
        if re.search(REGEX_ARTICLE, pid) or re.search(REGEX_FBPE, pid):
            return True
    elif script == "sci_serial":
        if re.search(REGEX_ISSN, pid):
            return True
    elif script == "sci_issues":
        if re.search(REGEX_ISSN, pid):
            return True
    return False


def validate_pdf(filepath, acronDict):
    pdf_spl = filepath.split("/")
    if len(pdf_spl) > 2:
        if pdf_spl[1] == 'pdf':
            if pdf_spl[2] != '':
                if pdf_spl[2] in acronDict:
                    return True
    return False


def validate_date(dat):
    if len(str(dat)) == 10:
        if int(dat[0:4]) <= int(date.today().year) and \
        (int(dat[5:7]) >= 1 and int(dat[5:7]) <= 12) and \
        (int(dat[8:10]) >= 1 and int(dat[8:10]) <= 31):
            return True
    return False


# Retrieving from CouchDB a Title dictionary as: dict['bjmbr']=XXXX-XXXX
acronDict = getTitles()

if (acronDict != False):
    for logdir in LOG_DIRS:

        print "listing log files at: " + logdir

        logfiles = os.popen('ls ' + logdir + '/*access.log')

        for f in logfiles:
            filepath = f.strip()
            fileloaded = open(filepath, 'r')
            print "processing " + filepath
            for line in fileloaded:
                #PDF FILES DOWNLOAD
                if "GET" in line and ".pdf" in line:
                    p = apachelog.parser(APACHE_LOG_FORMAT)
                    try:
                        data = p.parse(line)
                    except:
                        sys.stderr.write("Unable to parse %s" % line)
                        continue

                    day = data['%t'][1:3]
                    year = data['%t'][8:12]
                    month = ""
                    if data['%t'][4:7].upper() in MONTH_DICT:
                        month = MONTH_DICT[data['%t'][4:7].upper()]

                    dat = '{0}-{1}-{2}'.format(year, month, day)

                    if validate_date(dat):
                        stopwordflag = False
                        for stopword in STOP_WORDS:
                            if stopword in line:
                                stopwordflag = True

                        if stopwordflag == True:
                            continue  # register as a bot access and skip apachelog lines

                        pdfid = data['%r'][4:data['%r'].find('.pdf')]

                        #cleaning // and %0D/
                        pdfid = pdfid.replace("//", "/")
                        pdfid = pdfid.replace("%0D/", "")

                        if validate_pdf(pdfid, acronDict):
                            pdf_spl = pdfid.split("/")
                            issn = acronDict[pdf_spl[2]]
                            # REGISTRA ACESSO DE DOWNLOAD
                            #qrs = "code={0}&journal={0}&issue={0}&access_date={0}".format(pdfid, issn,,dat)
                            #req = urllib2.Request("http://localhost:8860/api/v1/pdf", qrs)
                            #urllib2.urlopen(req)
                            qrs = "code=www.scielo.br&page=download&access_date={0}".format(dat)
                            req = urllib2.Request("http://localhost:8860/api/v1/general", qrs)
                            urllib2.urlopen(req)
                #PAGES PATTERN
                if "GET /scielo.php" in line and "script" in line and "pid" in line:
                    p = apachelog.parser(APACHE_LOG_FORMAT)
                    try:
                        data = p.parse(line)
                    except:
                        sys.stderr.write("Unable to parse %s" % line)
                        continue  # register as a bot access and skip apachelog line

                    day = data['%t'][1:3]
                    year = data['%t'][8:12]
                    month = ""
                    if data['%t'][4:7].upper() in MONTH_DICT:
                        month = MONTH_DICT[data['%t'][4:7].upper()]

                    dat = '{0}-{1}-{2}'.format(year, month, day)

                    url = data['%r'].split(' ')[1]

                    params = urlparse(url).query.split('&')
                    par = {}

                    for param in params:
                        tmp = param.split('=')
                        if len(tmp) == 2:
                            par[tmp[0]] = tmp[1]

                    if 'script' in par:  # Validating if has script
                        script = par['script'].lower()
                        if script in ALLOWED_SCRIPTS:  # Validation if the script is allowed
                            if validate_date(dat):
                                stopwordflag = False
                                for stopword in STOP_WORDS:
                                    if stopword in line:
                                        stopwordflag = True

                                if stopwordflag == True:
                                    continue  # register as a bot access and skip apachelog line

                                if 'pid' in par:
                                    pid = par['pid'].replace('S', '').replace('s', '').strip()
                                    if validate_pid(script, pid):
                                        # CREATING SERIAL LOG DOCS
                                        if script == "sci_issuetoc":
                                            # ISSUE ACCESS
                                            qrs = "code={0}&journal={1}&access_date={2}".format(pid, pid[0:9], dat)
                                            req = urllib2.Request("http://localhost:8860/api/v1/issue", qrs)
                                            urllib2.urlopen(req)
                                            qrs = "code=www.scielo.br&page=sci_issuetoc&access_date={0}".format(dat)
                                            req = urllib2.Request("http://localhost:8860/api/v1/general", qrs)
                                            urllib2.urlopen(req)
                                        elif script == "sci_abstract":
                                            # ARTICLE ACCESS
                                            qrs = "code={0}&journal={1}&issue={2}&access_date={3}".format(pid, pid[0:9], pid[0:17], dat)
                                            req = urllib2.Request("http://localhost:8860/api/v1/article", qrs)
                                            urllib2.urlopen(req)
                                            qrs = "code=www.scielo.br&page=sci_abstract&access_date={0}".format(dat)
                                            req = urllib2.Request("http://localhost:8860/api/v1/general", qrs)
                                            urllib2.urlopen(req)
                                        elif script == "sci_arttext":
                                            qrs = "code={0}&journal={1}&issue={2}&access_date={3}".format(pid, pid[0:9], pid[0:17], dat)
                                            req = urllib2.Request("http://localhost:8860/api/v1/article", qrs)
                                            urllib2.urlopen(req)
                                            qrs = "code=www.scielo.br&page=sci_arttext&access_date={0}".format(dat)
                                            req = urllib2.Request("http://localhost:8860/api/v1/general", qrs)
                                            urllib2.urlopen(req)
                                        elif script == "sci_pdf":
                                            qrs = "code={0}&journal={1}&issue={2}&access_date={3}".format(pid, pid[0:9], pid[0:17], dat)
                                            req = urllib2.Request("http://localhost:8860/api/v1/pdf", qrs)
                                            urllib2.urlopen(req)
                                            qrs = "code=www.scielo.br&page=sci_pdf&access_date={0}".format(dat)
                                            req = urllib2.Request("http://localhost:8860/api/v1/general", qrs)
                                            urllib2.urlopen(req)
                                        elif script == "sci_home":
                                            qrs = "code=www.scielo.br&page=sci_home&access_date={0}".format(dat)
                                            req = urllib2.Request("http://localhost:8860/api/v1/general", qrs)
                                            urllib2.urlopen(req)
                                        elif script == "sci_issues":
                                            qrs = "code=www.scielo.br&page=sci_issues&access_date={0}".format(dat)
                                            req = urllib2.Request("http://localhost:8860/api/v1/general", qrs)
                                            urllib2.urlopen(req)
                                        elif script == "sci_alphabetic":
                                            qrs = "code=www.scielo.br&page=sci_alphabetic&access_date={0}".format(dat)
                                            req = urllib2.Request("http://localhost:8860/api/v1/general", qrs)
                                            urllib2.urlopen(req)
            proc_files.update({"_id": filepath}, {'$set': {'status': 'processed'}}, True)
else:
    print "Connection to CouchDB Fail"

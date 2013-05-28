#!/usr/bin/env python

import urllib2

from tools import *
from ratchet import *

# Retrieving from CouchDB a Title dictionary as: dict['bjmbr']=XXXX-XXXX
acrondict = getTitles()

allowed_issns = []
for key, issn in acrondict.items():
    allowed_issns.append(issn)

if acrondict:
    for logdir in get_logdirs():
        print "listing log files at: " + logdir
        for logfile in get_files_in_logdir(logdir):
            for line in get_file_lines(logfile):
                kind_of_access = log_line_triage(line)
                if kind_of_access:
                    parsed_line = parse_apache_line(line)
                    if parsed_line:
                        if kind_of_access == "PDF":
                            continue
                            pdfid = data['%r'][4:data['%r'].find('.pdf')]
                            #cleaning // and %0D/
                            pdfid = pdfid.replace("//", "/")
                            pdfid = pdfid.replace("%0D/", "")

                            if validate_pdf(pdfid, acrondict):
                                pdf_spl = pdfid.split("/")
                                issn = acrondict[pdf_spl[2]]
                                # REGISTRA ACESSO DE DOWNLOAD
                                qrs = "code={0}&page=download&access_date={1}".format(issn, parsed_line['iso_date'])
                                req = urllib2.Request("http://200.136.72.14:8860/api/v1/general", qrs)
                                urllib2.urlopen(req)
                                qrs = "code=www.scielosp.org&page=download&access_date={0}".format(parsed_line['iso_date'])
                                req = urllib2.Request("http://200.136.72.14:8860/api/v1/general", qrs)
                                urllib2.urlopen(req)

                        if kind_of_access == "HTML":
                            if is_allowed_query(parsed_line['query_string'], allowed_issns):
                                script = parsed_line['query_string']['script'][0]
                                pid = parsed_line['query_string']['pid'][0]
                                # CREATING SERIAL LOG DOCS
                                if script == "sci_serial":
                                    register_journal_page_access(pid, parsed_line['iso_date'])
                                elif script == "sci_abstract":
                                    # ARTICLE ACCESS
                                    qrs = "code={0}&journal={1}&issue={2}&access_date={3}".format(pid, pid[0:9], pid[0:17], parsed_line['iso_date'])
                                    req = urllib2.Request("http://200.136.72.14:8860/api/v1/article", qrs)
                                    urllib2.urlopen(req)
                                    qrs = "code=www.scielosp.org&page=sci_abstract&access_date={0}".format(parsed_line['iso_date'])
                                    req = urllib2.Request("http://200.136.72.14:8860/api/v1/general", qrs)
                                    urllib2.urlopen(req)
                                    qrs = "code={0}&page=sci_abstract&access_date={1}".format(pid[0:9], parsed_line['iso_date'])
                                    req = urllib2.Request("http://200.136.72.14:8860/api/v1/general", qrs)
                                    urllib2.urlopen(req)
                                elif script == "sci_issuetoc":
                                    # ISSUE ACCESS
                                    qrs = "code={0}&journal={1}&access_date={2}".format(pid, pid[0:9], parsed_line['iso_date'])
                                    req = urllib2.Request("http://200.136.72.14:8860/api/v1/issue", qrs)
                                    urllib2.urlopen(req)
                                    qrs = "code=www.scielosp.org&page=sci_issuetoc&access_date={0}".format(parsed_line['iso_date'])
                                    req = urllib2.Request("http://200.136.72.14:8860/api/v1/general", qrs)
                                    urllib2.urlopen(req)
                                    qrs = "code={0}&page=sci_issuetoc&access_date={1}".format(pid[0:9], parsed_line['iso_date'])
                                    req = urllib2.Request("http://200.136.72.14:8860/api/v1/general", qrs)
                                    urllib2.urlopen(req)
                                elif script == "sci_arttext":
                                    print "artigo"
                                    register_article_page_access(pid, parsed_line['iso_date'])
                                elif script == "sci_pdf":
                                    qrs = "code={0}&journal={1}&issue={2}&access_date={3}".format(pid, pid[0:9], pid[0:17], parsed_line['iso_date'])
                                    req = urllib2.Request("http://200.136.72.14:8860/api/v1/pdf", qrs)
                                    urllib2.urlopen(req)
                                    qrs = "code=www.scielosp.org&page=sci_pdf&access_date={0}".format(parsed_line['iso_date'])
                                    req = urllib2.Request("http://200.136.72.14:8860/api/v1/general", qrs)
                                    urllib2.urlopen(req)
                                    qrs = "code={0}&page=sci_pdf&access_date={1}".format(pid[0:9], parsed_line['iso_date'])
                                    req = urllib2.Request("http://200.136.72.14:8860/api/v1/general", qrs)
                                    urllib2.urlopen(req)
                                elif script == "sci_home":
                                    qrs = "code=www.scielosp.org&page=sci_home&access_date={0}".format(parsed_line['iso_date'])
                                    req = urllib2.Request("http://200.136.72.14:8860/api/v1/general", qrs)
                                    urllib2.urlopen(req)
                                elif script == "sci_issues":
                                    qrs = "code=www.scielosp.org&page=sci_issues&access_date={0}".format(parsed_line['iso_date'])
                                    req = urllib2.Request("http://200.136.72.14:8860/api/v1/general", qrs)
                                    urllib2.urlopen(req)
                                    qrs = "code={0}&page=sci_issues&access_date={1}".format(pid[0:9], parsed_line['iso_date'])
                                    req = urllib2.Request("http://200.136.72.14:8860/api/v1/general", qrs)
                                    urllib2.urlopen(req)
                                elif script == "sci_alphabetic":
                                    qrs = "code=www.scielosp.org&page=sci_alphabetic&access_date={0}".format(parsed_line['iso_date'])
                                    req = urllib2.Request("http://200.136.72.14:8860/api/v1/general", qrs)
                                    urllib2.urlopen(req)
else:
    print "Connection to CouchDB Fail"

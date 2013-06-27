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
            print logfile
            rq = RatchetQueue(limit=100)
            for line in get_file_lines(logfile):
                parsed_line = parse_apache_line(line, acrondict)
                if parsed_line:
                    if parsed_line['access_type'] == "PDF":
                        pdfid = parsed_line['pdf_path']
                        issn = parsed_line['pdf_issn']
                        rq.register_download_access(pdfid, issn, parsed_line['iso_date'])
                    if parsed_line['access_type'] == "HTML":
                        if is_allowed_query(parsed_line['query_string'], allowed_issns):
                            script = parsed_line['query_string']['script'][0]
                            pid = parsed_line['query_string']['pid'][0].upper().replace('S','')
                            if script == "sci_serial":
                                rq.register_journal_access(pid, parsed_line['iso_date'])
                            elif script == "sci_abstract":
                                rq.register_abstract_access(pid, parsed_line['iso_date'])
                            elif script == "sci_issuetoc":
                                rq.register_toc_access(pid, parsed_line['iso_date'])
                            elif script == "sci_arttext":
                                rq.register_article_access(pid, parsed_line['iso_date'])
                            elif script == "sci_pdf":
                                rq.register_pdf_access(pid, parsed_line['iso_date'])
                            elif script == "sci_home":
                                rq.register_home_access(pid, parsed_line['iso_date'])
                            elif script == "sci_issues":
                                rq.register_issues_access(pid, parsed_line['iso_date'])
                            elif script == "sci_alphabetic":
                                rq.register_alpha_access(pid, parsed_line['iso_date'])
else:
    print "Connection to CouchDB Fail"

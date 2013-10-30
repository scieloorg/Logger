#!/usr/bin/env python
import argparse

from tools import *
from ratchet import *
from logaccess_config import *
from accesschecker import AccessChecker

def main(*args, **xargs):
    ac = AccessChecker(xargs['collection'])
    proc_coll = get_proc_collection()
    proc_robots_coll = get_proc_robots_collection()

    if xargs['ttl']:
        proc_ttl_coll = get_proc_ttl_collection()
    else:
        proc_ttl_coll = None

    for logdir in get_logdirs():
        print "listing log files at: " + logdir
        rq = RatchetQueue(limit=100)
        for logfile in get_files_in_logdir(logdir):

            if log_was_processed(proc_coll, logfile):
                continue
            else:
                print "processing: {0}".format(logfile)
                reg_logfile(proc_coll, logfile)

            for raw_line in get_file_lines(logfile):
                parsed_line = ac.parse_access(raw_line)

                if parsed_line:

                    if parsed_line['access_type'] == "PDF":
                        pdfid = parsed_line['pdf_path']
                        issn = parsed_line['pdf_issn']
                        register_pdf_download_accesses(rq, issn, pdfid, parsed_line['iso_date'], parsed_line['ip'], ttl_coll=proc_ttl_coll)

                    if parsed_line['access_type'] == "HTML":
                        if is_allowed_query(parsed_line['query_string'], ac.allowed_issns):
                            script = parsed_line['query_string']['script'][0]
                            pid = parsed_line['query_string']['pid'][0].upper().replace('S', '')
                            register_html_accesses(rq, script, pid, parsed_line['iso_date'], parsed_line['ip'], ttl_coll=proc_ttl_coll)

            rq.send()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Run the processing to read the access log files and register accesses into Ratchet")
    parser.add_argument('--ttl', default=None, help='Indicates if the processing will use a lock database to control the acccesses according to Counter Project')
    parser.add_argument('--collection', default=None, help='Three letters collection id')
    args = parser.parse_args()

    main(ttl=args.ttl, collection=args.collection)




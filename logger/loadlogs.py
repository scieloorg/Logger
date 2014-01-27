#!/usr/bin/env python
import argparse

from tools import *
from ratchet import *
from logaccess_config import *
from accesschecker import AccessChecker, TimedSet, checkdatelock


def main(*args, **xargs):
    ts = TimedSet(expired=checkdatelock)
    ac = AccessChecker(xargs['collection'])
    proc_coll = get_proc_collection()
    proc_robots_coll = get_proc_robots_collection()

    rq = RatchetQueue(limit=100)
    for logfile in get_files_in_logdir(LOG_DIR):

        if log_was_processed(proc_coll, logfile):
            continue

        print "processing: {0}".format(logfile)
        reg_logfile(proc_coll, logfile)

        for raw_line in get_file_lines(logfile):
            parsed_line = ac.parsed_access(raw_line)

            if not parsed_line:
                continue

            locktime = 10
            if parsed_line['access_type'] == "PDF":
                locktime = 30

            if xargs['ttl']:
                try:
                    lockid = parsed_line['code']+parsed_line['script']
                    ts.add(lockid,
                           parsed_line['iso_datetime'], locktime)
                except ValueError:
                    continue

            if parsed_line['access_type'] == "PDF":
                pdfid = parsed_line['pdf_path']
                issn = parsed_line['pdf_issn']
                register_pdf_download_accesses(rq,
                                               issn,
                                               pdfid,
                                               parsed_line['iso_date'],
                                               parsed_line['ip'])

            if parsed_line['access_type'] == "HTML":
                script = parsed_line['query_string']['script']
                pid = parsed_line['query_string']['pid']
                register_html_accesses(rq,
                                       script,
                                       pid,
                                       parsed_line['iso_date'],
                                       parsed_line['ip'])

        rq.send()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Run the processing to read the access log files and register accesses into Ratchet")
    parser.add_argument('-t',
                        '--ttl',
                        action='store_true',
                        default=False,
                        help='Indicates if the processing will use a lock controller to control the acccesses according to Counter Project')
    parser.add_argument('-c',
                        '--collection',
                        default=None,
                        help='Three letters collection id')
    args = parser.parse_args()

    main(ttl=bool(args.ttl), collection=str(args.collection))

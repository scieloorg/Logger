from logaccess_config import *

import os
import re
import sys
import json
import urllib2
from datetime import date, datetime
import apachelog
import urlparse
from pymongo import Connection


def get_proc_collection():
    """
    The proc collection is a mongodb database that keeps the name of each processed file, to avoid
    processing these files again.
    """
    conn = Connection(LOGGER_DATABASE_DOMAIN, LOGGER_DATABASE_PORT)
    db = conn['proc_files']
    coll = db[LOGGER_DATABASE_COLLECTION]
    coll.ensure_index('file_name')

    return coll

def get_proc_ttl_collection():
    """
    The ttl collection is a mongodb database that keeps an ID with a 10 seconds time to leave
    record for each url + ip address.
    """
    conn = Connection(LOGGER_DATABASE_DOMAIN, LOGGER_DATABASE_PORT)
    db = conn['proc_ttl']
    coll = db[LOGGER_DATABASE_COLLECTION]
    coll.ensure_index('code')
    coll.ensure_index('date_html', expireAfterSeconds=COUNTER_HTML_TTL)
    coll.ensure_index('date_pdf', expireAfterSeconds=COUNTER_PDF_TTL)

    return coll

def get_proc_robots_collection():
    """
    The robots collection is a mongodb database that keeps the count of each robots occurences 
    record for each url + ip address.
    """
    conn = Connection(LOGGER_DATABASE_DOMAIN, LOGGER_DATABASE_PORT)
    db = conn['proc_robots']
    coll = db['robots']
    coll.ensure_index('code')

    return coll

def reg_logfile(coll, file_name):
    coll.insert({'file_name': file_name})


def log_was_processed(coll, file_name):

    if coll.find({'file_name': file_name}).count() > 0:
        return True


def get_logdirs():
    for logdir in LOG_DIRS:
        yield logdir


def get_files_in_logdir(logdir):
    logfiles = os.popen('ls ' + logdir + '/*access.log')
    for logfile in logfiles:
        yield logfile


def get_file_lines(logfile):
    filepath = logfile.strip()
    fileloaded = open(filepath, 'r')

    for line in fileloaded:
        yield line

def is_robot(line, proc_robots_coll):
    for robot in COMP_STOP_WORDS:
        if robot.search(line):
            proc_robots_coll.update({'code': robot.pattern}, {'$set': {'code': robot.pattern}, '$inc': {'count': 1}}, True)
            return True

def is_locked(coll, code, doc_type):
    """
    This method check if the documento code + IP address have already accessed the document
    in the last 10 minutes.
    """
    if coll.find_one({'code': code}):
        return True
    else:
        coll.insert({'code': code, 'date_%s' % doc_type: datetime.utcnow()})
        return False

def register_pdf_download_accesses(ratchet_queue, issn, pdfid, date, ip, ttl_coll=None):
    if ttl_coll:
        code = "%s_%s" % (ip, pdfid)
        if is_locked(ttl_coll, code, 'pdf'):
            return None

    ratchet_queue.register_download_access(pdfid, issn, date)

def register_html_accesses(ratchet_queue, script, pid, date, ip, ttl_coll=None):

    if ttl_coll:
        code = "%s_%s_%s" % (ip, script, pid)
        if is_locked(ttl_coll, code, 'html'):
            return None

    if script == "sci_serial":
        ratchet_queue.register_journal_access(pid, date)
    elif script == "sci_abstract":
        ratchet_queue.register_abstract_access(pid, date)
    elif script == "sci_issuetoc":
        ratchet_queue.register_toc_access(pid, date)
    elif script == "sci_arttext":
        ratchet_queue.register_article_access(pid, date)
    elif script == "sci_pdf":
        ratchet_queue.register_pdf_access(pid, date)
    elif script == "sci_home":
        ratchet_queue.register_home_access(pid, date)
    elif script == "sci_issues":
        ratchet_queue.register_issues_access(pid, date)
    elif script == "sci_alphabetic":
        ratchet_queue.register_alpha_access(pid, date)
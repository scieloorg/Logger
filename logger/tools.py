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


def getTitles():
    query_url = COUCHDB_DATABASE + "/" + COUCHDB_TITLE_QUERY
    print query_url
    try:
        query = urllib2.urlopen(query_url)
    except urllib2.URLError:
        return None

    titles = json.loads(query.read())

    title_dict = {}
    for title in titles['rows']:
        title_dict[title['doc']['v68'][0]['_']] = title['doc']['v400'][0]['_']

    return title_dict


def validate_pid(script, pid, allowed_issns):

    if pid[0:9] in allowed_issns:
        if script == u"sci_issuetoc":
            if re.search(REGEX_ISSUE, pid):
                return True
        elif script == u"sci_abstract" or re.search(REGEX_FBPE, pid):
            if re.search(REGEX_ARTICLE, pid):
                return True
        elif script == u"sci_arttext":
            if re.search(REGEX_ARTICLE, pid) or re.search(REGEX_FBPE, pid):
                return True
        elif script == u"sci_pdf":
            if re.search(REGEX_ARTICLE, pid) or re.search(REGEX_FBPE, pid):
                return True
        elif script == u"sci_serial":
            if re.search(REGEX_ISSN, pid):
                return True
        elif script == u"sci_issues":
            if re.search(REGEX_ISSN, pid):
                return True

    return None


def validate_pdf(filepath, acronDict):
    if filepath:
        pdf_spl = filepath.split("/")
        if len(pdf_spl) > 2:
            if pdf_spl[1] == u'pdf':
                if pdf_spl[2] != '':
                    if pdf_spl[2] in acronDict:
                        return True
    return None


def validate_date(dat):
    if len(str(dat)) == 10:
        if int(dat[0:4]) <= int(date.today().year) and \
            (int(dat[5:7]) >= 1 and int(dat[5:7]) <= 12) and \
                (int(dat[8:10]) >= 1 and int(dat[8:10]) <= 31):
            return True

    return None


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


def log_line_triage(line):
    """
    Check if the line contains a PDF directly download pattern or represents an html access
    """
    if "GET" in line and ".pdf" in line:
        return "PDF"

    if "GET" in line and "scielo.php" in line and "script" in line and "pid" in line:
        return "HTML"

    return None


def get_pdf_path(data_r):
    """
        Clean the GET request to bring just the pdf path.
        receive: GET /pdf/bjb/v62n2/10867.pdf HTTP/1.0
        return: /pdf/bjb/v62n2/10867
    """
    pdf_path = None
    find = re.findall('/pdf.*\.pdf', data_r)
    if len(find) == 1:
        pdf_path = find[0][0:-4]
        pdf_path = pdf_path.replace("//", "/")
        pdf_path = pdf_path.replace("%0D/", "")

    if not pdf_path:
        return None

    return pdf_path

def is_robot(line, proc_robots_coll):
    for robot in COMP_STOP_WORDS:
        if robot.search(line):
            proc_robots_coll.update({'code': robot.pattern}, {'$set': {'code': robot.pattern}, '$inc': {'count': 1}}, True)
            return True

def parse_apache_line(raw_line, proc_robots_coll, acrondict=None):
    kind_of_access = log_line_triage(raw_line)
    #Checking if the apache log line seams to be a valid HTML access or PDF donwload.

    if not kind_of_access:
        return None

    p = apachelog.parser(APACHE_LOG_FORMAT)
    try:
        data = p.parse(raw_line)
    except:
        sys.stderr.write(u"Unable to parse %s" % unicode(raw_line, errors='ignore'))
        return None

    line = {}
    line['ip'] = data['%h'].strip()
    line['access_type'] = kind_of_access
    line['day'] = data['%t'][1:3]
    line['year'] = data['%t'][8:12]
    line['month'] = ""
    if data['%t'][4:7].upper() in MONTH_DICT:
        line['month'] = MONTH_DICT[data['%t'][4:7].upper()]

    line['iso_date'] = '{0}-{1}-{2}'.format(line['year'], line['month'], line['day'])

    if not validate_date(line['iso_date']):
        return None

    url = data['%r'].split(' ')[1]
    line['query_string'] = urlparse.parse_qs(urlparse.urlparse(url).query)

    if kind_of_access.upper() == 'PDF':
        line['pdf_path'] = get_pdf_path(data['%r'])
        if validate_pdf(line['pdf_path'], acrondict):
            line['pdf_issn'] = acrondict[line['pdf_path'].split('/')[2]]
        else:
            return None

    if is_robot(raw_line, proc_robots_coll):
        return None

    return line

def is_allowed_query(query_string, allowed_issns):
    """
    Check if the query string have the necessary aguments to represent a valid access.
    The query_string must have the both parameters "pid, script"
    """

    if not 'script' in query_string:
        return None

    if not 'pid' in query_string:
        return None

    script = query_string['script'][0]
    if not script.lower() in ALLOWED_SCRIPTS:  # Validation if the script is allowed
        return None

    pid = query_string['pid'][0].replace('S', '').replace('s', '').strip()
    if not validate_pid(script, pid, allowed_issns):
        return None

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
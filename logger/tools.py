from logaccess_config import *

import os
import re
import sys
import json
import urllib2
from datetime import date
import apachelog
import urlparse


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

    if "GET /scielo.php" in line and "script" in line and "pid" in line:
        return "HTML"

    return None


def get_pdf_path(data_r):
    """
        Clean the GET request to bring just the pdf path.
        receive: GET /pdf/bjb/v62n2/10867.pdf HTTP/1.0
        return: /pdf/bjb/v62n2/10867
    """
    pdf_path = data_r[4:data_r.find('.pdf')]
    pdf_path = pdf_path.replace("//", "/")
    pdf_path = pdf_path.replace("%0D/", "")

    if not pdf_path:
        return None

    return pdf_path


def parse_apache_line(line, acrondict=None):
    kind_of_access = log_line_triage(line)
    #Checking if the apache log line seams to be a valid HTML access or PDF donwload.

    if not kind_of_access:
        return None

    p = apachelog.parser(APACHE_LOG_FORMAT)
    try:
        data = p.parse(line)
    except:
        sys.stderr.write(u"Unable to parse %s" % line)
        return None

    line = {}
    line['access_type'] = kind_of_access
    line['day'] = data['%t'][1:3]
    line['year'] = data['%t'][8:12]
    line['month'] = ""
    if data['%t'][4:7].upper() in MONTH_DICT:
        line['month'] = MONTH_DICT[data['%t'][4:7].upper()]

    line['iso_date'] = '{0}-{1}-{2}'.format(line['year'], line['month'], line['day'])

    if not validate_date(line['iso_date']):
        return None

    for stopword in STOP_WORDS:
        if stopword in line:
            return None

    url = data['%r'].split(' ')[1]
    line['query_string'] = urlparse.parse_qs(urlparse.urlparse(url).query)

    if kind_of_access.upper() == 'PDF':
        line['pdf_path'] = get_pdf_path(data['%r'])
        if validate_pdf(line['pdf_path'], acrondict):
            line['pdf_issn'] = acrondict[line['pdf_path'].split('/')[2]]
        else:
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

#!/usr/bin/env python
# -*- encoding: utf-8 -*-

LOGS_DIR = '../data/logs'
APACHE_LOG_FORMAT= r'%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"'
MONTH_DICT = {
    'JAN':'01',
    'FEB':'02',
    'MAR':'03',
    'APR':'04',
    'MAY':'05',
    'JUN':'06',
    'JUL':'07',
    'AUG':'08',
    'SEP':'09',
    'OCT':'10',
    'NOV':'11',
    'DEC':'12',
}
ALLOWED_SCRIPTS = [
    'SCI_ARTTEXT',
    'SCI_SERIAL',
    'SCI_ISSUES',
    'SCI_HOME',
    'SCI_ABSTRACT',
    'SCI_ISSUETOC',
    'SCI_ALPHABETIC',
    'SCI_PDF'
]

ALLOWED_LANGUAGES = ['PT','ES','EN','IT','FR','GR']

REGEX_ISSN    = "^[0-9]{4}-[0-9]{3}[0-9xX]$"
REGEX_ISSUE   = "^[0-9]{4}-[0-9]{3}[0-9xX][0-2][0-9]{3}[0-9]{4}$"
REGEX_ARTICLE = "^[0-9]{4}-[0-9]{3}[0-9xX][0-2][0-9]{3}[0-9]{4}[0-9]{5}$"
REGEX_FBPE    = "^[0-9]{4}-[0-9]{3}[0-9xX]\([0-9]{2}\)[0-9]{8}$"

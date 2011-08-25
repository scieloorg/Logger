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
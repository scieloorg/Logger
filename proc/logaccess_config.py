#!/usr/bin/env python
# -*- encoding: utf-8 -*-

MONGODB_DOMAIN="localhost"
MONGODB_PORT=27017
COLLECTION_CODE="bra"
COLLECTION_DOMAIN="www.scielo.br"

LOG_DIRS = ['../data/logs/scielo21',
            '../data/logs/scielo31',
            '../data/logs/scielo32',
            '../data/logs/scielo33',
            '../data/logs/scielo34']

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
    'sci_arttext',
    'sci_serial',
    'sci_issues',
    'sci_home',
    'sci_abstract',
    'sci_issuetoc',
    'sci_alphabetic',
    'sci_pdf'
]

ALLOWED_LANGUAGES = ['PT','ES','EN','IT','FR','DE','AF','AR']

REGEX_ISSN    = "^[0-9]{4}-[0-9]{3}[0-9xX]$"
REGEX_ISSUE   = "^[0-9]{4}-[0-9]{3}[0-9xX][0-2][0-9]{3}[0-9]{4}$"
REGEX_ARTICLE = "^[0-9]{4}-[0-9]{3}[0-9xX][0-2][0-9]{3}[0-9]{4}[0-9]{5}$"
REGEX_FBPE    = "^[0-9]{4}-[0-9]{3}[0-9xX]\([0-9]{2}\)[0-9]{8}$"

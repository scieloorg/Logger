# -*- encoding: utf-8 -*-

import logaccess_config

def listpatterns():
    """
    Recover the list of log patterns configured at logaccess_config.py 
    """

    pattern_types = (i for i in logaccess_config.ALLOWED_PATTERNS)

    return pattern_types

def getitem(code):
    """
    Recover an Item statistics acording to the item code.
    """

    return True

def getitemsbypattern(pattern):
    """
    Recover an list of item according to a pattern id retrieved by listpatterns method
    """

    return True
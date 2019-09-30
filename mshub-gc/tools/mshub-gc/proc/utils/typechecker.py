"""
Check various data types between python 2 and 3 versions

"""

import sys

PY2 = sys.version_info[0] == 2

def is_string(var):
    """Portable function to answer this question."""
    if PY2:
        return isinstance(var, basestring)  
    else:
        return isinstance(var, str)  
        
def is_number(var):
    """Portable function to answer this question."""
    if PY2:
        return isinstance(var, (int,long,float))  
    else:
        return isinstance(var, (int,float))
        
def iteritem(var):
    """Portable function to answer this question."""
    if PY2:
         return var.iteritems()  
    else:
        return iter(var.items())
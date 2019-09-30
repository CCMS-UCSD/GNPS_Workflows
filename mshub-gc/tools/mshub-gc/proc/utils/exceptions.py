# -*- coding: utf-8 -*-
"""
Created on Tue May 09 19:02:29 2017

@author: ilaponog
"""

class HDF5UtilsGroupError(Exception):
    pass

class UnSupportedObject(Exception):
    pass

class EmptyWorkGroup(Exception):
    pass

class UnknownClassID(Exception):
    pass

class ClassNotFound(Exception):
    pass

class NoNewMethodforClass(Exception):
    pass

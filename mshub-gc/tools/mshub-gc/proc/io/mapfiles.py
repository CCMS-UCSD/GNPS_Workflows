# -*- coding: utf-8 -*-
"""
************
File Mapping
************

Maps and stores the paths to all identified files of a user defined type
in the specified directory 

"""
import os

# specifies path to the folder with MSI data 
class FilesInfo(object):
    """**The container for imported data folder and file types**
        
         
    Attributes:
        
            
        folderpath: the path to a folder with indidivual MSI data files. All files in the sub-folders
                        of the specified path will be recursively and automatically mapped. The current
                        working directory is set by default. 
                        
                                            
        fileext: the type of imported MS data files
            
         
    """
    def __init__(self, folderpath=os.getcwd(),fileext = ".cdf"):
        self.folderpath = folderpath
        self.fileext    = fileext
	
    def set_folderpath(self,folderpath):
        """Sets the specified data folder path """
        self.folderpath = folderpath
        
    def set_fileext(self,fileext):
        """Sets the file extension type """

        self.fileext = fileext
                
    def map_files(self):
        """Maps and stores all paths to all identified files of the speicifed type """
        self.filepaths = [os.path.join(dp, f) for dp, dn, filenames in os.walk(self.folderpath) for f in filenames if (os.path.splitext(f)[1]).lower() == self.fileext]
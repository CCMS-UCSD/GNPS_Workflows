# -*- coding: utf-8 -*-
"""
*******************************************************************
Workflow assistant module for chromatography-mass spectrometry data
*******************************************************************

The module contains a set of methods shared across all workflow modules

"""
import os
import proc.io.manageh5db as mh5
import time
from proc.utils.typechecker import is_string
import traceback;

class H5BaseMSIWorkflow(object):
    
    """    
    **The container containing the choice of methods and parameters common across all pre-processing modules**
         
    Attributes:
            
                  
        method:  Method for specific pre-processing modules
             
        params:  Parameters for specific pre-processing modules
        
  
    """    
    def __init__(self):

        self.description = ''
        self.do = 'yes'
        self.method = ''
        self.params = ''
        self.index  = -1
    
    def load_procobj(self, dbfile, pathinh5):
        
        """    
        
        Overwrites the current preprocessing module parameters with the ones loaded from specified hdf5 database file
        
        Args:
            
            dbfile: the path to the database file
        
        
        """
        if H5BaseMSIWorkflow.checkdbfile(dbfile)==1:
            ProcObj = mh5.load_preproc_obj(dbfile,self.description,pathinh5)
            if not ProcObj:
                self.istrain = 1 
                print('%s database file doesn''t contain any parameters for %s' %(str(dbfile),str(self.description)))
                pass
            else:
                if isinstance(ProcObj,dict):
                    for i_name in ProcObj.keys():
                        setattr(self,i_name,ProcObj[i_name])
                else:
                    procobj_attr_names = [a for a in dir(ProcObj) if not a.startswith('__')]
                    for i_name in procobj_attr_names:
                        setattr(self,i_name,getattr(ProcObj,i_name))
                    
                print('The %s from the pre-processing workflow has been uploaded from %s' %(str(self.description),str(dbfile)))
                self.istrain = 0
        else:
            self.istrain = 0
            
    def save_procobj(self,dbfile,pathinh5):
        """    
        
        Saves the current preprocessing module parameters into hdf5 database file
        
        Args:
            
            dbfile: the path to the database file
        
        """  
        
        if H5BaseMSIWorkflow.checkdbfile(dbfile)==1:
            mh5.save_preproc_obj(dbfile,self,pathinh5)
          
    def save_preproc2matlab(self,dbfile,index):
        """    
        
        Saves the current preprocessing module parameters into hdf5 database file
        
        Args:
            
            dbfile: the path to the database file
        
        
        """  
        try: 
            objattrs = vars(self)
            mh5.save_preproc2matlab(dbfile,objattrs['do'],index, 
                                    objattrs['description'], objattrs['method'], objattrs['params'])
        except Exception as inst:
            print(inst)
            traceback.print_exc()
        
    @staticmethod    
    def checkdbfile(dbfile):
        """    
        
        Checks if the hdf5 database file exists
        
        Args:
            
            dbfile: the path to the database file
        
        
        """  
        if os.path.isfile(dbfile):
            isdbfile = 1
        else:
            if not dbfile:
                print('The database file name has not been provided ...')
            else:
                print('%s database file is not found' %str(dbfile))                
            isdbfile = 0
            
        return isdbfile
    
    @staticmethod           
    def get_dataset_names(dbfile):
        """    
        
        Exctracts data-set names from the hdf5 database file exists
        
        Args:
            
            dbfile: the path to the database file
        
         """    
        isdbfile = H5BaseMSIWorkflow.checkdbfile(dbfile)
        if isdbfile==1:
            datasets = mh5.get_dataset_names(dbfile,dataset_names=[])
            if not datasets:
                print('%s database file doesn''t contain any MSI datasets'%str(dbfile))
        else:
            datasets = []        
        return datasets
    
    @staticmethod           
    def get_traindata_names(dbfile,istrain):
        """    
        
        Exctracts data-set names from the hdf5 database file exists
        
        Args:
            
            dbfile: the path to the database file
        
         """    
        isdbfile = H5BaseMSIWorkflow.checkdbfile(dbfile)
        if isdbfile==1:
            datasets = mh5.get_traindata_names(dbfile,'', [],istrain)
            if not datasets:
                print('%s database file doesn''t contain any MSI datasets'%str(dbfile))
        else:
            datasets = []        
        return datasets
    
    @staticmethod           
    def h5pathfinder(datapath):
        """    
        
        Finds a suitable path in the database file for storage of workflow metadata
                
        """    
        if is_string(datapath):
            splitpath = datapath.split('/')
        else:
            h5inpath =''
            return h5inpath
        
        nsplits  = len(splitpath)
        h5inpath = ''
        if nsplits == 2:
            if splitpath[0]!='':
                h5inpath = splitpath[0] + '/'
        elif nsplits > 2:
            for i in range(nsplits-1):
                h5inpath = h5inpath + splitpath[i] +'/'
        
        return h5inpath    
    
    @staticmethod     
    def correct_h5path(pathid):
        """    
        
        Corrects user-defined path in h5 file for the workflow consistency
                
        """ 
        
        if not pathid:
            pathid = '/proc'
        
        if pathid[0]!='/':
            pathid = '/' + pathid
            
        if pathid[-1]!='/':
           pathid = pathid + '/'
    
        return pathid
    
    @staticmethod     
    def save_proc_meta(dbfilepath,h5writepath,h5readpath):
        if h5writepath!=h5readpath:
            mzrange = mh5.load_dataset(dbfilepath, h5readpath + 'mzrange')
            rtrange = mh5.load_dataset(dbfilepath, h5readpath + 'rtrange') 
            cmz     = mh5.load_dataset(dbfilepath, h5readpath + 'cmz')
            crt     = mh5.load_dataset(dbfilepath, h5readpath + 'crt')
            sizesp  = mh5.load_dataset(dbfilepath, h5readpath + 'sizesp')
            
            mh5.save_dataset(dbfilepath, h5writepath + 'mzrange',data=mzrange)
            mh5.save_dataset(dbfilepath, h5writepath + 'rtrange',data=rtrange) 
            mh5.save_dataset(dbfilepath, h5writepath + 'cmz',data=cmz,compression_opts = 5)
            mh5.save_dataset(dbfilepath, h5writepath + 'crt',data=crt,compression_opts = 5)
            mh5.save_dataset(dbfilepath, h5writepath + 'sizesp',data=sizesp)
    
    
    @staticmethod
    def generate_h5filename(dbrawfile,dbfile=''):
        """    
        
        Generates the hdf5 database file name for processing data and parameters storage
        
        Args:
            
            dbfile: the path to the database file
        
         """    
        dbdir = os.path.dirname(dbfile)
        if not (os.path.isdir(dbdir)):
            dbdir = os.path.dirname(dbrawfile)
        
        dbfile = os.path.basename(dbfile)
        if not os.path.basename(dbfile):
            dbfile = "pyproc_data__" + time.strftime("%H%M_%d_%m_%Y")
        else: 
            dbfile = os.path.splitext(dbfile)[0]
        
        dbfile = dbdir + os.path.sep + dbfile + ".h5"
        print('Setting database file for processed data to:%s ' %str(dbfile))
        return dbfile
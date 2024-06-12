'''
import unittest library
'''
import os
import random
import sys
import unittest


'''
import openms_workflow scripts
'''
sys.path.append('./tools/openms/scripts')
import openms_workflow as wrkflw
from openms_workflow import LogType


'''
test suite for openms_workflow
'''
class TestOpenMSWorkflow(unittest.TestCase):  
  openms_testfiles = './test/testfiles'
  mapaligner_path = openms_testfiles+'/mapalignerposeclustering'

  def get_testpath(self, modulename):
    '''
    generate modulename test
    '''
    pathname = self.openms_testfiles + "/" + modulename
    if os.path.exists(pathname):
      return pathname
    else:
      raise Exception


  def test_parsefolder_invalidpath(self):
    '''
    test parsefolder with an invalid path and make sure the list is empty
    '''
    test_dir = list(wrkflw.parsefolder(self.mapaligner_path+"invalidpath"))

    self.assertEquals(len(test_dir), 0)


  def test_parsefolder_validpath(self):
    '''
    test parsefolder without blacklisting or whitelisting any files
    '''
    mapaligner_path = self.get_testpath("mapalignerposeclustering")

    test_dir = [x[0] for x in wrkflw.parsefolder(mapaligner_path)] 
    exp_dir = [mapaligner_path+"/"+x for x in sorted(os.listdir(mapaligner_path))]
    
    self.assertEquals(test_dir, exp_dir)


  def test_parsefolder_count(self):
    '''
    test that file count increments
    '''
    mapaligner_path = self.get_testpath("mapalignerposeclustering")
    
    test_dir = [int(x[1]) for x in wrkflw.parsefolder(mapaligner_path, blacklist=['logfile'])]
    self.assertEquals(test_dir, range(0,len(test_dir)))

     
  def test_parsefolder_blacklist_1(self):
    '''
    test parsefolder while blacklisting a single file
    '''        
    mapaligner_path = self.get_testpath("mapalignerposeclustering")

    for file in sorted(os.listdir(mapaligner_path)):
      test = [x[0] for x in wrkflw.parsefolder(mapaligner_path, blacklist=[file])] 
      
      exp = [mapaligner_path+'/'+x for x in sorted(os.listdir(mapaligner_path))]
      exp.remove(mapaligner_path+'/'+file)
      
      self.assertEquals(test, exp)


  def test_parsefolder_blacklist_2(self):
    '''
    test parsefolder while blacklisting multiple files
    '''
    mapaligner_path = self.get_testpath("mapalignerposeclustering")

    for i in range(5):
      # choose random files to blacklist from the directory
      blacklist_files = os.listdir(mapaligner_path)[:i]
      random.shuffle(blacklist_files)
      
      # parse directory while blacklisting specified files
      dir_files = [f[0] for f in wrkflw.parsefolder(mapaligner_path, blacklist=blacklist_files)]

      # check that none of the blacklisted files are in the files
      self.assertEquals(all(f not in dir_files for f in blacklist_files), True)



  def test_postvalidation_singlelog(self):
    '''
    test postvalidation with:
      - single output file
      - single log file
    '''
    self.assertEquals(
      wrkflw.postvalidation("gnpsexport", 
        inpath=self.openms_testfiles+'/filefilter', 
        outpath=self.openms_testfiles+'/gnpsexport', 
        logtype=LogType.SINGLE,
        output_per_job=1),
      True
    )      

  
  def test_postvalidation_multlog(self):
    '''
    test postvalidation with:
      - multiple output files
      - multiple log files 
    '''
    self.assertEquals(
      wrkflw.postvalidation("mapalignerposeclustering-2",
        inpath=self.openms_testfiles+"/idmapper",
        outpath=self.openms_testfiles+"/mapalignerposeclustering-2",
        logtype=LogType.MULTIPLE,
        output_per_job=1
      ),
      True
    )

def test_postvalidation_multjob_singlelog(self):
  '''
  test postvalidation with:
    - multiple jobs
    - single log
  '''
  self.assertEquals(
    wrkflw.postvalidation(
      inpath=self.openms_testfiles+"/idmapper",
      outpath=self.openms_testfiles+"/mapalignerposeclustering",
      logtype=LogType.SINGLE,
      output_per_jobs=1
    ),
    True
  )
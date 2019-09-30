"""
************************************************************
Chromatography - mass spectrometry data import module
************************************************************

The module deposits (GC-MS or LC-MS) data from netCDF data files
to hdf5 based database file for subsequent pre-processing aimed to account
for various bioanalytical complexities associated with GC-MS/LC-MS technologies

run python importmsdata.py --help to get info about parameters of the script

"""

#===========================Import section=================================

#Importing standard and external modules
import os
import time
import h5py
import numpy as np
import traceback
import sys



#If run independently - check system endianness and add path to local modules
if __name__ == "__main__":
    if sys.byteorder!='little':
        print('Only little endian machines currently supported! bye bye ....');
        quit();
    module_path = os.path.abspath('%s/../..'%os.path.dirname(os.path.realpath(__file__)));
    sys.path.insert(0, module_path)

#Import local/internal modules
from proc.io import manageh5db as m5db

import proc.io.mapfiles as mf
from proc.procconfig import ImportSet_options
from proc.utils.cmdline import OptionsHolder
from proc.utils.timing import tic, toc;
from proc.utils.printlog import printlog, start_log, stop_log;



#==========================================================================
#From here the main code starts

def main(datapath, filetype, filereadinfo, dbname=''):

    """
    Reads chromatography-mass spectrometry datasets from individual files (e.g. from NETCDF files)
    and deposit them into hdf5 database file for downstream preprocessing

    See module references:

     Args:

         configuration: instance of OptionsHolder preset with ImportSet_options from procconfig containing:

            datafolder: Path to a folder with indidivual MSI data files. All files in the sub-folders
                        of the specified path will be recursively and automatically mapped. The current
                        working directory is set by default.

            filetype: Read file type. NETCDF by default


            filereadinfo: Parameter set for the read file type.
                            By default for netcdf: ``{'fileext': 'cdf', 'massid': 'mass_values',
                                                      'specid': 'intensity_values', 'scanid':
                                                    'scan_acquisition_time'}``

            dbname:   Name of the newly created database file, set to "msdata__time_stamp.h5" by default
    """

    #rt conversion to seconds

    #print(filereadinfo)
    if filereadinfo['timeunits'] == 'min':
        time_mult = 60.0;
    else:
        time_mult = 1.0;

    # map files from local directory
    if os.path.isdir(datapath) == False:
        datafolder = os.getcwd()

    f_info = mf.FilesInfo(folderpath=datapath, fileext=filereadinfo['fileext'])
    f_info.map_files()
    nfiles = len(f_info.filepaths)
    if nfiles>0:
        #printlog("\n\n***********Starting*************\n")
        if nfiles==1:
            printlog(str(nfiles) + " " + filereadinfo['fileext'] + " file found " + "in " + datapath)
        else:
            printlog(str(nfiles) + " " + filereadinfo['fileext'] + " files found " + "in " + datapath)

        if filetype.lower()=='netcdf':
            
            h5_info = NetCDFImport(filereadinfo, dbname, datapath, time_mult)
            h5_info.netcdf_reader(f_info.filepaths)
        elif filetype.lower()=='mzml':
            
            h5_info = mzMLImport(filereadinfo, dbname, datapath, time_mult)
            h5_info.mzml_reader(f_info.filepaths)
        elif filetype.lower()=="mzxml":
            #
            h5Info = mzXMLImport(filereadinfo, dbname, datapath, time_mult)
            #print(f_info.filepaths)
            h5Info.mzxml_reader(f_info.filepaths)
    else:
        printlog(datafolder
        + ": Failed to find any data files with the extension of "+
        filereadinfo['fileext'])


class NetCDFImport(object):

    """
    **The container containing the choice of methods and parameters for GC-MS NETCDF data import**

    Attributes:

        dbpath: the path of hdf5 database file  The  path to the user specified data directory is set by default.

        dbname: the name of hdf5 database file for GC-MS data deposition, by default ``msdata__timestamp.h5``

        __mass_string: the path for reading m/z values from netcdf files ('mass_values', by default)

        __intensity_string: the path for reading intensity values from netcdf files ('intensity_values', by default)

        __time_string: the path for reading time values from netcdf files ('scan_acquisition_time', by default)
    """

    def __init__(self, filereadinfo, dbname='', dbpath='', time_mult = 1.0):
        """
        Class parameter initialization
        """

        self.dbname = ''
        self.dbpath = ''
        self.time_mult = time_mult

        # the keys used to retrieve certain data from the NetCDF file
        self.__mass_string = filereadinfo['massid']
        self.__intensity_string = filereadinfo['specid']
        self.__scan_string = filereadinfo['scanid']
        self.__time_string = filereadinfo['timeid']

        if dbname!='':
            self.dbpath = os.path.dirname(dbname)
            self.dbname = os.path.basename(dbname)

        if self.dbpath == '':
            if os.path.isdir(dbpath):
                self.dbpath=dbpath
            else:
                self.dbpath=os.getcwd()

        try:
            if not os.path.isdir(self.dbpath):
                os.makedirs(self.dbpath);
        except:
            self.dbpath=os.getcwd()

        if self.dbname == '':
            printlog('Output database file name not provided. Setting output file name to:');
            self.dbname =  "msdata__" + time.strftime("%H%M_%d_%m_%Y") +".h5"
            printlog(self.dbname)
        else:
            self.dbname = os.path.splitext(self.dbname)[0] + '.h5'


    def netcdf_reader(self,filelist):
        """
        Performs reading chromatography-mass spectrometry data from NETCDF files

        Args:

            filelist: the list of files

        """
        from netCDF4 import Dataset
        hf      = h5py.File(os.path.join(self.dbpath, self.dbname), 'w')
        minmass = np.inf
        maxmass = 0.
        minrt   = np.inf
        maxrt   = 0.
        resrt   = -1.

        printlog(" \nReading netCDF files from '%s'...\n" % (self.dbpath))
        # loop through the files
        fileindex = 0
        for filepath in filelist:
            fileindex = fileindex + 1
            
            try:
                file = Dataset(filepath)
            except Exception as inst:
                printlog("%s: Cannot open file" % filepath)
                printlog(inst)
                traceback.print_exc()
                continue

            try:
                mass_values      = np.array(file.variables[self.__mass_string][:])
                intensity_values = np.array(file.variables[self.__intensity_string][:])
                time_values = np.array(file.variables[self.__time_string][:])
                scan_values = np.array(file.variables[self.__scan_string][:])
                
                minmass = np.min([minmass,np.min(mass_values)])
                maxmass = np.max([maxmass,np.max(mass_values)])

                if not len(mass_values) == len(intensity_values):
                    printlog("The length of mass_list is not equal to the length of intensity_list. Data not deposited!... !")
                    continue

                if not len(time_values) == len(scan_values):
                    printlog("The length of scan_aquisition_time is not equal to the length of scan_index. Data not deposited!... !")
                    continue

                #removing empty scans
                dd = np.diff(scan_values) != 0;
                dd = np.append(dd, True);
                ddi = np.arange(scan_values.shape[0], dtype = np.int64)[dd];
                time_values = time_values[ddi];
                scan_values = scan_values[ddi];

                #if np.median(np.diff(mass_values))<0:
                    
                if np.median(np.diff(time_values))<0:
                    printlog('Decreasing scan time values detected! Data not deposited!...!')
                
                minrt = np.min([minrt, np.min(time_values)])
                maxrt = np.max([maxrt, np.max(time_values)])

                if resrt==-1:
                    resrt = np.median(np.diff(time_values))
                else:
                    resrt = 0.5*(np.median(np.diff(time_values))+resrt)
                
                scan_end_values = np.append(scan_values[1:]-1, mass_values.shape[0]-1);
                
                scan_indcs = np.vstack([scan_values, scan_end_values])                
                
                dpath   = 'raw/' + os.path.splitext(os.path.basename(filepath))[0]
                try:
                    ginfo    = hf.create_group(dpath)
                    try:
                        m5db.save_dataset(ginfo,'mz',   data = mass_values, compression_opts = 5)
                        m5db.save_dataset(ginfo,'sp',   data = intensity_values, compression_opts = 5)
                        m5db.save_dataset(ginfo,'time', data = (time_values * self.time_mult) )
                        m5db.save_dataset(ginfo,'scan', data = scan_indcs)

                        # chunks=(nRows, nCols, 1))
                        printlog('%s. %s: Successfully deposited -> %s' %(fileindex, os.path.basename(filepath), self.dbname))
                        ginfo.attrs['is_raw'] = True;
                        ginfo.attrs['is_OK'] = True;
                        ginfo.attrs['is_processed'] = False;
                        ginfo.attrs['is_continuous'] = True;
                        ginfo.attrs['is_sample_dataset'] = True;
                        #TODO: properly treat test and training data
                        #ginfo.attrs['is_training'] = True;


                    except Exception as inst:
                        printlog('%s. %s: Failed to deposit' %(fileindex, os.path.basename(filepath)))
                        printlog(inst)
                        traceback.print_exc()

                except Exception as inst:
                    printlog('%s. %s: All files must have unique names: Failed to create a dataset in -> %s' %(fileindex, os.path.basename(filepath), self.dbname))
                    printlog(inst)
                    traceback.print_exc()                
                
                
                
                '''
                

                # calculate the number of scans
                scanidx = np.append(scanidx,True)
                nscans  = np.sum(scanidx)
                scanidx = np.where(scanidx==True)
                scanidx = scanidx[0][np.arange(0,nscans)]

                # pre-allocate arrays
                scan_start = np.array([]).astype(int)
                scan_end = np.array([]).astype(int)

                # arrange data for hdf5 database file storage
                istart  = 0
                for iend in scanidx:
                    imass_values = mass_values[np.arange(istart,iend+1)]
                    iintensity_values = intensity_values[np.arange(istart,iend+1)]
                    if len(imass_values)>0:
                        if descend==1:
                            mass_values[np.arange(istart,iend+1)] = imass_values[::-1]
                            intensity_values[np.arange(istart,iend+1)] = iintensity_values[::-1]
                        scan_start = np.append(scan_start,istart)
                        scan_end   = np.append(scan_end,iend)
                    istart = iend+1

                # arrange data for hdf5 database file storage
                scan_indlist = np.vstack((scan_start,scan_end))
                time_list    = np.array(file.variables[self.__time_string][:])
                if np.median(np.diff(time_list))<0:
                    time_list    = time_list[::-1]

                # sanity check
                if not len(time_list) == len(scan_start):
                    printlog("The number of time points (%d) does not equal the number of scans (%d). Data not deposited!"%(len(time_list), len(scan_start)))
                    continue
                else:
                    # deposit data into hdf5 database file
                    dpath   = 'raw/' + os.path.splitext(os.path.basename(filepath))[0]
                    try:
                        ginfo    = hf.create_group(dpath)
                        try:
                            m5db.save_dataset(ginfo,'mz', data = mass_values,compression_opts = 5)
                            m5db.save_dataset(ginfo,'sp', data = intensity_values, compression_opts = 5)
                            m5db.save_dataset(ginfo,'time',data = (time_list * self.time_mult) )
                            m5db.save_dataset(ginfo,'scan',data = scan_indlist)

                           # chunks=(nRows, nCols, 1))
                            printlog('%s. %s: Successfully deposited -> %s' %(fileindex, os.path.basename(filepath), self.dbname))
                            ginfo.attrs['is_raw'] = True;
                            ginfo.attrs['is_OK'] = True;
                            ginfo.attrs['is_processed'] = False;
                            ginfo.attrs['is_continuous'] = True;
                            ginfo.attrs['is_sample_dataset'] = True;
                            #TODO: properly treat test and training data
                            #ginfo.attrs['is_training'] = True;


                        except Exception as inst:
                            printlog('%s. %s: Failed to deposit' %(fileindex, os.path.basename(filepath)))
                            printlog(inst)
                            traceback.print_exc()

                    except Exception as inst:
                        printlog('%s. %s: All files must have unique names: Failed to create a dataset in -> %s' %(fileindex, os.path.basename(filepath), self.dbname))
                        printlog(inst)
                        traceback.print_exc()
                '''
            except Exception as inst:
                printlog('%s. %s: Failed to read in data' %(fileindex, os.path.basename(filepath)))
                printlog(inst)
                traceback.print_exc()

        m5db.save_dataset(hf,'raw/cmzrange',data=[np.floor(minmass),np.ceil(maxmass)])
        m5db.save_dataset(hf,'raw/crtrange',data=[np.floor(minrt * self.time_mult), resrt * self.time_mult, np.ceil(maxrt * self.time_mult)])

        printlog('Minimal mz: %s'%np.floor(minmass))
        printlog('Maximal mz: %s'%np.ceil(maxmass))
        printlog('Minimal rt (sec): %s'%np.floor(minrt * self.time_mult))
        printlog('Maximal rt (sec): %s'%np.ceil(maxrt * self.time_mult))


class mzMLImport(object):
    """
    **The container containing the choice of methods and parameters for GC-MS NETCDF data import**

    Attributes:

        dbpath: the path of hdf5 database file  The  path to the user specified data directory is set by default.

        dbname: the name of hdf5 database file for GC-MS data deposition, by default ``msdata__timestamp.h5``

        __mass_string: the path for reading m/z values from netcdf files ('mass_values', by default)

        __intensity_string: the path for reading intensity values from netcdf files ('intensity_values', by default)

        __time_string: the path for reading time values from netcdf files ('scan_acquisition_time', by default)
    """

    def __init__(self, filereadinfo, dbname='', dbpath='', time_mult = 1.0):
        """
        Class parameter initialization
        """

        self.dbname = ''
        self.dbpath = ''
        self.time_mult = time_mult

        if dbname!='':
            self.dbpath = os.path.dirname(dbname)
            self.dbname = os.path.basename(dbname)

        if self.dbpath == '':
            if os.path.isdir(dbpath):
                self.dbpath=dbpath
            else:
                self.dbpath=os.getcwd()

        try:
            if not os.path.isdir(self.dbpath):
                os.makedirs(self.dbpath);
        except:
            self.dbpath=os.getcwd()

        if self.dbname == '':
            printlog('Output database file name not provided. Setting output file name to:');
            self.dbname =  "msdata__" + time.strftime("%H%M_%d_%m_%Y") +".h5"
            printlog(self.dbname)
        else:
            self.dbname = os.path.splitext(self.dbname)[0] + '.h5'

    def mzml_reader(self,filelist):
        """
        Performs reading chromatography-mass spectrometry data from mzML files

        Args:

            filelist: the list of files

        """
        import pymzml as pyml            
        hf      = h5py.File(os.path.join(self.dbpath, self.dbname), 'w')
        minmass = np.inf
        maxmass = 0.
        minrt   = np.inf
        maxrt   = 0.
        resrt   = -1.

        printlog(" \nReading mzML files from '%s'...\n" % (self.dbpath))
        # loop through the files
        fileindex = 0
        for filepath in filelist:
            fileindex = fileindex + 1
            try:
                dataset = pyml.run.Reader(filepath)
            except Exception as inst:
                printlog("%s: Cannot open file" % filepath)
                printlog(inst)
                traceback.print_exc()
                continue

            try:
                # pre-allocate arrays (faster than appending)
                n_scans  = 0
                n_values = 0
                for sp in dataset:
                    if 'MS:1000511' in sp: # (code 'MS:1000511' for ms level)
                        if sp['MS:1000511']==1: # ms level 1 only
                            if 'MS:1000016' in sp: # (code 'MS:1000016' for retention time value)
                                X  = np.array(sp.centroidedPeaks).astype(float)
                                if len(X) > 0 and len(X.shape) == 2:
                                    healthcheck = np.logical_and(np.all(np.isfinite(X)), np.all(np.isreal(X)));
                                    if healthcheck:
                                        n_values = n_values + len(X)
                                        n_scans  = n_scans + 1
                                    else:
                                        printlog('Slice with numerical errors. Skipping...')
                                else:
                                    printlog('Empty slice. Skipping...')
                                            

                scan_start        = np.zeros(n_scans).astype(int)
                scan_end          = np.zeros(n_scans).astype(int)
                mass_values       = np.zeros(n_values).astype(float)
                intensity_values  = np.zeros(n_values).astype(float)
                time_list         = np.zeros(n_scans).astype(float)

                istart = 0
                iscan  = -1
                dataset = pyml.run.Reader(filepath)
                for sp in dataset:
                    if 'MS:1000511' in sp: # (code 'MS:1000511' for ms level)
                        if sp['MS:1000511']==1: # ms level 1 only
                            if 'MS:1000016' in sp: # (code 'MS:1000016' for retention time value)
                                X  = np.array(sp.centroidedPeaks).astype(float)
                                if len(X) > 0 and len(X.shape) == 2:
                                    healthcheck = np.logical_and(np.all(np.isfinite(X)), np.all(np.isreal(X)));
                                    if healthcheck:
                            
                                        imass_values      = X[:,0]
                                        iintensity_values = X[:,1]
        
                                        iscan = iscan+1
                                        if np.median(np.diff(imass_values))<0:
                                            imass_values= imass_values[::-1]
                                            iintensity_values = iintensity_values[::-1]
        
                                        scan_start[iscan] = istart
                                        iend       = istart + len(imass_values)-1
                                        scan_end[iscan]  = iend
        
                                        mass_values[np.arange(istart,iend+1)] = imass_values[::-1]
                                        intensity_values[np.arange(istart,iend+1)] = iintensity_values[::-1]
                                        istart     = iend+1
        
                                        time_list[iscan]  = sp['MS:1000016']

                                    else:
                                        printlog('Slice with numerical errors. Skipping...')
                                else:
                                    printlog('Empty slice. Skipping...')
                                    

                # arrange data for hdf5 database file storage
                scan_indlist = np.vstack((scan_start,scan_end))

                # in case data are in descending order
                if np.median(np.diff(time_list))<0:
                    time_list    = time_list[::-1]

                # update retention time range and resolution
                minrt = np.min([minrt,np.min(time_list)])
                maxrt = np.max([maxrt,np.max(time_list)])
                if resrt==-1:
                    resrt = np.median(np.diff(time_list))
                else:
                    resrt = 0.5*(np.median(np.diff(time_list))+resrt)

                # update mass range
                minmass = np.min([minmass,np.min(mass_values)])
                maxmass = np.max([maxmass,np.max(mass_values)])

                # sanity check
                if not len(time_list) == len(scan_start):
                    printlog("The number of time points (%d) does not equal the number of scans (%d). Data not deposited!"%(len(time_list), len(scan_start)))
                    continue
                else:
                    # deposit data into hdf5 database file
                    dpath   = 'raw/' + os.path.splitext(os.path.basename(filepath))[0]
                    try:
                        ginfo    = hf.create_group(dpath)
                        try:
                            m5db.save_dataset(ginfo,'mz', data = mass_values,compression_opts = 5)
                            m5db.save_dataset(ginfo,'sp', data = intensity_values, compression_opts = 5)
                            m5db.save_dataset(ginfo,'time',data = (time_list * self.time_mult))
                            m5db.save_dataset(ginfo,'scan',data = scan_indlist)

                           # chunks=(nRows, nCols, 1))
                            printlog('%s. %s: Successfully deposited -> %s' %(fileindex, os.path.basename(filepath), self.dbname))
                            ginfo.attrs['is_raw'] = True;
                            ginfo.attrs['is_OK'] = True;
                            ginfo.attrs['is_processed'] = False;
                            ginfo.attrs['is_continuous'] = True;
                            ginfo.attrs['is_sample_dataset'] = True;
                            #TODO: properly treat test and training data
                            #ginfo.attrs['is_training'] = True;


                        except Exception as inst:
                            printlog('%s. %s: Failed to deposit' %(fileindex, os.path.basename(filepath)))
                            printlog(inst)
                            traceback.print_exc()

                    except Exception as inst:
                        printlog('%s. %s: All files must have unique names: Failed to create a dataset in -> %s' %(fileindex, os.path.basename(filepath), self.dbname))
                        printlog(inst)
                        traceback.print_exc()

            except Exception as inst:
                printlog('%s. %s: Failed to read in data' %(fileindex, os.path.basename(filepath)))
                printlog(inst)
                traceback.print_exc()

        m5db.save_dataset(hf,'raw/cmzrange',data=[np.floor(minmass),np.ceil(maxmass)])
        m5db.save_dataset(hf,'raw/crtrange',data=[np.floor(minrt * self.time_mult), resrt * self.time_mult, np.ceil(maxrt * self.time_mult)])

        printlog('Minimal mz: %s'%np.floor(minmass))
        printlog('Maximal mz: %s'%np.ceil(maxmass))
        printlog('Minimal rt (sec): %s'%np.floor(minrt * self.time_mult))
        printlog('Maximal rt (sec): %s'%np.ceil(maxrt * self.time_mult))

class mzXMLImport(object):
    def __init__(self, filereadinfo, dbname='', dbpath='', time_mult = 1.0):
        """
        Class parameter initialization
        """

        self.dbname = ''
        self.dbpath = ''
        self.time_mult = time_mult

        if dbname!='':
            self.dbpath = os.path.dirname(dbname)
            self.dbname = os.path.basename(dbname)

        if self.dbpath == '':
            if os.path.isdir(dbpath):
                self.dbpath=dbpath
            else:
                self.dbpath=os.getcwd()

        try:
            if not os.path.isdir(self.dbpath):
                os.makedirs(self.dbpath);
        except:
            self.dbpath=os.getcwd()

        if self.dbname == '':
            print('Output database file name not provided. Setting output file name to:');
            self.dbname =  "msdata__" + time.strftime("%H%M_%d_%m_%Y") +".h5"
            print(self.dbname)
        else:
            self.dbname = os.path.splitext(self.dbname)[0] + '.h5'

    def mzxml_reader(self, filelist):
        """
        Performs reading chromatography-mass spectrometry data from NETCDF files

        Args:

            filelist: the list of files

        """
        import mzxml            

        hf      = h5py.File(os.path.join(self.dbpath, self.dbname), 'w')
        minmass = np.inf
        maxmass = 0.
        minrt   = np.inf
        maxrt   = 0.
        resrt   = -1.

        print(" \nReading mzXML files from '%s'...\n" % (self.dbpath))

        #print(filelist)

        # loop through the files
        fileindex = 0
        for filepath in filelist:
            fileindex = fileindex + 1

            try:
                mzXML_scans = mzxml.load_mzxml_file(filepath)
                #raise Exception('Not available yet due to issues.')
            except Exception as inst:
                printlog(inst)
                traceback.print_exc()
                print("%s: Cannot open file" % filepath)
                
                continue

            try:
                mass_values = np.array([])
                intensity_values = np.array([])
                time_list_list = []
                for scan in mzXML_scans:
                    time_list_list.append(scan.retention_time)
                    scan_masses_as_list, scan_intensities_as_list = zip(*scan.peaks)
                    mass_values = np.concatenate((mass_values, np.asarray(scan_masses_as_list)))
                    intensity_values = np.concatenate((intensity_values, np.asarray(scan_intensities_as_list)))

                time_list = np.asarray(time_list_list)
                minmass = np.min([minmass,np.min(mass_values)])
                maxmass = np.max([maxmass,np.max(mass_values)])

                if not len(mass_values) == len(intensity_values):
                    print("The length of mass_list is not equal to the length of intensity_list. Data not deposited!... !")
                    continue


                if np.median(np.diff(mass_values))<0:
                    # descending order arrangment of m/z values
                     scanidx = np.diff(mass_values)>=0
                     descend = 1
                else:
                    # ascending order arrangment of m/z values
                     scanidx = np.diff(mass_values)<=0
                     descend = 0

                # calculate the number of scans
                scanidx = np.append(scanidx,True)
                nscans  = np.sum(scanidx)
                scanidx = np.where(scanidx==True)
                scanidx = scanidx[0][np.arange(0,nscans)]

                # pre-allocate arrays
                scan_start = np.array([]).astype(int)
                scan_end = np.array([]).astype(int)

                # arrange data for hdf5 database file storage
                istart  = 0
                for iend in scanidx:
                    imass_values = mass_values[np.arange(istart,iend+1)]
                    iintensity_values = intensity_values[np.arange(istart,iend+1)]
                    if len(imass_values)>0:
                        if descend==1:
                            mass_values[np.arange(istart,iend+1)] = imass_values[::-1]
                            intensity_values[np.arange(istart,iend+1)] = iintensity_values[::-1]
                        scan_start = np.append(scan_start,istart)
                        scan_end   = np.append(scan_end,iend)
                    istart = iend+1

                # arrange data for hdf5 database file storage
                scan_indlist = np.vstack((scan_start,scan_end))
                if np.median(np.diff(time_list))<0:
                    time_list    = time_list[::-1]
                minrt = np.min([minrt,np.min(time_list)])
                maxrt = np.max([maxrt,np.max(time_list)])
                if resrt==-1:
                    resrt = np.median(np.diff(time_list))
                else:
                    resrt = 0.5*(np.median(np.diff(time_list))+resrt)

                # sanity check
                if not len(time_list) == len(scan_start):
                    print("The number of time points (%d) does not equal the number of scans (%d). Data not deposited!"%(len(time_list), len(scan_start)))
                    continue
                else:
                    # deposit data into hdf5 database file
                    dpath   = 'raw/' + os.path.splitext(os.path.basename(filepath))[0]
                    try:
                        ginfo    = hf.create_group(dpath)
                        try:
                            m5db.save_dataset(ginfo,'mz', data = mass_values,compression_opts = 5)
                            m5db.save_dataset(ginfo,'sp', data = intensity_values, compression_opts = 5)
                            m5db.save_dataset(ginfo,'time',data = time_list * self.time_mult)
                            m5db.save_dataset(ginfo,'scan',data = scan_indlist)

                           # chunks=(nRows, nCols, 1))
                            print('%s. %s: Successfully deposited -> %s' %(fileindex, os.path.basename(filepath), self.dbname))

                        except:
                            print('%s. %s: Failed to deposit' %(fileindex, os.path.basename(filepath)))
                    except:
                        print('%s. %s: All files must have unique names: Failed to create a dataset in -> %s' %(fileindex, os.path.basename(filepath), self.dbname))
            except:
                raise
                print('%s. %s: Failed to read in data' %(fileindex, os.path.basename(filepath)))
        m5db.save_dataset(hf,'raw/cmzrange',data=[np.floor(minmass),np.ceil(maxmass)])
        m5db.save_dataset(hf,'raw/crtrange',data=[np.floor(minrt * self.time_mult), resrt * self.time_mult, np.ceil(maxrt * self.time_mult)])

        printlog('Minimal mz: %s'%np.floor(minmass))
        printlog('Maximal mz: %s'%np.ceil(maxmass))
        printlog('Minimal rt (sec): %s'%np.floor(minrt * self.time_mult))
        printlog('Maximal rt (sec): %s'%np.ceil(maxrt * self.time_mult))


if __name__ == "__main__":
    tic();
    settings=OptionsHolder(__doc__, ImportSet_options);
    settings.description='Import Raw Data';
    printlog(settings.program_description);
    #Parse command line parameters
    try:
        settings.parse_command_line_args()   
    except Exception as inst:
        printlog('!!! Error in command line parameters: !!!');
        printlog(inst);
        printlog('\nRun python ' + sys.argv[0] + ' --help for command line options information!');
        sys.exit(-1)

    parameters = settings.parameters;
    if parameters['logfile'] != '':
        start_log(parameters['logfile'], overwrite_existing = (parameters['overwrite_logfile'] == 'yes'), verbosity_level = parameters['verbose']);
        printlog(settings.program_description, print_enabled = False);

    printlog('Started on %s ...'%(time.strftime("%a, %d %b %Y at %H:%M:%S")));
    printlog(settings.format_parameters());

    settings.do='yes';

    main(settings.parameters['datapath'], settings.parameters['filetype'], settings.parameters['filereadinfo'], settings.parameters['dbfilename']);

    printlog('\nFinished on %s in'%(time.strftime("%a, %d %b %Y at %H:%M:%S")));
    toc();
    printlog(settings.description_epilog);
    stop_log();

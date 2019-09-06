# -*- coding: utf-8 -*-
"""

************************
HDF5-database management
************************

The module includes a set of methods for organization, management and rapid retrieval of MSI data 
via HDF5-based chunked layouts

"""

#===========================Import section=================================

#Importing standard and external modules
import h5py
import sys
import os
import re
import traceback
import numpy as np;

#If run independently - check system endianness and add path to local modules
if __name__ == "__main__":
    if sys.byteorder!='little':
        print('Only little endian machines currently supported! bye bye ....');
        quit();
    module_path = os.path.abspath('%s/../..'%os.path.dirname(os.path.realpath(__file__)));
    sys.path.insert(0, module_path);

#Import local/internal modules
from proc.utils.typechecker import is_string, iteritem 
from proc.utils.printlog import printlog, LoggingException;
from proc.utils.h5utils import h5read_strings;

#==========================================================================
#From here the main code starts

class H5FileError(LoggingException):
    pass

class HDF5Error(LoggingException):
    pass

class OperationError(LoggingException):
    pass

class LoggingIOError(LoggingException):
    pass

class LoggingValueError(LoggingException):
    pass
  
def save_dataset(dbfilepath, pathinh5, data, chunksize = '', compression_opts = ''):
    
    pathinh5 = re.sub('//','/',pathinh5)
    
    if is_string(dbfilepath) and (os.path.exists(dbfilepath)):
        h5file_group = h5py.File(dbfilepath,'a')
        isdbfile=1
    elif (isinstance(dbfilepath,h5py.File)) or (isinstance(dbfilepath,h5py.Group)): 
        h5file_group = dbfilepath
        isdbfile=0
    else:
        return
    
    try:        
        isdata = pathinh5 in h5file_group
    except Exception as inst:
        printlog(inst)
        traceback.print_exc()
        return
        
    if isdata:
        fdata = h5file_group[pathinh5]
        
        if (fdata.shape == data.shape) and (fdata.dtype == data.dtype):
            fdata[...] = data
            return
        else:
            printlog('Deleting original');
            del h5file_group[pathinh5];
            
        
    if (not chunksize) and (not compression_opts):
        h5file_group.create_dataset(pathinh5,data=data)
    elif (chunksize) and (compression_opts):
        h5file_group.create_dataset(pathinh5,data=data, chunks = chunksize, 
                                     compression = "gzip", compression_opts = compression_opts)
    elif (chunksize):
        h5file_group.create_dataset(pathinh5,data=data, chunks = chunksize )
    elif (compression_opts):
        h5file_group.create_dataset(pathinh5,data=data, chunks = True, 
                                     compression = "gzip", compression_opts = compression_opts)
        
    if isdbfile==1:
        h5file_group.close()
    return

def load_dataset(dbfilepath, pathinh5):
    
    pathinh5 = re.sub('//','/',pathinh5)
    
    dataset=[]    
    if is_string(dbfilepath) and (os.path.exists(dbfilepath)):
        h5file_group = h5py.File(dbfilepath,'a')
        isdbfile=1
    elif (isinstance(dbfilepath,h5py.File)) or (isinstance(dbfilepath,h5py.Group)): 
        h5file_group = dbfilepath
        isdbfile=0
    else:
        return dataset
    
    try:        
        isdata = pathinh5 in h5file_group
    except Exception as inst:
        printlog(inst)
        traceback.print_exc()
        return dataset
    
    if isdata ==True:
        dataset = h5file_group[pathinh5][()]
        
    if isdbfile==1:
        h5file_group.close()
    
    return dataset
        
def save_preproc_obj(dbfilepath, ProcObj, pathinh5 =''):
    
    """
    **Saves the pre-processing parameters of a module into the hdf5 database.**
    
    Args: 
        
        dbfilepath: the name and path to the hdf5-database file
        
        ProcObj: the pre-processing workflow object
        
        pathinh5: the path in the hdf5 file for object storage
        
    """ 
    
    h5objpath = pathinh5 + ProcObj.description
    h5objpath = re.sub('//','/',h5objpath)
    
    if is_string(dbfilepath) and (os.path.exists(dbfilepath)):
        h5file_group = h5py.File(dbfilepath,'a')
        isdbfile=1
    elif (isinstance(dbfilepath,h5py.File)) or (isinstance(dbfilepath,h5py.Group)): 
        h5file_group = dbfilepath
        isdbfile=0
    else:
        return

    try:    
        objvars = vars(ProcObj)
    except Exception as inst:
        printlog(inst)
        traceback.print_exc()
        return

    try:
        isgroup = h5objpath in h5file_group
    except Exception as inst:
        printlog(inst)
        traceback.print_exc()
        return
    
    if isgroup==False:
        h5file_group.create_group(h5objpath)
    else:
        printlog('%s object has already been saved into the database file' %h5objpath)
        return
    
    
    h5obj = h5file_group[h5objpath]
    for i_name in objvars.keys():
        subobj = objvars[i_name]
        if isinstance(subobj,dict):
            h5obj.create_group(i_name)
            h5subobj = h5obj[i_name]
            for j_name in subobj.keys():
                save_dataset(h5subobj,j_name,subobj[j_name])
        else:                
            save_dataset(h5obj,i_name,objvars[i_name])
    
    printlog('\n%s from pre-processing workflow have been saved to --> %s' %(h5objpath,str(dbfilepath)))
    
    if isdbfile==1:
        h5file_group.close()
    
def load_preproc_obj(dbfilepath,procid, pathinh5 =''):
    
    """
    
    **Loads the pre-processing parameters of a module from the hdf5 database.**
    
    Args: 
        
        dbfilepath: the name and path to the hdf5-database file
        
        procid: the module identifier
        
        pathinh5: the path in the hdf5 file for object storage
        
    """ 
    
    h5objpath = pathinh5 +procid
    h5objpath = re.sub('//','/',h5objpath)
    
    ProcObj = {}
    if is_string(dbfilepath) and (os.path.exists(dbfilepath)):
        h5file_group = h5py.File(dbfilepath,'a')
        isdbfile=1
    elif (isinstance(dbfilepath,h5py.File)) or (isinstance(dbfilepath,h5py.Group)): 
        h5file_group = dbfilepath
        isdbfile=0
    else:
        return ProcObj
        
    try:
        isobj = h5objpath in h5file_group
    except Exception as inst:
        printlog(inst)
        traceback.print_exc()
        return ProcObj
        
    if isobj==False:
        return ProcObj
    # check whether this object is part of the preprocessing workflow
    h5obj = h5file_group[h5objpath]
    for i_name in h5obj.keys():
        if isinstance(h5obj[i_name],h5py.Group):
            h5subobj = h5obj[i_name]
            subProcObj = {}
            for j_name in h5subobj.keys():
                 subProcObj[j_name] = load_dataset(h5subobj,j_name)
            ProcObj[i_name] = subProcObj
        else:
            ProcObj[i_name] = load_dataset(h5obj,i_name)
              
    if isdbfile==1:
        h5file_group.close()

    return ProcObj

def get_dataset_names(dbfilepath, dbroot='', dataset_names=[], pathinh5 = []):
    """
        
    Recursively exctracts dataset names from hdf5 database
        
    """    
    if is_string(dbfilepath) and (os.path.exists(dbfilepath)):
        h5file = h5py.File(dbfilepath,'r')
        item   = h5file
        isdbfile = 1
    elif (isinstance(dbfilepath, h5py.File)) or (isinstance(dbfilepath, h5py.Group)): 
        item = dbfilepath
        isdbfile = 0
    else:
        return dataset_names
        
    for key, val in iteritem(dict(item)):
        #printlog(key, val)
        try: 
            subitem = dict(val)
            if ('mz' in subitem) or ('sp' in subitem) or ('sp_unfiltered_peaks' in subitem) or (('is_sample_dataset' in subitem.attrs) and (subitem.attrs['is_sample_dataset'] == True)):
                success = 1
            else:
                success = 0
        except Exception as inst:
            #printlog(inst)
            #traceback.print_exc()
            success = 0
        if success==1:
            if is_string(pathinh5):
                success = 0
                h5str = val.name.split('/')[0:2]
                for i in h5str:
                    if '/'+i==pathinh5:
                        datasetname = re.sub(pathinh5,'',val.name)
                        dataset_names.append(datasetname)
                        success=1
                        break
            else:
                dataset_names.append(val.name)
        if success==0:
            if isinstance(val,h5py.Group):
                dbroot = dbroot + val.name
                dataset_names = get_dataset_names(val,dbroot,dataset_names,pathinh5=pathinh5)
    
    if isdbfile==1:
        h5file.close()

    return sorted(dataset_names)

def get_traindata_names(dbfilepath, dbroot='', dataset_names=[], istrain=1):
    """
    
    Recursively exctracts dataset names from hdf5 database
    
    """    
    if is_string(dbfilepath) and (os.path.exists(dbfilepath)):
        h5file = h5py.File(dbfilepath,'r')
        item   = h5file
        isdbfile=1
    elif (isinstance(dbfilepath,h5py.File)) or (isinstance(dbfilepath,h5py.Group)): 
        item = dbfilepath
        isdbfile=0
    else:
        return dataset_names
        
    for key, val in iteritem(dict(item)):
        try: 
            subitem = dict(val)
            if ('istrain' in subitem) and ('Sp' in subitem):
                if load_dataset(item,val.name+'/istrain')==istrain:
                    success = 1
                else:
                    success = 0
            else:
                success = 0
        except Exception as inst:
            printlog(inst)
            traceback.print_exc()
            success = 0
        if success==1:
            dataset_names.append(val.name)
        elif isinstance(val,h5py.Group):
            dbroot = dbroot + val.name
            dataset_names = get_traindata_names(val,dbroot,dataset_names,istrain)
    if isdbfile==1:
        h5file.close()

    return dataset_names
 
 
def print_structure_h5db(dbfilepath, dbroot = '', offset='    ') :
    """Prints the HDF5 database structure"""
    if is_string(dbfilepath) and (os.path.exists(dbfilepath)):
        h5file = h5py.File(dbfilepath,'r')
        item   = h5file
        isdbfile=1
    elif (isinstance(dbfilepath,h5py.File)) or (isinstance(dbfilepath,h5py.Group)): 
        item = dbfilepath
        isdbfile=0
    else:
        return 
    
    if  isinstance(item,h5py.File):
       printlog(item.file, '(File)', item.name)
 
    elif isinstance(item,h5py.Dataset):
        printlog('(Dataset)', item.name, '    len =', item.shape) #, g.dtype
 
    elif isinstance(item,h5py.Group):
        printlog('(Group)', item.name)
 
    else:
        printlog('Warning: The item type is unkown', item.name)
        sys.exit ( "execution is terminated" )
 
    if isinstance(item, h5py.File) or isinstance(item, h5py.Group):
        for key,val in dict(item).iteritems() :
            subitem = val
            printlog(offset, key) #,"   ", subg.name #, val, subg.len(), type(subg),
            dbroot = dbroot+'i'
            print_structure_h5db(subitem,  dbroot = dbroot, offset = '    ')
    
    if isdbfile==1:
       h5file.close()

def conv_dict2strlist(d):
    fields = d.keys()
    s = []    
    for field in fields:
        s.append(field)
        vals = d[field]
        if isinstance(vals,list):
            if len(vals)>2:
                vals = vals[:2]
        s.append(str(vals))
    h5slist = [n.encode("ascii", "ignore") for n in s]
    return h5slist




#--------------------------------------------------------------------

'''
def get_attribute_names(work_group, return_sorted = True, filter_by_names = []):
    """
    Returns the list of attribute names (optionally filtered and sorted).
    
    """
    result = list(work_group.attrs.keys());
    
    if filter_by_names:
        set_names = set(filter_by_names);
        for i in reversed(range(len(result))):
            if not (result[i] in set_names):
                del result[i];

    if return_sorted:
        return sorted(result);
    else:
        return result;


def get_attributes(work_group, filter_by_names = []):
    """
    Returns the dictionary of attributes.
    
    """
    
    result = {};
    attribute_names = get_attribute_names(work_group, return_sorted = False, filter_by_names = filter_by_names);
    for aname in attribute_names:
        result[aname] = work_group.attrs[aname];
    return result;


def get_dataset_names2(work_group, return_sorted = True, return_full_paths = False, filter_by_names = [], filter_by_attributes = {}):
    """
    Returns the list of dataset names within the group. Optionally filtered by names and/or attribute values.
    
    """
    result = [];
    
    for key in work_group:
        if isinstance(work_group[key], h5py.Dataset):
            result.append(key);
    
    if filter_by_names:
        filter_names = set(filter_by_names);    
        for i in reversed(range(len(result))):
            if not result[i] in filter_names:
                del result[i];
    
    if filter_by_attributes:
        for key in filter_by_attributes:
            for i in reversed(range(len(result))):
                wds = work_group[result[i]];
                if key in wds.attrs:
                    if wds.attrs[key] != filter_by_attributes[key]:
                        del result[i];
                else:
                    del result[i];

    if return_full_paths:
        pre_path = work_group.name;
        for i in range(len(result)):
            result[i] = '/'.join([pre_path, result[i]]);

    if return_sorted:
        return sorted(result);
    else:
        return result;

'''


def match_attributes(attrs, filter_attributes):
    """
    Check if attributes in filter_attributes are present and equal to the ones 
    in attrs
    """

    result = True;

    for key in filter_attributes.keys():
        if not (key in attrs):
            result = False;
            break;
        elif attrs[key] != filter_attributes[key]:
            result = False;
            break;
    
    return result



def split_mask(selection):
    selection = selection.split('/');
    path = [];
    mask = [];
    inpath = True;
    for i in selection:
        if ('?' in i) or ('*' in i):
            inpath = False;
        if inpath:
            path.append(i);
        else:
            mask.append(i);
    
    return '/'.join(path), mask;

def __findline(submask, itemid):
    if submask == '':
        return 0;
    if '?' in submask:
        leftmask, rightmask = submask.split('?', 1);
        if not leftmask in itemid:
            return -1;
        
        while leftmask in itemid:
            subindex = itemid.index(leftmask);
            
            subid = itemid[(subindex + len(leftmask)+1):];
            
            if len(subid) < len(rightmask):
                return -1
            
            allmatch = True;
            for i in range(len(rightmask)):
                if rightmask[i] != subid[i] and rightmask[i] != '?':
                    allmatch = False;
                    break;
            if allmatch:    
                return subindex;
            
            itemid = itemid[(subindex + len(leftmask)+1):];
        
        return -1;
        
    else:
        if submask in itemid:
            return itemid.index(submask);
        else:
            return -1;
        
    

def mask_matched(itemid, mask):
    while '**' in mask:
        mask = mask.replace('**','*');
   
    mask = mask.split('*');
    masklen = len(mask);
    
    for i in range(masklen):
        submask = mask[i];
        j = __findline(submask, itemid);
        if i == 0:
            if j < 0:
                return False;
            if (j != 0) and (submask != ''):
                return False;
        elif i == masklen - 1:
            if submask == '':
                return True
            else:
                return j >= 0;
        else:
            if j < 0:
                return False
            else:
                itemid = itemid[(j+len(submask)):];
    return True        


def match_masks(value, masks = None):
    """
    Match string to the list of masks or a single mask
    """
    result = False;
    
    if masks is None:
        mask = [];

    if not isinstance(masks, list):
        masks = [str(masks)];
        
    if not masks:
        masks.append('*');
    
    for mask in masks:
        if mask_matched(str(value), str(mask)):
            result = True;
            break;
            
    return result;

def get_subgroup_names(work_group, return_sorted = True, return_full_paths = False, recursive = False, filter_by_names = None, filter_by_attributes = None):
    """
    Returns the list of sub-groups names within the group. Optionally filtered by names and/or attribute values.
    
    """
    
    if filter_by_names is None:
        filter_by_names = [];
        
    if filter_by_attributes is None:
        filter_by_attributes = {};
        
    result = [];
    
    for key in work_group:
        if isinstance(work_group[key], h5py.Group):
            result.append(work_group[key]);

    new_result = [];
    
    for i in reversed(range(len(result))):    
        group = result[i].name;
        accepted_via_children = False;
        if recursive:
            sub_groups = get_subgroup_names(result[i], 
                                            return_sorted = return_sorted, 
                                            return_full_paths = True, 
                                            recursive = recursive, 
                                            filter_by_names = filter_by_names, 
                                            filter_by_attributes = filter_by_attributes);
            if sub_groups:
                accepted_via_children = True;
                new_result.append(group);
                new_result += sub_groups;

        if not accepted_via_children:
            if filter_by_names:
                if not match_masks(group, filter_by_names):
                    continue
            if filter_by_attributes:
                if not match_attributes(result[i].attrs, filter_by_attributes):
                    continue
            new_result.append(group);


    if not return_full_paths:
        pathlen = len(work_group.name);
        for i in range(len(new_result)):
            new_result[i] = new_result[i][pathlen + 1:];
        
    if return_sorted:
        return sorted(new_result);
    else:
        return new_result;


    

def get_dataset_names_from_hdf5(h5file, 
                      h5readpath, 
                      filter_by_names = None, 
                      filter_by_attributes = None,
                      return_indeces = False,
                      ):
    
    if not h5readpath.startswith('/'):
        raise HDF5Error('h5readpath must be an absolute path!');
    
    if filter_by_names is None:
        filter_by_names = [];
    
    if filter_by_attributes is None:
        filter_by_attributes = {};                  
                                        
    filter_by_attributes['is_sample_dataset'] = True;                                    
    
    if not h5readpath in h5file:
        raise H5FileError('Error! "%s" group not found in %s!'%(h5readpath, h5file.filename));
        
    work_group = h5file[h5readpath];
    
    if not isinstance(work_group, h5py.Group):
        raise H5FileError('Error! "%s" is not a group in %s!'%(h5readpath, h5file.filename));
        
    if not filter_by_names:
        filter_by_names = ['*'];
        
    abs_filter_by_names = [];    
    
    for filter_name in filter_by_names:
        abs_filter_by_names.append('/'.join([h5readpath, filter_name]));
    
    sub_groups = get_subgroup_names(work_group, 
                                    return_sorted = True, 
                                    return_full_paths = False, 
                                    recursive = False, 
                                    filter_by_names = abs_filter_by_names, 
                                    filter_by_attributes = filter_by_attributes);
    
    if return_indeces:
        if (not 'dataset_names' in work_group) or (not 'utf_8' in work_group):
            raise H5FileError('Error! "dataset_names" or "utf-8" not found in "%s" in %s ! They are essential for index return!'%(h5readpath, h5file.filename));
        
        dataset_names = work_group['dataset_names'];
        utf_8 = work_group['utf_8'];
        
        d_names = h5read_strings(dataset_names, utf_8);
        
        d_names_indeces = {};
        
        indeces = [];
                
        for i in range(len(d_names)):
            d_names_indeces[d_names[i]] = i;
            
        for i in range(len(sub_groups)):
            try:
                indeces.append(d_names_indeces[sub_groups[i]]);
            except:
                raise H5FileError('"%s" not found in "dataset_names" in "%s" of %s! Inconsistency detected!' %(sub_groups[i], h5readpath, h5file.filename));
                
        indeces = np.array(indeces, dtype = np.int64);
        
        idx = np.argsort(indeces);
        indeces = indeces[idx];
        
        sub_groups = [x for _,x in sorted(zip(idx.tolist(), sub_groups))];
        
        return sub_groups, indeces;
                                
    else:
        return sub_groups;



def get_short_name(name):
    name = name.split('/')[-1];
    if name == '':
        name = '/';
    return name


def split_hdf5_path(item):
    return '/'.join(item.split('/')[:-1]) + '/';
    
    
def copy_attributes(source, destination):
    for attribute in source.attrs.keys():
        destination.attrs[attribute] = source.attrs[attribute];


def rel_hdf5_path(h5path, reference_path = '/'):
    """
    Make absolute HDF5 path relative to reference_path
    """
    if not h5path.startswith('/'):
        raise OperationError('Input path should be absolute path!');

    if not reference_path.startswith('/'):
        raise OperationError('Reference path should be absolute path!');
        
    end_slash = h5path.endswith('/');
        
    h5path = h5path.split('/');
    reference_path = reference_path.rstrip('/').split('/');
        
    index = -1;        
    for i in range(min(len(h5path), len(reference_path))):
        if h5path[i] == reference_path[i]:
            index = i;
        else:
            break;

    newpath = ['..'] * (len(reference_path) - index - 1);

    for i in range(index + 1, len(h5path)):
        if h5path[i] != '':
            newpath.append(h5path[i]);
        
    if len(newpath) == 0:
        newpath = ['.'];

    result = '/'.join(newpath);

    if end_slash:
        if not result.endswith('/'):
            result += '/';
        
    return result;
    
    
    
    
def abs_hdf5_path(h5path, reference_path = '/'):
    """
    Make HDF5 relative path absolute
    """
    if not reference_path.startswith('/'):
        raise OperationError('Reference path should be absolute path!');

    if not h5path.startswith('/'):
        h5path = reference_path.rstrip('/') + '/' + h5path;
        
    end_slash = h5path.endswith('/');
    
    h5path = h5path.split('/');

    newpath = [];
    for i in range(len(h5path)):
        if h5path[i] == '..':
            if len(newpath) > 0:
                del newpath[-1];
            else:
                printlog('Error! Cannot go above root with ".." in path! Staying at root!');
        elif h5path[i] != '.' and h5path[i] != '':
            newpath.append(h5path[i]);
        
    result = '/%s'%('/'.join(newpath));

    if end_slash:
        if not result.endswith('/'):
            result += '/';
        
    return result;


def print_attributes(item):
    for attribute in item.attrs.keys():
        printlog('      %s = %s'%(attribute, item.attrs[attribute]));



def _get_mask_for_rts(rts, rt_list, rt_tolerance):
    
    if '*' in rt_list:
        return np.full(rts.shape, True, dtype = np.bool);
    
    n_rts = len(rts);
    rts = np.array(rts).tolist();
    mask = np.zeros((n_rts, ), dtype = np.int8);
    rt_tolerance = rt_tolerance * 60.0;

    rt_list_points = [];
    #print(rts)
    for rt in rt_list:
        #print(rt)
        if '-' in rt:
            rt = rt.split('-');

            if '*' in rt[0]:
                min_rt = rts[0];
            else:
                min_rt = float(rt[0]) * 60.0;
                
            if '*' in rt[1]:
                max_rt = rts[-1];
            else:
                max_rt = float(rt[1]) * 60.0;
            
            if max_rt < min_rt:
                min_rt, max_rt = max_rt, min_rt;
                
            min_rt = min_rt - rt_tolerance;
            max_rt = max_rt + rt_tolerance;
            indexes = np.searchsorted(rts, [min_rt, max_rt]);
            mask[indexes[0]:indexes[1]] = 1;
            #print(mask)    
        else:
            rt_list_points.append(float(rt) * 60.0);
    
    #print(rt_list_points)    
    
    refrt = np.sort(np.array(rt_list_points) * 60.0).tolist();
    i = 0;
    j = 0;
    n_refrts = len(refrt);
    
    while (i < n_rts) and (j < n_refrts):
        d = rts[i] - refrt[j];
        if abs(d) <= rt_tolerance:
            mask[i] = 1;
            i += 1;
        elif d < 0.0:
            i += 1;
        else:
            j += 1;
    
    #print(mask)
    return mask > 0;




def get_processed_rt_indeces(h5file, h5readpath, rt_list, rt_tolerance):

    rts_set = h5readpath + '/grouped_rts';
    if not (rts_set in h5file):
        raise H5FileError('Error! grouped_rts not found in [%s]%s ! Skipping...'%(h5file.filename, h5readpath));
    
    rts = h5file[rts_set];
        
    rts_mask = _get_mask_for_rts(rts, rt_list, rt_tolerance);
    
    return np.arange(rts_mask.shape[0], dtype = np.int64)[rts_mask];
        
    
def has_metadata_entries(h5file, h5readpath, dataset_name, metadata_entries):

    metapath = h5readpath + '/' + dataset_name + '/MetaData';
    if not metapath in h5file:
        return [False] * len(metadata_entries);

    metagroup = h5file[metapath];
    if not isinstance(metagroup, h5py.Group):
        return [False] * len(metadata_entries);
    
    result = [];
    for entry in metadata_entries:
        result.append(entry in metagroup.attrs);
    
    return result;
    
def get_metadata(h5file, h5readpath, dataset_name):
    metapath = h5readpath + '/' + dataset_name + '/MetaData';
    if not metapath in h5file:
        return {};

    metagroup = h5file[metapath];
    if not isinstance(metagroup, h5py.Group):
        return {};
    
    return metagroup.attrs;
    


'''
def list_dataset_contents(dataset, offset = 4, pre_space = '', return_sorted = True, draw_lines = True, show_attributes = True):
    """
    Return textual list of dataset (attributes)
    
    """
    result = [];
    if show_attributes:
        attributes = get_attribute_names(dataset, return_sorted = return_sorted);
    else:
        attributes = [];
        
        
    if draw_lines:
        str_mid_offset = u' ├' + u'─' * (offset - 3) + ' ';
        str_last_offset = u' └' + u'─' * (offset - 3) + ' ';
        str_inter_mid = u' │' + u' ' * (offset -2);
        str_inter_last = u' ' * offset;
    else:
        str_mid_offset = u' ' * offset;
        str_last_offset = str_mid_offset;
        str_inter_mid = str_mid_offset;
        str_inter_last = str_mid_offset;
        
    result.append('%s%s%s : %s of %s'%(pre_space, ' ' * (offset - 1), get_short_name(dataset.name), dataset.shape, dataset.dtype))
    
    #TODO: Show attributes of the dataset
    #if attributes:
    #    result.append('%s%sAttributes:'%(pre_space, ' ' * (offset * 2)));
    #    for attribute in attributes:
    #        pass
    #        #result.append(u'%s%s%s = %s'%(pre_space + inner_offset,' ' * (offset - 1), attribute, work_group.attrs[attribute]));
    #    result.append('%s'%(pre_space))
    
        
    return result    
'''
    






'''

def __get_masked_items_from_group(h5group, mask, recursive = True):
    path = h5group.name;
    groups = [];
    datasets = [];
    result = [];
    for itemid in h5group.keys():
        if mask:
            if not mask_matched(itemid, mask[0]):
                continue
        item = h5group[itemid];
        if isinstance(item, h5py.Group):
            groups.append(itemid);
        elif isinstance(item, h5py.Dataset):
            datasets.append(itemid);
        else:
            printlog('Unknown element type of %s : %s'%(itemid, type(item)));
                     
    groups = sorted(groups);

    if len(mask)>1:
        for group in groups:
            result += __get_masked_items_from_group(h5group[group], mask[1:], recursive = recursive);
    elif recursive:
        for group in groups:
            result += __get_masked_items_from_group(h5group[group], [], recursive = recursive);
    else:
        groups = sorted(groups);
        for group in groups:
            result.append(path + '/' + group);
    
    if len(mask)<=1:
        datasets = sorted(datasets);
        for dataset in datasets:
            result.append(path + '/' + dataset);
        
    return result
    
'''    
    
        
'''    

def get_items_list_from_hdf5(h5file, selection, recursive = True):
    
    if not selection.startswith('/'):
        raise OperationError('Selection should be absolute path!');
        
    if selection.endswith('/'):
        selection += '*';
        
    path, mask = split_mask(selection);
    
    if mask:
        if not path in h5file:
            return [];
        base_group = h5file[path];
        if isinstance(base_group, h5py.Group):
            return __get_masked_items_from_group(base_group, mask, recursive = recursive);
        else:
            return [];
    else:
        if path in h5file:
            return [path]
'''    
'''    
    
def passes_group_filter(group, group_filter):
    if group_filter == '':
        return True;
    
    
    return True;
    
def passes_dataset_filter(dataset, dataset_filter):
    if dataset_filter == '':
        return True;
    
    
    return True;
'''
'''

def filter_hdf5_items_list(h5file, itemslist, include_groups = True, include_datasets = True, group_filter = '', dataset_filter = ''):
    result = [];
    for item_name in itemslist:
        if item_name in h5file:
            item = h5file[item_name];
            if isinstance(item, h5py.Group):
                if include_groups:
                    if passes_group_filter(item, group_filter):
                        result.append(item_name);
            elif isinstance(item, h5py.Dataset):
                if include_datasets:
                    if passes_dataset_filter(item, dataset_filter):
                        result.append(item_name);
            else:
                printlog('Error! Item %s of unknown type %s! Skipping!'%(item_name, type(item)));
    
    
    
    return result;
    
'''
    
    
'''    
def copy_hdf5_item(h5file, source, destination):
    item = h5file[source];
    if isinstance(item, h5py.Group):
        if destination in h5file:
            group = h5file[destination];
        else:
            group = h5file.create_group(destination);
        copy_attributes(item, group);
    elif isinstance(item, h5py.Dataset):
        if destination in h5file:
            del h5file[destination];
        h5file.copy(source, split_hdf5_path(destination));
    else:
        printlog('Error! %s item is neither Group nor Dataset! Ignoring...'%(source));
    
'''    
'''
def list_group_contents(work_group, offset = 4, pre_space = '', inner_pre_space = '', return_sorted = True, recursive = True, draw_lines = True, show_datasets = True, show_attributes = True):
    """
    Return textual list of hdf5 group internal contents
    
    """
    result = [];
    if show_attributes:
        attributes = get_attribute_names(work_group, return_sorted = return_sorted);
    else:
        attributes = [];
        
    if show_datasets:
        datasets = get_dataset_names2(work_group);
    else:
        datasets = [];
        
    sub_groups = get_subgroup_names(work_group, return_sorted, recursive = False, return_full_paths = False);
    
        
    if draw_lines:
        str_mid_offset = u' ├' + u'─' * (offset - 3) + ' ';
        str_last_offset = u' └' + u'─' * (offset - 3) + ' ';
        str_inter_mid = u' │' + u' ' * (offset -2);
        str_inter_last = u' ' * offset;
    else:
        str_mid_offset = u' ' * offset;
        str_last_offset = str_mid_offset;
        str_inter_mid = str_mid_offset;
        str_inter_last = str_mid_offset;
        
    result.append('%sGroup "%s"'%(pre_space, get_short_name(work_group.name)))
    
    if attributes:
        if sub_groups or datasets:
            str_offset = str_mid_offset;
            inner_offset = str_inter_mid;
        else:
            str_offset = str_last_offset;
            inner_offset = str_inter_last;
        
        result.append('%sAttributes:'%(inner_pre_space+str_offset));
        for attribute in attributes:
            result.append(u'%s%s%s = %s'%(inner_pre_space + inner_offset,' ' * (offset - 1), attribute, work_group.attrs[attribute]));
        result.append('%s'%(inner_pre_space + inner_offset))

    if datasets:

        if sub_groups:
            str_offset = str_mid_offset;
            inner_offset = str_inter_mid;
        else:
            str_offset = str_last_offset;
            inner_offset = str_inter_last;
            
        result.append('%sData sets:'%(inner_pre_space+str_offset));    

        for i in range(len(datasets)):
            result += list_dataset_contents(work_group[datasets[i]], offset = offset, pre_space = inner_pre_space + inner_offset, return_sorted = return_sorted, draw_lines = draw_lines, show_attributes = show_attributes);
        
        result.append('%s'%(inner_pre_space + inner_offset))    
    
    for i in range(len(sub_groups)):
        if i != len(sub_groups)-1:
            str_offset = str_mid_offset;
            inner_offset = str_inter_mid;
        else:
            str_offset = str_last_offset;
            inner_offset = str_inter_last;
            
        result += list_group_contents(work_group[sub_groups[i]], offset = offset, pre_space = inner_pre_space + str_offset, inner_pre_space = inner_pre_space + inner_offset, return_sorted = return_sorted, recursive = recursive, draw_lines = draw_lines, show_datasets = show_datasets, show_attributes = show_attributes);
        #printlog('%s%sGroup "%s"'%(pre_space, str_offset, sub_groups[i]))

    if sub_groups:    
        result.append('%s'%(inner_pre_space))

    return result
'''



'''

def print_group_contents(work_group, offset = 4, pre_space = '', inner_pre_space = '', return_sorted = True, recursive = True, draw_lines = True, show_datasets = True, show_attributes = True):
    """
    Print hdf5 group internal contents
    
    """
    printlog('\n'.join(list_group_contents(work_group, offset, pre_space, inner_pre_space, return_sorted, recursive, draw_lines, show_datasets, show_attributes)));
    
'''    
    
'''
def print_structure_h5db2(dbfile, subpath = '', offset = 4, return_sorted = True, recursive = True, draw_lines = True):
    """
    Print hd5file internal structure.
    
    """
    if not (isinstance(dbfile, h5py.File) or isinstance(dbfile, h5py.Group)):
        if os.path.exists(dbfile):
            with h5py.File(dbfile, 'r') as h5file:
                print_structure_h5db2(h5file, subpath, offset, return_sorted, recursive, draw_lines);
        else:
            raise H5FileError('HDF5 file "%s" not found!'%dbfile);
    else:
        printlog('File "%s":'%dbfile.filename);

        if not subpath.startswith('/'):
            subpath = '/%s'%subpath;

        work_group = dbfile[subpath];
        print_group_contents(work_group, offset, pre_space = '', inner_pre_space = ' '*offset, return_sorted = return_sorted, recursive = recursive, draw_lines = draw_lines);
        
'''

#TODO: test it using datasets and subgroups
def recursive_copy_group_contents(source, target, overwrite = True):
    """
    Recursively copy group contents considering overwrite setting
    
    """
    for attribute in source.attrs.keys():
        if not (attribute in target.attrs) or overwrite:
            target.attrs[attribute] = source.attrs[attribute];
    
    for key in source.keys():
        item = source[key];
        if isinstance(item, h5py.Group):
            if key in target:
                oitem = target[key];
                if not isinstance(oitem, h5py.Group):
                    raise H5FileError('Error! Cannot copy group %s from %s into existing dataset %s in %s!'%(key, source.name, key, target.name));
            else:
                oitem = target.create_group(key);
            recursive_copy_group_contents(item, oitem, overwrite);
        elif isinstance(item, h5py.Dataset):
            if not (key in target) or overwrite:
                if key in target:
                    del target[key];
                source.copy(item, target, name = key);
        else:
            printlog('Unsupported item %s of type %s ignored!'%(key, type(item)));
    
    

def copy_meta_over(source_group, target_group, overwrite = True, clean_copy = False):
    """
    Pass metadata from source group to target group. Both should be open, target
    should be writeable. overwrite controls if the existing metadata entries 
    should be overwritten. clean_copy destroys existing metadata in target prior
    to copying to avoid mixing of different metadata states, but only if the 
    source group contains metadata.
    """
    if not ('MetaData' in source_group):
        return
    
    if source_group == target_group:
        return
    
    if ('MetaData' in target_group) and clean_copy:
        del target_group['MetaData'];
        
    if 'MetaData' in target_group:
        tmetagroup = target_group['MetaData'];
    else:
        tmetagroup = target_group.create_group('MetaData');
    
    smetagroup = source_group['MetaData'];
    
    recursive_copy_group_contents(smetagroup, tmetagroup, overwrite = overwrite);
    
    target_group.attrs['has_metadata'] = True;

    
if __name__ == "__main__":
    # python manageh5.py dbfilepath

    printlog(split_mask('/hellp/kdd/t'))
    '''
    printlog(sys.argv)
    if len(sys.argv)==2:     
        
        arg_strs = sys.argv[1:]
        arg_strs = ''.join(arg_strs)
        #print kwargs    
        print_structure_h5db2(arg_strs)
        #print_structure_h5db(arg_strs)
    #sys.exit ( "End of import" )
    '''
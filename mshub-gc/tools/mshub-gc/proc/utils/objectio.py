# -*- coding: utf-8 -*-
"""
Created on Tue May 09 18:57:21 2017

@author: Dr. Ivan Laponogov

"""

import os;
import sys;

if __name__=='__main__':
    if sys.byteorder!='little':
        print('Only little endian machines currently supported! bye bye ....');
        quit();
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')));


import h5py;

import numpy as np;

try:
    import scipy.sparse as sp;
    scipy_sparse_available = True;
    from proc.utils.scipy_handler import scipy_add_methods;
except:
    scipy_sparse_available = False;


from proc.utils.exceptions import EmptyWorkGroup, UnknownClassID, UnSupportedObject, ClassNotFound, NoNewMethodforClass, HDF5UtilsGroupError;
from proc.utils.numpy_handler import numpy_add_methods;


python_version = sys.version_info.major;
if python_version == 3:
    from io import IOBase

class ObjectGroup(object):
    
    def __init_containers(self):
        #object lists
        self.ids = [];
        self.strings = [];
        self.ints = [];
        self.uints = [];
        self.floats = [];
        self.ndarrays = [];
        self.bools = [];
        self.generic_objects = set();
        self.object_ids = [];
        self.datasets = [];

        #add new here
    
    def __init__(self):
        #class management
        
        self.class_savers={};
        self.class_loaders={};
        self.class_data=[];
        self.class_ids={};
        self.class_ids[0] = 'general class'
        self.supported_classes = set();
        self.registered_classes = {};
        
        self.__general_id=0;
        self.class_loaders[self.__general_id] = self.__general_class_instance_loader;

        self.__list_id=1;
        self.class_data.append([list, 'list', self.__list_id, self.__load_list, self.__save_list]);

        self.__dict_id=2;
        self.class_data.append([dict, 'dict', self.__dict_id, self.__load_dict, self.__save_dict]);

        self.__set_id=3;
        self.class_data.append([set, 'set', self.__set_id, self.__load_set, self.__save_set]);

        self.__tuple_id=4;
        self.class_data.append([tuple, 'tuple', self.__tuple_id, self.__load_tuple, self.__save_tuple]);

        self.__int_id=5;
        self.class_data.append([int, 'int', self.__int_id, self.__load_int, self.__save_int]);

        self.__str_id=6;
        self.class_data.append([str, 'str', self.__str_id, self.__load_str, self.__save_str]);

        self.__float_id=7;
        self.class_data.append([float, 'float', self.__float_id, self.__load_float, self.__save_float]);

        self.__ndarray_id=8;
        self.class_data.append([np.ndarray, 'ndarray', self.__ndarray_id, self.__load_ndarray, self.__save_ndarray]);

        self.__none_id=9;
        self.class_data.append([None.__class__, 'NoneType', self.__none_id, self.__load_none, self.__save_none]);

        self.__bool_id=10;
        self.class_data.append([bool, 'bool', self.__bool_id, self.__load_bool, self.__save_bool]);

        self.__dataset_id=11;
        self.class_data.append([h5py.Dataset, 'Dataset', self.__dataset_id, self.__load_dataset, self.__save_dataset]);

        
        self.__complex_id=12;
        self.class_data.append([complex, 'complex', self.__complex_id, self.__load_complex, self.__save_complex]);
        
        if python_version == 2:
            self.__long_id=13;
            self.class_data.append([long, 'long', self.__long_id, self.__load_long, self.__save_long]);
            
        
        numpy_add_methods(self);
        
        if scipy_sparse_available:
            scipy_add_methods(self);
        

        for i in self.class_data:
            self.supported_classes.add(i[1]);
            self.class_loaders[i[2]] = i[3];
            self.class_savers[i[0]] = i[4];
            self.class_ids[i[0]] = i[2];


    
    def __repr__(self):
        return '\n'.join((
        'WorkGroup object:',
        'IDs: ',
        str(self.ids),
        'Ints: ',
        str(self.ints),
        'Strings: ',
        str(self.strings),
        'Floats:',
        str(self.floats),
        'NDArrays: ',
        str(self.ndarrays),
        'Booleans: ',
        str(self.bools),
        'Generic_objects: ',
        str(self.generic_objects),
        'Object IDs: ',
        str(self.object_ids)
        ));
        
        
    def _recursive_reconstructor(self):
        self.id_index += 1;
        w_id = self.ids[self.id_index];
        self.object_id_index += 1;
        object_id = self.object_ids[self.object_id_index];

        if object_id in self.restored_objects:
            return self.restored_objects[object_id];

        if w_id in self.class_loaders:
            result = self.class_loaders[w_id](object_id); 
            return result
        else:
            raise UnknownClassID('ID %s for class type is not supported! Internal Error!')

    def _pickle_object(self, obj):
        if hasattr(obj,'__call__'):
            raise UnSupportedObject('Error! Variables referencing functions currently not supported! %s'%obj)
        
        if python_version == 2:
            if isinstance(obj, file):
                raise UnSupportedObject('Error! File objects currently not supported! %s'%obj)
        else:
            if isinstance(obj, IOBase):
                raise UnSupportedObject('Error! File objects currently not supported! %s'%obj)
            
        
        if isinstance(obj, h5py.File):
            raise UnSupportedObject('Error! HDF5 file objects as/inside object being saved currently not supported! %s'%obj)
    
        if isinstance(obj, h5py.Group):
            raise UnSupportedObject('Error! HDF5 group objects as/inside object being saved currently not supported! %s'%obj)
        
        if hasattr(obj,'__class__'):
    
            object_id = id(obj);
            self.object_ids.append(object_id);
            
            obj_type = obj.__class__;
            
            if obj_type in self.class_ids:
                obj_class_id = self.class_ids[obj_type];
            else:
                obj_class_id = 0;
                
            self.ids.append(obj_class_id);
            
            if not (object_id in self.generic_objects):
                self.generic_objects.add(object_id);    
            
                if obj_type in self.class_savers:
                    obj_saver = self.class_savers[obj_type];
                else:
                    obj_saver = self.__general_class_instance_saver;
        
                obj_saver(obj)    
        
        else:
            raise UnSupportedObject('Error! Unsupported object: %s'%obj);


    def register_classes(self, classes):
        for i in classes:
            self.registered_classes[i.__name__]=i;
        
#-------------------------------------------------------


    def __general_class_instance_loader(self, object_id):
        
        self.string_index += 1;
        class_name = self.strings[self.string_index];
        
        if class_name in self.registered_classes:
            class_obj = self.registered_classes[class_name];
        elif class_name in globals():
            class_obj = globals()[class_name];
        else:
            raise ClassNotFound('Class %s not found in global namespace! Cannot reconstruct class instance!'%class_name);
    
        if hasattr(class_obj,'__new__'):  #Check this behavior
            obj = class_obj.__new__(class_obj);
        else:
            raise NoNewMethodforClass('Class %s has no __new__ method defined! Derive it from "object" class at least!')
            
        self.restored_objects[object_id] = obj;
        
        if hasattr(obj, '__from_hdf5_dictionary__'):
            obj.__from_hdf5_dictionary__(self._recursive_reconstructor())
        else:
            obj.__dict__ = self._recursive_reconstructor()
    
        return obj
        
    
    
        
    def __general_class_instance_saver(self, obj):
        if hasattr(obj,'__to_hdf5_dictionary__'):
            self.strings.append(obj.__class__.__name__)
            self._pickle_object(obj.__to_hdf5_dictionary__());
        elif hasattr(obj,'__dict__'):
            self.strings.append(obj.__class__.__name__)
            self._pickle_object(obj.__dict__);
        else:
            raise UnSupportedObject('Error! Object %s has no __dict__ defined! This is needed for arbitrary object type storage!'%obj)
    
    
    #--------------------------------------------------------------------------
    #list
    def __load_list(self, object_id):
        result = [];
        self.restored_objects[object_id] = result;
        self.int_index += 1;
        count = self.ints[self.int_index];
        for i in range(count):
            result.append(self._recursive_reconstructor());
        return result;
    
    def __save_list(self, obj):
        self.ints.append(len(obj));
        for v in obj:
            self._pickle_object(v);
    #--------------------------------------------------------------------------
    #dict
    def __load_dict(self, object_id):
        result = {};
        self.restored_objects[object_id] = result;
        self.int_index += 1;
        count = self.ints[self.int_index];
        for i in range(count):
            key = self._recursive_reconstructor();
            value = self._recursive_reconstructor();
            result[key] = value;
        return result;
    
    
    def __save_dict(self, obj):
        self.ints.append(len(obj));
        for key in obj.keys():
            self._pickle_object(key);
            self._pickle_object(obj[key]);
    #--------------------------------------------------------------------------
    #set
    def __load_set(self, object_id):
        result = set();
        self.restored_objects[object_id] = result;
        self.int_index += 1;
        count = self.ints[self.int_index];
        for i in range(count):
            result.add(self._recursive_reconstructor());
        return result;
    
    def __save_set(self, obj):
        self.ints.append(len(obj));
        for i in obj:
            self._pickle_object(i);
    #--------------------------------------------------------------------------
    #tuple
    def __load_tuple(self, object_id):
        result = [];
        self.int_index += 1;
        count = self.ints[self.int_index];
        for i in range(count):
            result.append(self._recursive_reconstructor());
        result = tuple(result);
        self.restored_objects[object_id] = result;    
        return result;
    
    def __save_tuple(self, obj):
        self.ints.append(len(obj));
        for v in obj:
            self._pickle_object(v);
    #--------------------------------------------------------------------------
    #int
    def __load_int(self, object_id):
        self.int_index += 1;
        result = int(self.ints[self.int_index])
        self.restored_objects[object_id] = result;
        return result;
    
    def __save_int(self, obj):
        self.ints.append(obj);

    #--------------------------------------------------------------------------
    #long for python 2
    def __load_long(self, object_id):
        self.int_index += 1;
        if python_version == 2:
            result = long(self.ints[self.int_index])
        else:
            result = int(self.ints[self.int_index])
        self.restored_objects[object_id] = result;
        return result;
    
    def __save_long(self, obj):
        self.ints.append(obj);

    #--------------------------------------------------------------------------
    #str
    def __load_str(self, object_id):
        self.string_index += 1;
        result = self.strings[self.string_index];
        self.restored_objects[object_id] = result;
        return result
    
    def __save_str(self, obj):
        self.strings.append(obj);
    #--------------------------------------------------------------------------
    #float
    def __load_float(self, object_id):
        self.float_index +=1;
        result = self.floats[self.float_index];
        self.restored_objects[object_id] = result;    
        return result
    
    def __save_float(self, obj):
        self.floats.append(obj);


    #--------------------------------------------------------------------------
    #complex
    def __load_complex(self, object_id):
        self.float_index += 1;
        re = self.floats[self.float_index];
        self.float_index += 1;
        im = self.floats[self.float_index];
        result = complex(re,im);
        self.restored_objects[object_id] = result;
        return result;
    
    def __save_complex(self, obj):
        self.floats.append(obj.real);
        self.floats.append(obj.imag);

    
    #--------------------------------------------------------------------------
    #NumPy array
    def __load_ndarray(self, object_id):
        self.ndarray_index += 1;
        result = self.ndarrays[self.ndarray_index]
        self.restored_objects[object_id] = result;    
        return result;
    
    def __save_ndarray(self, obj):
        self.ndarrays.append(obj);
    #--------------------------------------------------------------------------
    #None
    def __load_none(self, object_id):
        return None
    
    def __save_none(self, obj):
        pass
    #--------------------------------------------------------------------------
    #Boolean
    def __load_bool(self, object_id):
        self.bool_index += 1;
        result = self.bools[self.bool_index]
        self.restored_objects[object_id] = result;    
        return result;
    
    def __save_bool(self, obj):
        self.bools.append(obj);
    #--------------------------------------------------------------------------
    #HDF5 dataset
    def __load_dataset(self, object_id):
        self.dataset_index += 1;
        result = self.datasets[self.dataset_index]
        self.restored_objects[object_id] = result;    
        return result
    
    def __save_dataset(self, obj):
        self.datasets.append(obj);
    
    #------------------------------------------------------------------------------------------
    
    def store_object(self, obj):
        self.__init_containers();
        self._pickle_object(obj);
        
    def reconstruct_object(self):
        if self.ids:
            self.restored_objects = {};
            self.id_index = -1;
            self.string_index = -1;
            self.int_index = -1;
            self.uint_index = -1;
            self.float_index = -1;
            self.ndarray_index = -1;
            self.bool_index = -1;
            self.object_id_index = -1;
            self.dataset_index = -1;
            #add reset to other counters here.
            

            return self._recursive_reconstructor();
        else:
            raise EmptyWorkGroup('Empty workgroup! Workgroup does not contain any object!');
        
    @staticmethod    
    def string_to_byte_array(s):
        if python_version == 2:                                  
            '''            
            print(s)
            s=s.encode('utf-8');
            print(s)
            s=bytearray(s)
            print(s)
            s = np.array(s)
            print(s)
            
            return s
            '''
            return np.array(bytearray(s.encode('utf-8')));
        else:
            return np.array(list(bytes(s.encode('utf-8'))));
        
    @staticmethod    
    def byte_array_to_string(byte_array):
        if python_version == 2:   
            '''print(byte_array)                               
            byte_array = bytearray(byte_array)
            print(byte_array)
            s = str(byte_array)
            print(s)
            return s
            '''
            return str(bytearray(byte_array.tolist()));
        else:
            return str(bytes(list(byte_array)).decode('utf-8'));


    def read_from_hdf5_group(self, work_group):
        self.ids = np.array(work_group['ids']).tolist();
        self.ints = np.array(work_group['ints']);
        self.uints = np.array(work_group['uints']);
            
        self.floats = np.array(work_group['floats']).tolist();
        self.bools = np.array(work_group['bools']).tolist();
        self.object_ids = np.array(work_group['object_ids']).tolist();
        
        self.ndarrays = [];
        nd_count = work_group.attrs['nd_arrays'];
        for i in range(nd_count):
            self.ndarrays.append(np.array(work_group['nd_arrays_group/nd_%s'%i]))
        
        self.strings = [];
        
        
        str_indexes_dataset = work_group['str_indexes'];
        str_bytes_dataset = work_group['str_bytes'];
        
        
        for i in range(len(str_indexes_dataset)):
            i0 = str_indexes_dataset[i, 0];
            i1 = str_indexes_dataset[i, 1];
            
            self.strings.append(ObjectGroup.byte_array_to_string(str_bytes_dataset[i0:i1]))
        
        self.datasets = [];
        data_start = work_group.attrs['data_path_string_start'];
        data_count = work_group.attrs['data_paths_count'];
        
        hdf5file = work_group.file;        
        for i in range(data_start, data_start+data_count):
            self.datasets.append(hdf5file[self.strings[i]])

    
    def write_to_hdf5_group(self, work_group):
        work_group.create_dataset('ids', data = np.array(self.ids, dtype = np.uint16), chunks = True, compression = "gzip")
        work_group.create_dataset('ints', data = np.array(self.ints, dtype = np.int64), chunks = True, compression = "gzip")
        work_group.create_dataset('uints', data = np.array(self.uints, dtype = np.uint64), chunks = True, compression = "gzip")
        work_group.create_dataset('floats', data = np.array(self.floats, dtype = np.float64), chunks = True, compression = "gzip")
        work_group.create_dataset('bools', data = np.array(self.bools, dtype = np.bool), chunks = True, compression = "gzip")
        work_group.create_dataset('object_ids', data = np.array(self.object_ids, dtype = np.uint64), chunks = True, compression = "gzip")
        
        work_group.attrs['nd_arrays']=len(self.ndarrays);
        nd_group = work_group.create_group('nd_arrays_group');
        for i in range(len(self.ndarrays)):
            nd_group.create_dataset('nd_%s'%i, data = self.ndarrays[i], chunks = True, compression = "gzip")
        
        work_group.attrs['data_path_string_start'] = len(self.strings);
        work_group.attrs['data_paths_count'] = len(self.datasets);

        for dataset in self.datasets:
            data_path = dataset.name;
            if dataset.file != work_group.file:
                copyset = work_group.file.create_dataset(data_path, data = dataset);
                for attr in dataset.attrs:
                    copyset.attrs[attr] = dataset.attrs[attr];
                
            self.strings.append(data_path);
        
        
        strbytes = [];

        for s in self.strings:
            strbytes.append(ObjectGroup.string_to_byte_array(s));

        total_len = 0;        
        for s in strbytes:
            total_len += len(s)
            
        str_indexes_dataset = work_group.create_dataset('str_indexes', (len(strbytes), 2), dtype = np.uint32, chunks = True, compression = "gzip");
        str_bytes_dataset = work_group.create_dataset('str_bytes', (total_len, ), dtype = np.uint8, chunks = True, compression = "gzip");
        
        index = 0;
        for i in range(len(strbytes)):
            value = strbytes[i];
            str_bytes_dataset[index:index+len(value)] = value[:];
            str_indexes_dataset[i, 0] = index;
            index += len(value);
            str_indexes_dataset[i, 1] = index;






def store_to_hdf5(obj, h5file, subpath, allow_overwrite = False):
    """
    ** Write object into HDF5 **
    Args:

        obj - object to be stored

        h5file - opened hdf5 file in mode allowing writing

        subpath - path to the group to store the object
        
        allow_overwrite - allows to write to the group already storing anothe
        object, replacing it. Default - False

    Returns:
        None
    
    """
    if subpath in h5file:
        if allow_overwrite:
            del h5file[subpath]
        else:
            raise HDF5UtilsGroupError('Subpath %s already exists! Set allow_overwrite to True to overwrite.'%subpath)
            
    work_group = h5file.create_group(subpath);
    work_group.attrs['GroupPurpose']=1;
    
    object_group = ObjectGroup();
    object_group.store_object(obj);
    object_group.write_to_hdf5_group(work_group)
    
    
def restore_from_hdf5(h5file, subpath, run_init = False, classes_to_register = []):
    """
    ** Write object into HDF5 **
    Args:

        h5file - opened hdf5 file in mode allowing reading

        subpath - path to the group of the stored object
        
        run_init - run default constructor for the loaded object. 
        Default - False

    Returns:
        object read from HDF5
    
    """
    work_group=h5file[subpath];

    if not ('GroupPurpose' in work_group.attrs):
        raise HDF5UtilsGroupError('Subpath %s does not refer to the object storing group!'%subpath)
    
    if work_group.attrs['GroupPurpose'] != 1:
        raise HDF5UtilsGroupError('Subpath %s does not refer to the object storing group!'%subpath)
        
    object_group = ObjectGroup();
    object_group.register_classes(classes_to_register);
    object_group.read_from_hdf5_group(work_group);
    obj = object_group.reconstruct_object();

    return obj


    
    
# -*- coding: utf-8 -*-
"""
Created on Sun May 14 15:02:58 2017

@author: Dr. Ivan Laponogov
"""

import numpy as np;
import numpy.ma as ma;
from types import MethodType;


def __load_int8(self, object_id):
    self.int_index += 1;
    result = np.int8(self.ints[self.int_index]);
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_int8(self, obj):
    self.ints.append(obj);



def __load_int16(self, object_id):
    self.int_index += 1;
    result = np.int16(self.ints[self.int_index]);
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_int16(self, obj):
    self.ints.append(obj);



def __load_int32(self, object_id):
    self.int_index += 1;
    result = np.int32(self.ints[self.int_index]);
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_int32(self, obj):
    self.ints.append(obj);



def __load_int64(self, object_id):
    self.int_index += 1;
    result = np.int64(self.ints[self.int_index]);
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_int64(self, obj):
    self.ints.append(obj);



def __load_uint8(self, object_id):
    self.uint_index += 1;
    result = np.uint8(self.uints[self.uint_index]);
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_uint8(self, obj):
    self.uints.append(obj);



def __load_uint16(self, object_id):
    self.uint_index += 1;
    result = np.uint16(self.uints[self.uint_index]);
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_uint16(self, obj):
    self.uints.append(obj);
    
    
def __load_uint32(self, object_id):
    self.uint_index += 1;
    result = np.uint32(self.uints[self.uint_index]);
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_uint32(self, obj):
    self.uints.append(obj);
    

def __load_uint64(self, object_id):
    self.uint_index += 1;
    result = np.uint64(self.uints[self.uint_index]);
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_uint64(self, obj):
    self.uints.append(obj);

#------------------------

def __load_float16(self, object_id):
    self.float_index += 1;
    result = np.float16(self.floats[self.float_index]);
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_float16(self, obj):
    self.floats.append(obj);

def __load_float32(self, object_id):
    self.float_index += 1;
    result = np.float32(self.floats[self.float_index]);
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_float32(self, obj):
    self.floats.append(obj);

def __load_float64(self, object_id):
    self.float_index += 1;
    result = np.float64(self.floats[self.float_index]);
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_float64(self, obj):
    self.floats.append(obj);

def __load_complex64(self, object_id):
    self.float_index += 1;
    re = self.floats[self.float_index];
    self.float_index += 1;
    im = self.floats[self.float_index];
    result = np.complex64(re+im*1j);
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_complex64(self, obj):
    self.floats.append(obj.real);
    self.floats.append(obj.imag);


def __load_complex128(self, object_id):
    self.float_index += 1;
    re = self.floats[self.float_index];
    self.float_index += 1;
    im = self.floats[self.float_index];
    result = np.complex128(re+im*1j);
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_complex128(self, obj):
    self.floats.append(obj.real);
    self.floats.append(obj.imag);


def __load_bool_(self, object_id):
    self.bool_index += 1;
    result = np.bool_(self.bools[self.bool_index]);
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_bool_(self, obj):
    self.bools.append(obj);

def __load_float_(self, object_id):
    self.float_index += 1;
    result = np.float_(self.floats[self.float_index]);
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_float_(self, obj):
    self.floats.append(obj);

def __load_int_(self, object_id):
    self.int_index += 1;
    result = np.int_(self.ints[self.int_index]);
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_int_(self, obj):
    self.ints.append(obj);

def __load_matrix(self, object_id):
    self.ndarray_index += 1;
    result = np.matrix(self.ndarrays[self.ndarray_index]);
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_matrix(self, obj):
    self.ndarrays.append(obj);



def __load_masked_array(self, object_id):
    data = self._recursive_reconstructor();
    mask = self._recursive_reconstructor();
    fill_value = self._recursive_reconstructor();
    hardmask = self._recursive_reconstructor();
    
    result = ma.masked_array(data = data, mask = mask, fill_value = fill_value);
    
    if result.hardmask!=hardmask:
        if hardmask:
            result.harden_mask();
        else:
            result.soften_mask();
    
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_masked_array(self, obj):
    self._pickle_object(obj.data);
    self._pickle_object(obj.mask);
    self._pickle_object(obj.fill_value);
    self._pickle_object(obj.hardmask);

#-------------------------------


def numpy_add_methods(object_group):
    
    object_group.__int8_id   = 1001;
    object_group.__int16_id  = 1002;
    object_group.__int32_id  = 1003;
    object_group.__int64_id  = 1004;
    object_group.__uint8_id  = 1005;
    object_group.__uint16_id = 1006;
    object_group.__uint32_id = 1007;
    object_group.__uint64_id = 1008;

    object_group.__float16_id    = 1009;
    object_group.__float32_id    = 1010;
    object_group.__float64_id    = 1011;
    
    object_group.__complex64_id  = 1012;
    object_group.__complex128_id = 1013;
    
    object_group.__float__id     = 1014;
    object_group.__int__id       = 1015;
    object_group.__bool__id      = 1016;

    object_group.__matrix_id      = 1017;

    object_group.__masked_array_id      = 1018;
    

    object_group.__load_int8   = MethodType(__load_int8,   object_group);
    object_group.__load_int16  = MethodType(__load_int16,  object_group);
    object_group.__load_int32  = MethodType(__load_int32,  object_group);
    object_group.__load_int64  = MethodType(__load_int64,  object_group);
    object_group.__load_uint8  = MethodType(__load_uint8,  object_group);
    object_group.__load_uint16 = MethodType(__load_uint16, object_group);
    object_group.__load_uint32 = MethodType(__load_uint32, object_group);
    object_group.__load_uint64 = MethodType(__load_uint64, object_group);

    object_group.__load_float16 = MethodType(__load_float16, object_group);
    object_group.__load_float32 = MethodType(__load_float32, object_group);
    object_group.__load_float64 = MethodType(__load_float64, object_group);

    object_group.__load_complex64  = MethodType(__load_complex64,  object_group);
    object_group.__load_complex128 = MethodType(__load_complex128, object_group);

    object_group.__load_int_   = MethodType(__load_int_,   object_group);
    object_group.__load_float_ = MethodType(__load_float_, object_group);
    object_group.__load_bool_  = MethodType(__load_bool_,  object_group);

    object_group.__load_matrix  = MethodType(__load_matrix,  object_group);
    
    object_group.__load_masked_array  = MethodType(__load_masked_array,  object_group);


    object_group.__save_int8   = MethodType(__save_int8,   object_group);
    object_group.__save_int16  = MethodType(__save_int16,  object_group);
    object_group.__save_int32  = MethodType(__save_int32,  object_group);
    object_group.__save_int64  = MethodType(__save_int64,  object_group);
    object_group.__save_uint8  = MethodType(__save_uint8,  object_group);
    object_group.__save_uint16 = MethodType(__save_uint16, object_group);
    object_group.__save_uint32 = MethodType(__save_uint32, object_group);
    object_group.__save_uint64 = MethodType(__save_uint64, object_group);
    
    
    object_group.__save_float16 = MethodType(__save_float16, object_group);
    object_group.__save_float32 = MethodType(__save_float32, object_group);
    object_group.__save_float64 = MethodType(__save_float64, object_group);

    object_group.__save_complex64  = MethodType(__save_complex64,  object_group);
    object_group.__save_complex128 = MethodType(__save_complex128, object_group);

    object_group.__save_int_   = MethodType(__save_int_,   object_group);
    object_group.__save_float_ = MethodType(__save_float_, object_group);
    object_group.__save_bool_  = MethodType(__save_bool_,  object_group);

    object_group.__save_matrix  = MethodType(__save_matrix,  object_group);
    
    object_group.__save_masked_array  = MethodType(__save_masked_array,  object_group);
    
    
    object_group.class_data.append([np.int8,   'int8',   object_group.__int8_id,   object_group.__load_int8,   object_group.__save_int8  ]);
    object_group.class_data.append([np.int16,  'int16',  object_group.__int16_id,  object_group.__load_int16,  object_group.__save_int16 ]);
    object_group.class_data.append([np.int32,  'int32',  object_group.__int32_id,  object_group.__load_int32,  object_group.__save_int32 ]);
    object_group.class_data.append([np.int64,  'int64',  object_group.__int64_id,  object_group.__load_int64,  object_group.__save_int64 ]);
    object_group.class_data.append([np.uint8,  'uint8',  object_group.__uint8_id,  object_group.__load_uint8,  object_group.__save_uint8 ]);
    object_group.class_data.append([np.uint16, 'uint16', object_group.__uint16_id, object_group.__load_uint16, object_group.__save_uint16]);
    object_group.class_data.append([np.uint32, 'uint32', object_group.__uint32_id, object_group.__load_uint32, object_group.__save_uint32]);
    object_group.class_data.append([np.uint64, 'uint64', object_group.__uint64_id, object_group.__load_uint64, object_group.__save_uint64]);      
    
    object_group.class_data.append([np.float16, 'float16', object_group.__float16_id, object_group.__load_float16, object_group.__save_float16]);      
    object_group.class_data.append([np.float32, 'float32', object_group.__float32_id, object_group.__load_float32, object_group.__save_float32]);      
    object_group.class_data.append([np.float64, 'float64', object_group.__float64_id, object_group.__load_float64, object_group.__save_float64]);      
    
    object_group.class_data.append([np.complex64,  'complex64',  object_group.__complex64_id,  object_group.__load_complex64,  object_group.__save_complex64 ]);      
    object_group.class_data.append([np.complex128, 'complex128', object_group.__complex128_id, object_group.__load_complex128, object_group.__save_complex128]);      
    
    object_group.class_data.append([np.int_,   'int_',   object_group.__int__id,   object_group.__load_int_,   object_group.__save_int_  ]);      
    object_group.class_data.append([np.float_, 'float_', object_group.__float__id, object_group.__load_float_, object_group.__save_float_]);      
    object_group.class_data.append([np.bool_,  'bool_',  object_group.__bool__id,  object_group.__load_bool_,  object_group.__save_bool_ ]);      

    object_group.class_data.append([np.matrix,  'matrix',  object_group.__matrix_id,  object_group.__load_matrix,  object_group.__save_matrix ]);      
    
    object_group.class_data.append([ma.MaskedArray,  'MaskedArray',  object_group.__masked_array_id,  object_group.__load_masked_array,  object_group.__save_masked_array ]);      
    

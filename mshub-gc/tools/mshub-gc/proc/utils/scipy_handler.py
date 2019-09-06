# -*- coding: utf-8 -*-
"""
Created on Sun May 14 15:02:34 2017

@author: Dr. Ivan Laponogov
"""

import scipy.sparse as sp;

from types import MethodType;


def __load_bsr_matrix(self, object_id):
    self.int_index += 1;
    a = self.ints[self.int_index];
    self.int_index += 1;
    b = self.ints[self.int_index];

    shape = (a, b);
    
    data = self._recursive_reconstructor();
    indices = self._recursive_reconstructor();
    indptr = self._recursive_reconstructor();

    self.int_index += 1;
    a = self.ints[self.int_index];
    self.int_index += 1;
    b = self.ints[self.int_index];
    
    blocksize = (a, b);
    
    result = sp.bsr_matrix((data, indices, indptr), shape = shape, blocksize = blocksize);
    
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_bsr_matrix(self, obj):
    self.ints.append(obj.shape[0]);
    self.ints.append(obj.shape[1]);
    self._pickle_object(obj.data);
    self._pickle_object(obj.indices);
    self._pickle_object(obj.indptr);
    self.ints.append(obj.blocksize[0]);
    self.ints.append(obj.blocksize[1]);


def __load_coo_matrix(self, object_id):
    self.int_index += 1;
    a = self.ints[self.int_index];
    self.int_index += 1;
    b = self.ints[self.int_index];

    shape = (a, b);
    
    data = self._recursive_reconstructor();
    row = self._recursive_reconstructor();
    col = self._recursive_reconstructor();

    result = sp.coo_matrix((data, (row, col)), shape = shape);
    
    self.restored_objects[object_id] = result;
    return result;    

def __save_coo_matrix(self, obj):
    self.ints.append(obj.shape[0]);
    self.ints.append(obj.shape[1]);
    self._pickle_object(obj.data);
    self._pickle_object(obj.row);
    self._pickle_object(obj.col);
    


def __load_csc_matrix(self, object_id):
    self.int_index += 1;
    a = self.ints[self.int_index];
    self.int_index += 1;
    b = self.ints[self.int_index];

    shape = (a, b);
    
    data = self._recursive_reconstructor();
    indices = self._recursive_reconstructor();
    indptr = self._recursive_reconstructor();

    result = sp.csc_matrix((data, indices, indptr), shape = shape);
    
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_csc_matrix(self, obj):
    self.ints.append(obj.shape[0]);
    self.ints.append(obj.shape[1]);
    self._pickle_object(obj.data);
    self._pickle_object(obj.indices);
    self._pickle_object(obj.indptr);
    

def __load_csr_matrix(self, object_id):
    self.int_index += 1;
    a = self.ints[self.int_index];
    self.int_index += 1;
    b = self.ints[self.int_index];

    shape = (a, b);
    
    data = self._recursive_reconstructor();
    indices = self._recursive_reconstructor();
    indptr = self._recursive_reconstructor();

    result = sp.csr_matrix((data, indices, indptr), shape = shape);
    
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_csr_matrix(self, obj):
    self.ints.append(obj.shape[0]);
    self.ints.append(obj.shape[1]);
    self._pickle_object(obj.data);
    self._pickle_object(obj.indices);
    self._pickle_object(obj.indptr);



def __load_dia_matrix(self, object_id):
    self.int_index += 1;
    a = self.ints[self.int_index];
    self.int_index += 1;
    b = self.ints[self.int_index];

    shape = (a, b);
    
    data = self._recursive_reconstructor();
    offsets = self._recursive_reconstructor();
    
    result = sp.dia_matrix((data, offsets), shape = shape);
    
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_dia_matrix(self, obj):
    self.ints.append(obj.shape[0]);
    self.ints.append(obj.shape[1]);
    self._pickle_object(obj.data);
    self._pickle_object(obj.offsets);
    

def __load_dok_matrix(self, object_id):
    data = self._recursive_reconstructor();
    result = sp.dok_matrix(data);
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_dok_matrix(self, obj):
    data = sp.coo_matrix(obj);
    self._pickle_object(data);

def __load_lil_matrix(self, object_id):
    data = self._recursive_reconstructor();
    result = sp.lil_matrix(data);
    self.restored_objects[object_id] = result;
    return result;    
    
def __save_lil_matrix(self, obj):
    data = sp.coo_matrix(obj);
    self._pickle_object(data);
    

    

def scipy_add_methods(object_group):

    object_group.__bsr_matrix_id   = 2001;
    object_group.__coo_matrix_id  = 2002;
    object_group.__csc_matrix_id  = 2003;
    object_group.__csr_matrix_id  = 2004;
    object_group.__dia_matrix_id  = 2005;
    object_group.__dok_matrix_id = 2006;
    object_group.__lil_matrix_id = 2007;
    
    object_group.__load_bsr_matrix   = MethodType(__load_bsr_matrix,   object_group);
    object_group.__load_coo_matrix   = MethodType(__load_coo_matrix,   object_group);
    object_group.__load_csc_matrix   = MethodType(__load_csc_matrix,   object_group);
    object_group.__load_csr_matrix   = MethodType(__load_csr_matrix,   object_group);
    object_group.__load_dia_matrix   = MethodType(__load_dia_matrix,   object_group);
    object_group.__load_dok_matrix   = MethodType(__load_dok_matrix,   object_group);
    object_group.__load_lil_matrix   = MethodType(__load_lil_matrix,   object_group);
    
    object_group.__save_bsr_matrix   = MethodType(__save_bsr_matrix,   object_group);
    object_group.__save_coo_matrix   = MethodType(__save_coo_matrix,   object_group);
    object_group.__save_csc_matrix   = MethodType(__save_csc_matrix,   object_group);
    object_group.__save_csr_matrix   = MethodType(__save_csr_matrix,   object_group);
    object_group.__save_dia_matrix   = MethodType(__save_dia_matrix,   object_group);
    object_group.__save_dok_matrix   = MethodType(__save_dok_matrix,   object_group);
    object_group.__save_lil_matrix   = MethodType(__save_lil_matrix,   object_group);

    object_group.class_data.append([sp.bsr_matrix,   'bsr_matrix',   object_group.__bsr_matrix_id,   object_group.__load_bsr_matrix,   object_group.__save_bsr_matrix  ]);
    object_group.class_data.append([sp.coo_matrix,   'coo_matrix',   object_group.__coo_matrix_id,   object_group.__load_coo_matrix,   object_group.__save_coo_matrix  ]);
    object_group.class_data.append([sp.csc_matrix,   'csc_matrix',   object_group.__csc_matrix_id,   object_group.__load_csc_matrix,   object_group.__save_csc_matrix  ]);
    object_group.class_data.append([sp.csr_matrix,   'csr_matrix',   object_group.__csr_matrix_id,   object_group.__load_csr_matrix,   object_group.__save_csr_matrix  ]);
    object_group.class_data.append([sp.dia_matrix,   'dia_matrix',   object_group.__dia_matrix_id,   object_group.__load_dia_matrix,   object_group.__save_dia_matrix  ]);
    object_group.class_data.append([sp.dok_matrix,   'dok_matrix',   object_group.__dok_matrix_id,   object_group.__load_dok_matrix,   object_group.__save_dok_matrix  ]);
    object_group.class_data.append([sp.lil_matrix,   'lil_matrix',   object_group.__lil_matrix_id,   object_group.__load_lil_matrix,   object_group.__save_lil_matrix  ]);
    
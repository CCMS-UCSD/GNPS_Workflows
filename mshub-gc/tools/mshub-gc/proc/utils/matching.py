# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 15:30:51 2017

@author: Dr. Ivan Laponogov
"""

import numpy as np;

def condense_with_tolerance(vector, delta):
    """
    Condenses the 1D array of elements (sorted) if two or more entries are 
    within delta distance from each other.
    
    Returns condensed 1D array
    
    """
    
    differences = np.diff(vector);
    
    mask = differences <= delta;
    
    mask1 = np.insert(mask, 0, False);
    mask2 = np.append(mask, False);

    singlemask = np.logical_not(np.logical_or(mask1, mask2));

    endmask = np.logical_and(mask1, np.logical_not(mask2));
    startmask = np.logical_and(mask2, np.logical_not(mask1));

    idc1 = np.nonzero(startmask)[0];
    idc2 = np.nonzero(endmask)[0];

    result = vector[singlemask];

    means = np.zeros(idc1.shape, dtype = np.float64);

    for i in range(idc1.shape[0]):
        means[i] = np.mean(vector[idc1[i]:idc2[i]] + 1);


    result = np.hstack([result, means]);
    
    return np.sort(result);

        

def match_lists(list1, list2, return_inverse = False):
    """
    Matching of two lists.
    
    Args:
        list1, list2  - two lists to be matched
        return_inverse - return inverse conversion indeces or not, default = False
        
    Returns:
        indeces1 - array of conversion indeces (dtype = np.int64) 
                      from list1 to list2, i.e. for i in range(len(list1))
                      list1[i] is matched to list2[indeces1[i]],
                      indeces1 has same size as list1
                      "-1" numerical value in indeces1[i] indicates no match
        
        indeces2 - (optional) array of inverse conversion indeces 
                      (dtype = np.int64) i.e. for i in range(len(list2))
                      list2[i] is matched to list1[indeces2[i]],
                      indeces2 has same size as list2
                      "-1" numerical value in indeces2[i] indicates no match
    
    """
    indeces1 = [];
    for s in list1:
        try:
            #for each element in list1 try to find corresponding index 
            #in list2
            indeces1.append(list2.index(s));
        except:
            #if none found - set index to -1
            indeces1.append(-1);
    
    #convert to numpy array
    indeces1 = np.array(indeces1, dtype = np.int64);

    if return_inverse:
        #prepare output array indeces2 pre-filled with -1 for no matches
        indeces2 = np.full((len(list2), ), -1, dtype = np.int64);
        #get mask of matched indeces
        list1_mask = indeces1 >= 0;
        #get indeces of matches
        list1_indcs = np.arange(len(list1), dtype = np.int64);
        #assign them to inverse indeces
        indeces2[indeces1[list1_mask]] = list1_indcs[list1_mask];
        return indeces1, indeces2;
    else:
        return indeces1

def nn_match(rt, crt, tolerance = 0.1001, return_inverse = False):
    """
    Recursive matching of two 1D NumPy arrays of values with given tolerance.
    
    Args:
        rt, crt - two 1D NumPy arrays to be matched
        tolerance - allowed matching distance between values, default = 0.1001
        return_inverse - return inverse conversion indeces or not, default = False
        
    Returns:
        rt2crtindcs - array of conversion indeces (dtype = np.int64) 
                      from rt to crt, i.e. for i in range(rt.shape[0])
                      rt[i] is matched to crt[rt2crtindcs[i]],
                      rt2crtindcs has same size as rt
                      "-1" numerical value in rt2crtindcs[i] indicates no match
                      with given tolerance
        
        crt2rtindcs - (optional) array of inverse conversion indeces 
                      (dtype = np.int64) i.e. for i in range(crt.shape[0])
                      crt[i] is matched to rt[crt2rtindcs[i]],
                      crt2rtindcs has same size as crt
                      "-1" numerical value in crt2rtindcs[i] indicates no match
                      with given tolerance
    
    """
    
    if len(rt.shape) != 1:
        raise TypeError('rt should be 1D NumPy array!');

    if len(crt.shape) != 1:
        raise TypeError('crt should be 1D NumPy array!');
    

    if crt.shape[0] == 0 or rt.shape[0] == 0:
        if return_inverse:
            return np.array([], dtype = np.int64), np.array([], dtype = np.int64);
        else:
            return np.array([], dtype = np.int64);

        
    #indeces for array subselections    
    crt_ind_range = np.arange(crt.shape[0], dtype = np.int64);
    rt_ind_range = np.arange(rt.shape[0], dtype = np.int64);

    # efficient nearest-neighbour alignment of retention time vector to the common feature vector


    rt2crtindcs = np.round(np.interp(rt, crt, np.arange(0., len(crt))))
    rt2crtindcs = (rt2crtindcs.astype(int)).flatten()
                
    # remove all matched pairs smaller than pre-defined or calculated torelance 
    # -1 indicates no match
    rt2crtindcs[np.abs(crt[rt2crtindcs] - rt) > tolerance] = -1;
    
    # remove repetitions leaving the closest match only
    #get unique link indeces and their counts
    u, uc = np.unique(rt2crtindcs, return_counts = True);
    #get indeces with counts more than 1
    mids = u[uc > 1];
    #exclude mismatched indeces marked as -1
    mids = mids[mids >=0 ];
    
    #prepare the list for indeces to be re-processed recursively
    redo_list = [];
    
    #Iterate through indeces with multiple matches (i.e. non-unique ones)    
    for i in range(mids.shape[0]):
        #get rt indeces of the non-unique match
        rti = rt_ind_range[rt2crtindcs == mids[i]];
        #calculate distances for non-unique matches
        dist = np.abs(crt[mids[i]] - rt[rti]);
        #get position of the best match
        best = np.argmin(dist);
        #set all indeces to -2 to indicate the non-unique match
        rt2crtindcs[rti] = -2;
        #but set the best match to one closest in dist
        rt2crtindcs[rti[best]] = mids[i];
        #add the remaining indeces to the list of the ones needing re-iteration
        redo_list.append(np.delete(rti, best));

    #check if re-iteration is needed (i.e. there are non-matched non-unique entries left)    
    if redo_list:
        #get full list of indeces for re-matching
        redo_rt_idcs = np.hstack(redo_list);
        #prepare boolean mask for unmatched indeces
        unmatched_crts = np.full(crt.shape, True, dtype = np.bool);
        #get the list of uniquely matched indeces
        matched_crts = rt2crtindcs[rt2crtindcs >= 0];
        #exclude entries which were uniquely matched from the mask
        unmatched_crts[matched_crts] = False;
        #get the list of unmatched indeces
        redo_crt_idcs = crt_ind_range[unmatched_crts];
        #call matching recursively for unmatched and non-uniquely matched indeces
        sub_rt2crt = nn_match(rt[redo_rt_idcs], crt[redo_crt_idcs], tolerance);
        #get mask for newly matched indeces
        sub_rt2crt_unmatched = sub_rt2crt < 0;
        #get inverse mask for completely unmatched indeces
        sub_rt2crt_matched = np.logical_not(sub_rt2crt_unmatched);
        #set completely unmatched indeces to -1
        rt2crtindcs[redo_rt_idcs[sub_rt2crt_unmatched]] = -1;
        #set re-matched indeces to the newly detected values from recursive call
        rt2crtindcs[redo_rt_idcs[sub_rt2crt_matched]] = redo_crt_idcs[sub_rt2crt[sub_rt2crt_matched]];
    

    rt2crtindcs[rt2crtindcs[:] == -2] = -1;
    
    if return_inverse:
        #create and pre-fill crt2rtindcs with -1 to cover non-matched indeces
        crt2rtindcs = np.full(crt.shape, -1, dtype = np.int64);
        #get mask of matched rt indeces
        match_rt2crt_mask = rt2crtindcs >=0;
        #get array of matched crt indeces
        matched_crts = rt2crtindcs[match_rt2crt_mask];
        #get array of corresponding rt indeces
        matched_rts = rt_ind_range[match_rt2crt_mask];
        #assign matched inverse indeces
        crt2rtindcs[matched_crts] = matched_rts;
        return rt2crtindcs, crt2rtindcs;
    else:
        return rt2crtindcs;



#------------------------------
if __name__ == "__main__": 
    
    rt = np.array([0.2,0.21,0.22,0.3,0.33,0.34]);
    crt = np.array([0.2, 0.3]);
    
    
    a,b = nn_match(rt, crt, return_inverse = True);    
    print(rt)
    print(a)
    print(crt)
    print(b)
    
    
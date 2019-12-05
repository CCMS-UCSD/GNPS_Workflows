# -*- coding: utf-8 -*-
"""Kovat Index Filter
This file is used to filter out the compounds with bad retention Queries.

Example
-------
    $ python mapping.py input.csv mode(p/m) polyfitParameter/carbonMarker.csv cosineScore(float) errorTolerance(float)


Notes
-----
Run it with kovatLib.csv in the same directory.
"""

import sys
import os
import csv
import numpy as np
import pandas as pd
import argparse
import math


# load df from input data file
def loadDf(csv, prediction):
    df = pd.read_csv(csv,sep = '\t')

    new_df = df
    new_df['Kovats_Index_calculated'] = np.nan
    new_df['Kovats_Index_Lib_Record'] = np.nan
    new_df['Kovats_Index_Error'] = np.nan
    new_df['Kovats_Confidence'] = np.nan
    
    #fill in the kovat index from the library search
    for i in range(len(new_df)):
        new_df['Kovats_Index_calculated'][i] = kovatIndex(float(new_df['RT_Query'][i]), prediction)

    return new_df


def loadMarkers(marker):
    df = pd.read_csv(marker, sep=',')
    # compounds name has to be in the format of "name(C#)"
    for i in range(len(df)):
        c_n = df['Carbon_Number'][i]
        df.ix[i, 'Compound_Name'] = float(c_n)
        df.ix[i, 'RT'] = float(df['RT'][i])
    df = df.sort_values(['Compound_Name'], ascending=[True])
    return df

def kovatIndex(rt, markerDic):
    for i in range(len(markerDic)):
        if i == len(markerDic)-1:
            return 0
        elif (rt > markerDic.RT_Query[i] and rt < markerDic.RT_Query[i+1]) \
             or (rt == markerDic.RT_Query[i] or rt ==  markerDic.RT_Query[i+1]):
            N,n,tr_N,tr_n = markerDic['Compound_Name'][i+1],markerDic['Compound_Name'][i], \
                           markerDic.RT_Query[i+1],markerDic.RT_Query[i]
            Original_Annotation_KI_calculated = 100.0*(n+(N-n)*(rt-tr_n)/(tr_N - tr_n))
            return Original_Annotation_KI_calculated
    return 0.0


def csv_builder(inputF, additionalFile, result_nonfiltered):
    
    try:
        prediction = loadMarkers(additionalFile)
    except:
        empty_tsv = open(result_nonfiltered,'w')
        empty_tsv_filtered = open(result_filtered,'w')
        empty_tsv.write('Bad Carbon Marker File Format')
        empty_tsv_filtered.write('Bad Carbon Marker File Format')
        return
    #LoadDataframe and trim it to be the one we need
    df = loadDf(inputF, prediction)
    df.to_csv(result_nonfiltered, sep='\t',index=False,na_rep="None")

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



# load df from input data file
def loadDf(csv,cosine,prediction,mode,lib):
    df = pd.read_csv(csv,sep = '\t')

    new_df = df
    new_df['Kovats_Index_calculated'] = np.nan
    new_df['Kovats_Index_Lib_Record'] = np.nan
    new_df['Kovats_Index_Error'] = np.nan
    # filter out by cosine score first
    new_df = new_df[new_df.MQScore > cosine]
    new_df = new_df.reset_index(drop=True)

    # load database:
    # library is sorted by CAS
    lib_df = pd.read_csv(lib)
    lib_df = lib_df[lib_df.polarity.str.contains('non-polar')]
    lib = pd.Series(lib_df.ki_nonpolar_average.values,index=lib_df.INCHI.values).to_dict()
    #fill in the kovat index from the library search
    for i in range(len(new_df)):
        if mode == 'm':
            new_df['Kovats_Index_calculated'][i] =kovatIndex(float(new_df['RT_Query'][i]), prediction)
        else:
            new_df['Kovats_Index_calculated'][i]= np.polyval(prediction,float(new_df['RT_Query'][i]))

        try:
            new_df['Kovats_Index_Lib_Record'][i] = lib[new_df['INCHI'][i]]
            new_df['Kovats_Index_Error'][i] = abs(new_df['Kovats_Index_calculated'][i] - new_df['Kovats_Index_Lib_Record'][i])/new_df['Kovats_Index_Lib_Record'][i]
        except:
            continue
    return new_df

def loadMarkers(marker):
    df = pd.read_csv(marker,sep = ';')
    # compounds name has to be in the format of "name(C#)"
    for i in range(len(df)):
        c_n = (df['Compound_Name'][i].split('(C')[-1]).split(")")[0]
        df.ix[i, 'Compound_Name'] = float(c_n)
        df.ix[i, 'RT_Query'] = float(df['RT_Query'][i])
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


def csv_builder(inputF,mode,additionalFile,cosineScore,errorTolerance,result_nonfiltered,result_filtered,lib):
    # load markers
    if mode == 'p':
        prediction = additionalFile
        print(prediction)
    else:
        try:
            prediction = loadMarkers(additionalFile)
        except:
            empty_tsv = open(result_nonfiltered,'w')
            empty_tsv_filtered = open(result_filtered,'w')
            empty_tsv.write('Bad Carbon Marker File Format')
            empty_tsv_filtered.write('Bad Carbon Marker File Format')
            return
    #LoadDataframe and trim it to be the one we need
    df = loadDf(inputF,cosineScore,prediction,mode,lib)
    df.to_csv(result_nonfiltered, sep='\t',index=False,na_rep="None")
    # filtering by RI error threshold

    df_filtered = df[df.Kovats_Index_Error < errorTolerance]
    df_filtered.to_csv(result_filtered, sep='\t',index=False,na_rep="None")

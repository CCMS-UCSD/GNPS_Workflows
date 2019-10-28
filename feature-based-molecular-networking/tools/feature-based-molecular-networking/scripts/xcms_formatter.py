
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 14:47:58 2018. Modified on April 1 2019.
@author: zheng zhang and louis felix nothias
@purpose: to convert the XCMS-(CAMERA)-(IIN) output into a diserable format for FBMN or FBMNxIIN
"""

import pandas as pd
import numpy as np
import sys

def convert_to_feature_csv(input_filename, output_filename):
    #Check and convert for XCMS or XCMS-CAMERA for FBMN

    input_format_df = pd.read_csv(input_filename,index_col=None,sep='\t')

    if 'annotation network number' not in input_format_df.columns:
        #Prepare left table with ID mz rt
        input_format_df = input_format_df.rename(columns={ "Row.names":"row ID", "mzmed":"row m/z","rtmed":"row retention time"})

        table_part_left = input_format_df[['row ID', 'row m/z','row retention time']]

        #Prepare right table with ms filename
        list_data_filename = list(input_format_df.filter(regex='.mzML|.mzXML|.mzml|.mzxml|.raw|.cdf|.CDF|.mzData|.netCDF|.netcdf|.mzdata'))
        table_part_right = input_format_df[list_data_filename]

                ## Add Peak area
        for i in range(0,len(table_part_right.columns.values)):
            table_part_right.columns.values[i] += " Peak area"
                ## Do some table processing
        table_part_right = table_part_right.fillna(value=0)
                ##Remove the FT string from the first column
        new_column = table_part_left['row ID'].to_list()
        new_column = [w.replace('FT', '') for w in new_column]
        table_part_left_copy = pd.DataFrame(np.array([new_column]).T)
        table_part_left_copy.columns = ['row ID']
        table_part_left_copy['row ID'] = new_column
        table_part_left_copy[['row ID']] = table_part_left_copy[['row ID']].apply(pd.to_numeric)
        table_part_left = table_part_left.drop(['row ID'], axis=1)
        table_part_left_processed = pd.concat([table_part_left_copy, table_part_left], axis=1, join='inner')

            ## Join back the tables
        output_format = pd.concat([table_part_left_processed, table_part_right], axis=1, join='inner')

            ## Rounding up values for better Cytoscape rendering
        output_format['row m/z'] = input_format_df['row m/z'].apply(lambda x: round(x, 3))
        output_format['row retention time'] = input_format_df['row retention time'].apply(lambda x: round(x, 1))

        output_format.to_csv(output_filename,index = False)

    #Check and convert for XCMS-CAMERA for IINxFBMN
    elif 'annotation network number' in input_format_df.columns:
        input_format_df = input_format_df.rename(columns={"mzmed":"row m/z", "rtmed":"row retention time"})

        table_part_left = input_format_df[['row ID', 'row m/z','row retention time','correlation group ID',\
                                                   'annotation network number','best ion','auto MS2 verify','identified by n=',\
                                                   'partners','neutral M mass']]

        #Prepare right table with ms filename
        list_data_filename = list(input_format_df.filter(regex='.mzML|.mzXML|.mzml|.mzxml|.raw|.RAW|.cdf|.CDF|.mzData|.netCDF|.netcdf|.mzdata'))
        table_part_right = input_format_df[list_data_filename]

        ## Add Peak area
        for i in range(0,len(table_part_right.columns.values)):
            table_part_right.columns.values[i] += " Peak area"
        #    ## Do some table processing
            table_part_right = table_part_right.fillna(value=0)

        #    ## Join back the tables
            output_format = pd.concat([table_part_left, table_part_right], axis=1, join='inner')

        #    ## Rounding up values for better Cytoscape rendering
            output_format['neutral M mass'] = input_format_df['neutral M mass'].apply(lambda x: round(x, 4))
            output_format['row m/z'] = input_format_df['row m/z'].apply(lambda x: round(x, 3))
            output_format['row retention time'] = input_format_df['row retention time'].apply(lambda x: round(x, 1))
            output_format.to_csv(output_filename,index = False)

    else:
        print('Feature quantification table format is incorrect. Verify the input table or the option selection. Please provide an XCMS table FBMN or an XCMS-CAMERA for FBMNxIIN format.')

if __name__=="__main__":
    # there should be obly one input file
    convert_to_feature_csv(sys.argv[1],sys.argv[2])

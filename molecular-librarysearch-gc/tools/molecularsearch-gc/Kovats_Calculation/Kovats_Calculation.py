import sys
import os
import argparse
import ming_proteosafe_library
import polyFitting
import mapping

def main():
    parser = argparse.ArgumentParser(description='Running sirius wrapper')
    parser.add_argument('libFiles', help='input')
    parser.add_argument('input', help='input')
    parser.add_argument('workflow_parameters', help='workflow_parameters')
    parser.add_argument('carbonMarker', help='Carbon_Marker_File')
    parser.add_argument('result_nonfiltered', help='Kovats_Result_Nonfiltered')
    parser.add_argument('result_filtered', help='Kovats_Result_Nonfiltered')

    args = parser.parse_args()
    lib = args.libFiles
    param = args.workflow_parameters
    input = args.input
    carbonMarker = args.carbonMarker
    result_nonfiltered = args.result_nonfiltered
    result_filtered = args.result_filtered

    #parse params
    params_obj = ming_proteosafe_library.parse_xml_file(open(param))
    try:
        cosineScore = float(params_obj["Kovats_Filter_Cosine_Threshold"][0])
    except:
        cosineScore = 0.9
    try:
        errorFilter = float(params_obj["Error_Filter_Threshold"][0])/100
    except:
        errorFilter = 0.1
    try:
        if params_obj["runKovats"][0] == "on":
            optin = True
    except:
        optin = False
    '''try:
        minimunFeature = int(params_obj["polyFitting_data_point"][0])
    except:
        minimunFeature = 10'''
    # set minimumFeature to be 10 currently
    minimunFeature = 10
    if not optin:
        empty_tsv = open(result,'w')
        empty_tsv.write('Kovats Calculation Opt Out')
        return
    #if there is no csv file
    if carbonMarker == '':
        supporting_file = polyFitting.getParams(input,cosineScore,1.5,lib,minimunFeature)
        if supporting_file is None:
            empty_tsv = open(result,'w')
            empty_tsv.write('Not enough data for polynomial fitting')
            return
        mode = 'p'
        #try:
        #    supporting_file = polyFitting.getParams(input,cosineScore,1.5)
        #    mode = 'p'
        #except:
        #    empty_tsv = open(result,'w')
        #    empty_tsv.write(param+'\n')
        #    empty_tsv.write(input+'\n')
        #    empty_tsv.write(carbonMarker+'\n')
        #    empty_tsv.write(result+'\n')
        #    return
    else:
        supporting_file = carbonMarker
        mode = 'm'
    #try:
    #    mapping.csv_builder(input,mode,supporting_file,cosineScore,errorFilter,result,lib)
    #except:
    #    empty_tsv = open(result,'w')
    #    empty_tsv.write('48,exit')
    #    return
    mapping.csv_builder(input,mode,supporting_file,cosineScore,errorFilter,result_nonfiltered,result_filtered,lib)




if __name__ == "__main__":
    main()

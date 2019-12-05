import sys
import os
import argparse
import ming_proteosafe_library
import polyFitting
import mapping

def main():
    parser = argparse.ArgumentParser(description='Running sirius wrapper')
    parser.add_argument('input', help='input')
    parser.add_argument('input_filtered', help='input_filtered')
    parser.add_argument('workflow_parameters', help='workflow_parameters')
    parser.add_argument('carbonMarker', help='Carbon_Marker_File')
    parser.add_argument('result_nonfiltered', help='Kovats_Result_Nonfiltered')

    args = parser.parse_args()
    param = args.workflow_parameters
    input_identifications = args.input
    input_filtered = args.input_filtered
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
        window_start = int(params_obj["window_start"][0])*60
    except:
        window_start = 60
    try:
        window_end = int(params_obj["window_end"][0])*60
    except:
        window_end = 60*13

    try:
        if params_obj["runKovats"][0] == "on":
            optin = True
    except:
        optin = False
    # set minimumFeature to be 10 currently
    minimunFeature = 10
    if not optin:
        empty_tsv = open(result_nonfiltered,'w')
        empty_tsv.write('Kovats Calculation Opt Out')
        empty_tsv = open(result_filtered,'w')
        empty_tsv.write('Kovats Calculation Opt Out')
        return
    supporting_file = carbonMarker
    mode = 'm'

    mapping.csv_builder(input, supporting_file, errorFilter, result_nonfiltered)




if __name__ == "__main__":
    main()

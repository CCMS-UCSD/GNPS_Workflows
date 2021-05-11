import pandas as pd
import argparse
import shutil
import math
import numpy as np

def loadMarkers(marker):
    df = pd.read_csv(marker, sep=',')

    # compounds name has to be in the format of "name(C#)"
    df["Compound_Name"] = df["Carbon_Number"].astype('int32')
    df["RT"] = df["RT"].astype('float32')/60
    df = df.sort_values(['Compound_Name'], ascending=[True])

    return df

"""Given the marker file, this function calculate the RI"""
def kovatIndex(rt, markerDic):
    for i in range(len(markerDic)):
        if i == len(markerDic)-1:
            return 0
        elif (rt > markerDic.RT[i] and rt < markerDic.RT[i+1]) \
             or (rt == markerDic.RT[i] or rt ==  markerDic.RT[i+1]):
            N,n,tr_N,tr_n = markerDic['Compound_Name'][i+1],markerDic['Compound_Name'][i], \
                           markerDic.RT[i+1],markerDic.RT[i]
            Original_Annotation_KI_calculated = 100.0*(n+(N-n)*((math.log(rt)-math.log(tr_n))/(math.log(tr_N) - math.log(tr_n))))
            return Original_Annotation_KI_calculated
    return 0.0


def calculate_kovats(input_identifications_filename, input_marker_filename, output_identifications_filename):
    try:
        print(input_marker_filename)
        marker_dictionary = loadMarkers(input_marker_filename)
    except:
        raise
        raise Exception("Invalid Carbon Marker File")

    #Loading identifications file
    identifications_df = pd.read_csv(input_identifications_filename, sep="\t")

    new_df = identifications_df
    new_df['Kovats_Index_calculated'] = np.nan
    
    #fill in the kovat index from the library search
    for i in range(len(new_df)):
        new_df['Kovats_Index_calculated'][i] = kovatIndex(float(new_df['RT_Query'][i]), marker_dictionary)

    new_df.to_csv(output_identifications_filename, sep='\t', index=False, na_rep="None")


def main():
    parser = argparse.ArgumentParser(description='Running Kovats Prediction')
    parser.add_argument('input_library_identifications', help='input_library_identifications')
    parser.add_argument('input_carbon_marker_filename', help='Carbon_Marker_File')
    parser.add_argument('output_library_identifications', help='output_library_identifications')
    parser.add_argument('--run_kovats', help='run_kovats', default="off")
    args = parser.parse_args()

    if args.run_kovats == "off":
        shutil.copy(args.input_library_identifications, args.output_library_identifications)
        exit(0)

    ### Performing Prediction
    calculate_kovats(args.input_library_identifications, 
    args.input_carbon_marker_filename, 
    args.output_library_identifications)

if __name__ == "__main__":
    main()

import sys
import os
import requests
import argparse
import pandas as pd

parser = argparse.ArgumentParser(description='Batch Create Wrapper Validator')
parser.add_argument('workflowparams')
parser.add_argument('pklbinfolder')
parser.add_argument('annotation_table')
parser.add_argument('result_output')
parser.add_argument('new_results_output')
parser.add_argument('output_library')
parser.add_argument('main_execmodule_path')
args = parser.parse_args()

# Making sure the into annotation table has a dummy spectrumID
annotation_table_df = pd.read_csv(args.annotation_table, sep="\t")
temp_annotation_filename = "annotation.tsv"
annotation_table_df["SPECTRUMID"] = "SPECLIBTEMP"
annotation_table_df.to_csv(temp_annotation_filename, sep="\t", index=False)

cmd = "{} ExecSpectraExtractionTable {} -ccms_input_spectradir {} -ccms_table_input {} -ccms_results_dir {} -ccms_newresults_dir {} -ccms_newoutputlibrary {} -ccms 1 -ll 9".format(args.main_execmodule_path, 
    args.workflowparams, args.pklbinfolder, temp_annotation_filename, args.result_output, args.new_results_output, args.output_library)

print(cmd)

exit_status = os.system(cmd)

if exit_status != 0:
    exit(1)
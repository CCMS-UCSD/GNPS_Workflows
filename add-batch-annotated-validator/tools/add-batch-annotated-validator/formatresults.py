import argparse
import pandas as pd
import os
import sys
sys.path.insert(0, "./shared_code/")
import ming_proteosafe_library

parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('input_annotation')
parser.add_argument('workflowParams')
parser.add_argument('output_formatted_result')

args = parser.parse_args()

params_obj = ming_proteosafe_library.parse_xml_file(open(args.workflowParams, "r"))
reverse_mangled_mapping = ming_proteosafe_library.get_reverse_mangled_file_mapping(params_obj)

input_annotation_df = pd.read_csv(args.input_annotation, sep='\t')
annotation_results_list = input_annotation_df.to_dict(orient='records')

for annotation_obj in annotation_results_list:
    filename = os.path.basename(annotation_obj["FILENAME"])
    mangled_filename = reverse_mangled_mapping[filename]

    annotation_obj["proteosafe_path"] = mangled_filename

new_df = pd.DataFrame(annotation_results_list)
new_df.to_csv(args.output_formatted_result, sep='\t', index=False)




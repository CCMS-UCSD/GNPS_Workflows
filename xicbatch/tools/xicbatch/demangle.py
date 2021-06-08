import os
import sys
import pandas as pd

import argparse
import ming_proteosafe_library

def main():
    parser = argparse.ArgumentParser(description='Creating Demangling')
    parser.add_argument('input_results', help='input_mgf')
    parser.add_argument('output_results', help='output_results')
    parser.add_argument('params', help='msaccess_path')
    args = parser.parse_args()

    params_dict = ming_proteosafe_library.parse_xml_file(open(args.params))
    mangled_mapping = ming_proteosafe_library.get_mangled_file_mapping(params_dict)

    results_df = pd.read_csv(args.input_results, sep="\t")
    results_list = results_df.to_dict(orient="records")

    for result in results_list:
        filename = result["filename"]
        full_ccms_path = mangled_mapping[filename]
        result["full_ccms_path"] = full_ccms_path
    

    demanged_results_df = pd.DataFrame(results_list)
    demanged_results_df.to_csv(args.output_results, sep="\t", index=False)
    

if __name__ == "__main__":
    main()

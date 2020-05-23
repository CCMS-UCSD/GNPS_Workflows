import sys
import getopt
import os
import fnmatch
import glob
import xmltodict
import ming_proteosafe_library
import argparse
import pandas as pd
import requests

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('param_xml', help='param_xml')
    parser.add_argument('metadata_folder', help='metadata_folder')
    parser.add_argument('output_metadata_folder', help='output_metadata_folder')
    args = parser.parse_args()

    process(args.param_xml, args.metadata_folder, args.output_metadata_folder)

def process(param_xml, metadata_folder, output_metadata_folder):
    params_object = ming_proteosafe_library.parse_xml_file(open(param_xml))
    mangled_mapping = ming_proteosafe_library.get_mangled_file_mapping(params_object)

    input_metadata_filenames = glob.glob(os.path.join(metadata_folder, "*"))

    user_metadata_df = None
    if len(input_metadata_filenames) == 1:
        user_metadata_df = pd.read_csv(input_metadata_filenames[0], sep="\t")
    
    if len(input_metadata_filenames) > 1:
        print("You have selected too many metadata files")
        exit(1)
    
    # We didnt input metadata file, lets see what we can do with sheets
    if len(input_metadata_filenames) == 0:
        try:
            from urllib.parse import urlparse
            sheets_url = params_object["googlesheetsmetadata"][0]
            parsed_url = urlparse(sheets_url)
            path = parsed_url.path
            path_splits = path.split("/")
            sheets_id = path_splits[3]

            json_url = "https://gnps-sheets-proxy.herokuapp.com/sheets.json?sheets_id={}".format(sheets_id)

            r = requests.get(json_url)
            user_metadata_df = pd.DataFrame(r.json())
        except:
            pass



    default_group_list = []
    for mangled_name in mangled_mapping.keys():
        group_dict = {}
        group_dict["filename"] = os.path.basename(mangled_mapping[mangled_name])
        if mangled_name.find("spec-") != -1:
            group_dict["DefaultGroup"] = "G1"
        if mangled_name.find("specone-") != -1:
            group_dict["DefaultGroup"] = "G1"
        if mangled_name.find("spectwo-") != -1:
            group_dict["DefaultGroup"] = "G2"
        if mangled_name.find("specthree-") != -1:
            group_dict["DefaultGroup"] = "G3"
        if mangled_name.find("specfour-") != -1:
            group_dict["DefaultGroup"] = "G4"
        if mangled_name.find("specfive-") != -1:
            group_dict["DefaultGroup"] = "G5"
        if mangled_name.find("specsix-") != -1:
            group_dict["DefaultGroup"] = "G6"

        if len(group_dict) > 1:
            default_group_list.append(group_dict)

    default_metadata_df = pd.DataFrame(default_group_list)

    if user_metadata_df is not None:
        merged_metadata_df = default_metadata_df.merge(user_metadata_df, how="outer", on="filename")
    else:
        merged_metadata_df = default_metadata_df

    output_metadata_filename = os.path.join(output_metadata_folder, "metadata.tsv")
    merged_metadata_df.to_csv(output_metadata_filename, sep="\t", index=False)


if __name__ == '__main__':
    main()
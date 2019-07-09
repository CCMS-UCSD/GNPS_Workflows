#!/usr/bin/python


import sys
import getopt
import os
import json
import argparse
import ming_fileio_library
import ming_proteosafe_library
import re
from collections import defaultdict
import pandas as pd
import requests
import shutil

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('param_xml', help='metadata_folder')
    parser.add_argument('cluster_buckets', help='cluster_buckets')
    parser.add_argument('metadata_folder', help='metadata_folder')
    parser.add_argument('output_folder', help='output_folder')
    args = parser.parse_args()

    param_object = ming_proteosafe_library.parse_xml_file(open(args.param_xml, "r"))

    if param_object["CREATE_CLUSTER_BUCKETS"][0] == "0":
        print("Do not do things")
        exit(0)

    reverse_file_mangling = ming_proteosafe_library.get_reverse_mangled_file_mapping(param_object)

    """Reading Metadata File"""
    metadata_files_in_folder = ming_fileio_library.list_files_in_dir(args.metadata_folder)
    object_list = []

    if len(metadata_files_in_folder) != 1:
        for real_name in reverse_file_mangling:
            mangled_name = reverse_file_mangling[real_name]
            if mangled_name.find("spec") == -1:
                continue
            object_list.append({"filename" : real_name})
    else:
        object_list_temp = ming_fileio_library.parse_table_with_headers_object_list(metadata_files_in_folder[0])
        #object_list_temp = pd.read_csv(metadata_files_in_folder[0], sep="\t")

        object_list = []
        for metadata_object in object_list_temp:
            if len(metadata_object["filename"]) > 1:
                object_list.append(metadata_object)
        
        #Adding all files, if analyzed file is not in list
        for real_name in reverse_file_mangling:
            mangled_name = reverse_file_mangling[real_name]
            if mangled_name.find("spec") == -1:
                continue

            found = False
            for metadata_object in object_list:
                if os.path.basename(real_name) == metadata_object["filename"]:
                    found = True
                    break

            if found is False:
                object_list.append({"filename" : real_name})

    #Writing headers
    header_list = ["#SampleID", "BarcodeSequence", "LinkerPrimerSequence"]
    for key in object_list[0]:
        if not key in header_list:
            header_list.append(key)

    header_list.append("ATTRIBUTE_GNPSDefaultGroup")

    for metadata_object in object_list:
        if not "#SampleID" in metadata_object:
            if "#SampleID" in metadata_object:
                metadata_object["#SampleID"] = metadata_object["#SampleID"]
            else:
                #Stripping off all non-alphanumeric characters
                #metadata_object["#SampleID"] = ''.join(ch for ch in metadata_object["filename"] if ch.isalnum())
                metadata_object["#SampleID"] = metadata_object["filename"]
        if not "Description" in metadata_object:
            metadata_object["Description"] = "LoremIpsum"
        if not "BarcodeSequence" in metadata_object:
            metadata_object["BarcodeSequence"] = "GATACA"
        if not "LinkerPrimerSequence" in metadata_object:
            metadata_object["LinkerPrimerSequence"] = "GATACA"

        #Adding default grouping information
        try:
            mangled_name = reverse_file_mangling[metadata_object["filename"]]
            if mangled_name.find("spec-") != -1:
                metadata_object["ATTRIBUTE_GNPSDefaultGroup"] = "G1"
            elif mangled_name.find("spectwo-") != -1:
                metadata_object["ATTRIBUTE_GNPSDefaultGroup"] = "G2"
            elif mangled_name.find("specthree-") != -1:
                metadata_object["ATTRIBUTE_GNPSDefaultGroup"] = "G3"
            elif mangled_name.find("specfour-") != -1:
                metadata_object["ATTRIBUTE_GNPSDefaultGroup"] = "G4"
            elif mangled_name.find("specfive-") != -1:
                metadata_object["ATTRIBUTE_GNPSDefaultGroup"] = "G5"
            elif mangled_name.find("specsix-") != -1:
                metadata_object["ATTRIBUTE_GNPSDefaultGroup"] = "G6"
        except:
            print(metadata_object["filename"], "Not Mapped")
            metadata_object["ATTRIBUTE_GNPSDefaultGroup"] = "Not Mapped"

    output_metadata_filename = os.path.join(args.output_folder, "qiime2_metadata.tsv")
    output_manifest_filename = os.path.join(args.output_folder, "qiime2_manifest.tsv")

    for metadatum in object_list:
        if "sample_name" in metadatum:
            if len(metadatum["sample_name"]) > 1:
                metadatum["#SampleID"] = metadatum["sample_name"]


    #Removing metadata filenames that are not in the actual data
    #analysis_files = 

    metadata_df = pd.DataFrame(object_list)
    metadata_df.to_csv(output_metadata_filename, index=False, sep="\t", columns=header_list)

    """Outputting Manifest Filename"""
    manifest_df = pd.DataFrame()
    manifest_df["sample_name"] = metadata_df["#SampleID"]
    manifest_df["filepath"] = metadata_df["filename"]
    manifest_df.to_csv(output_manifest_filename, index=False, sep=",")

    """Calling remote server to do the calculation"""
    SERVER_BASE = "http://dorresteinappshub.ucsd.edu:5024"
    files = {'manifest': open(output_manifest_filename, 'r'), \
    'metadata': open(output_metadata_filename, 'r'), \
    'bucket': open(args.cluster_buckets, 'r')}

    r_post = requests.post(SERVER_BASE + "/processclassic", files=files)
    response_dict = r_post.json()

    with open(os.path.join(args.output_folder, "qiime2_table.qza"), 'wb') as f:
        r = requests.get(SERVER_BASE + response_dict["table_qza"], stream=True)
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)

    with open(os.path.join(args.output_folder, "qiime2_emperor.qzv"), 'wb') as f:
        r = requests.get(SERVER_BASE + response_dict["emperor_qzv"], stream=True)
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)




if __name__ == "__main__":
    main()

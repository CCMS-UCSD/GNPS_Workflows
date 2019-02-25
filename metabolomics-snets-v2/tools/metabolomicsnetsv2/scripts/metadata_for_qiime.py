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

def main():
    parser = argparse.ArgumentParser(description='Modifying script')
    parser.add_argument('param_xml', help='metadata_folder')
    parser.add_argument('metadata_folder', help='metadata_folder')
    parser.add_argument('output_metadata_table', help='output_metadata_table')
    parser.add_argument('output_view_emporer', help='output_metadata_table')
    args = parser.parse_args()

    param_object = ming_proteosafe_library.parse_xml_file(open(args.param_xml, "r"))



    if param_object["CREATE_CLUSTER_BUCKETS"][0] == "0":
        output_html_file = open(args.output_view_emporer, "w")
        output_html_file.write("Please Enable Bucket Table/Biom output on the input menu")
        output_html_file.close()
    else:
        """Outputting html"""
        from urllib.parse import urlencode, quote_plus
        parameters_for_qiime = { 'biom' : 'http://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=biom_output/networking_quant.biom' % (param_object["task"][0]), 'metadata' : 'http://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=metadata_for_qiime/metadata_for_qiime.txt' % (param_object["task"][0])}

        output_html_file = open(args.output_view_emporer, "w")
        output_html_file.write("<script>\n")
        output_html_file.write('window.location.replace("https://mingwangbeta.ucsd.edu/emperor?%s")\n' % urlencode(parameters_for_qiime))
        output_html_file.write("</script>\n")
        output_html_file.close()

    reverse_file_mangling = ming_proteosafe_library.get_reverse_mangled_file_mapping(param_object)

    metadata_files_in_folder = ming_fileio_library.list_files_in_dir(args.metadata_folder)

    object_list = []

    if len(metadata_files_in_folder) != 1:
        for real_name in reverse_file_mangling:
            mangled_name = reverse_file_mangling[real_name]
            if mangled_name.find("spec") == -1:
                continue
            object_list.append({"filename" : real_name})

    else:
        print(metadata_files_in_folder[0])
        object_list = ming_fileio_library.parse_table_with_headers_object_list(metadata_files_in_folder[0])
        if len(object_list) == 0:
            for real_name in reverse_file_mangling:
                mangled_name = reverse_file_mangling[real_name]
                if mangled_name.find("spec") == -1:
                    continue
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
                metadata_object["#SampleID"] = ''.join(ch for ch in metadata_object["filename"] if ch.isalnum())
        if not "Description" in metadata_object:
            metadata_object["Description"] = "LoremIpsum"
        if not "BarcodeSequence" in metadata_object:
            metadata_object["BarcodeSequence"] = "GATACA"
        if not "LinkerPrimerSequence" in metadata_object:
            metadata_object["LinkerPrimerSequence"] = "GATACA"

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


    ming_fileio_library.write_list_dict_table_data(object_list, args.output_metadata_table, header_list)





if __name__ == "__main__":
    main()

#!/usr/bin/python


import sys
import getopt
import os
import argparse
import ming_fileio_library
import ming_proteosafe_library
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser(description='Group Mapping from input, defaults and metadata file')
    parser.add_argument('proteosafe_parameters', help='proteosafe_parameters')
    parser.add_argument('groupmapping_folder', help='groupmapping_folder')
    parser.add_argument('attributemapping_folder', help='attributemapping_folder')
    parser.add_argument('metadata_folder', help='metadata_folder')
    parser.add_argument('output_groupmapping_file', help='output_groupmapping_file')
    parser.add_argument('output_attributemapping_file', help='output_attributemapping_file')
    parser.add_argument('inputspectrafolder', help='inputspectrafolder')
    args = parser.parse_args()

    param_obj = ming_proteosafe_library.parse_xml_file(open(args.proteosafe_parameters))
    mangled_file_mapping = ming_proteosafe_library.get_mangled_file_mapping(param_obj)
    reverse_file_mangling = ming_proteosafe_library.get_reverse_mangled_file_mapping(param_obj)
    print(reverse_file_mangling.keys())
    file_path_prefix = args.inputspectrafolder

    output_group_file = open(args.output_groupmapping_file, "w")
    output_attribute_file = open(args.output_attributemapping_file, "w")

    """
    Writing Default Grouping to output file
    """
    default_groupings = {'G1' : [] , 'G2' : [] ,'G3' : [] ,'G4' : [] ,'G5' : [] ,'G6' : [] }
    for mangled_name in mangled_file_mapping.keys():
        if mangled_name.find("spec-") != -1:
            default_groupings['G1'].append(mangled_name.rstrip())
        if mangled_name.find("spectwo-") != -1:
            default_groupings['G2'].append(mangled_name.rstrip())
        if mangled_name.find("specthree-") != -1:
            default_groupings['G3'].append(mangled_name.rstrip())
        if mangled_name.find("specfour-") != -1:
            default_groupings['G4'].append(mangled_name.rstrip())
        if mangled_name.find("specfive-") != -1:
            default_groupings['G5'].append(mangled_name.rstrip())
        if mangled_name.find("specsix-") != -1:
            default_groupings['G6'].append(mangled_name.rstrip())

    for default_group_key in default_groupings.keys():
        default_group_string = ""
        default_group_string += "GROUP_" + default_group_key +"="
        for mangled_name in default_groupings[default_group_key]:
            default_group_string += os.path.join(file_path_prefix, mangled_name) + ";"
        if len(default_groupings[default_group_key]) > 0:
            default_group_string = default_group_string[:-1]
        output_group_file.write(default_group_string + "\n")


    """Determining output whether to use group mapping file or metadata file"""
    metadata_files_in_folder = ming_fileio_library.list_files_in_dir(args.metadata_folder)
    groupmapping_files_in_folder = ming_fileio_library.list_files_in_dir(args.groupmapping_folder)
    attributemapping_files_in_folder = ming_fileio_library.list_files_in_dir(args.attributemapping_folder)

    if len(metadata_files_in_folder) > 1:
        print("Too many metafile inputted")
        exit(1)
    if len(metadata_files_in_folder) == 1:
        #Using metadatat file
        row_count, table_data = ming_fileio_library.parse_table_with_headers(metadata_files_in_folder[0])
        if not "filename" in table_data:
            print("Missing 'filename' header in metadata file. Please specify the file name that goes along with each piece of metadata with the header: filename")
            exit(1)
        attributes_to_groups_mapping = defaultdict(set)
        group_to_files_mapping = defaultdict(list)
        for i in range(row_count):
            filename = table_data["filename"][i]
            basename_filename = os.path.basename(filename).rstrip()
            print(basename_filename, len(reverse_file_mangling.keys()))
            if basename_filename in reverse_file_mangling:
                mangled_name = reverse_file_mangling[basename_filename]
                for key in table_data:
                    if key.find("ATTRIBUTE_") != -1:
                        group_name = table_data[key][i]
                        if len(group_name) < 1:
                            continue
                        group_to_files_mapping[group_name].append(os.path.join(file_path_prefix, mangled_name))
                        attributes_to_groups_mapping[key.replace("ATTRIBUTE_", "")].add(group_name)
            else:
                #Filename is not part of sample set
                print(basename_filename, "missing")
                continue


        for group_name in group_to_files_mapping:
            group_string = "GROUP_" + group_name + "="  + ";".join(group_to_files_mapping[group_name])
            output_group_file.write(group_string + "\n")

        for attribute_name in attributes_to_groups_mapping:
            attribute_string = attribute_name + "=" + ";".join(list(attributes_to_groups_mapping[attribute_name]))
            output_attribute_file.write(attribute_string + "\n")
        exit(0)

    """Falling back on old group mapping file"""
    if len(groupmapping_files_in_folder) > 1 or len(attributemapping_files_in_folder) > 1:
        print("Too many group/attribute mappings inputted")
        exit(1)

    if len(groupmapping_files_in_folder) == 1:
        for line in open(groupmapping_files_in_folder[0], errors='ignore'):
            splits = line.rstrip().split("=")
            if len(splits) < 2:
                continue

            group_name = splits[0]
            group_files = []
            for filename in splits[1].split(";"):
                if os.path.basename(filename) in reverse_file_mangling:
                    mangled_name = reverse_file_mangling[os.path.basename(filename)]
                    group_files.append(os.path.join(file_path_prefix, mangled_name))

            group_string = group_name + "=" + ";".join(group_files)
            output_group_file.write(group_string + "\n")

    if len(attributemapping_files_in_folder) == 1:
        for line in open(attributemapping_files_in_folder[0]):
            output_attribute_file.write(line)


if __name__ == "__main__":
    main()

#!/usr/bin/python

import os
import csv
import shutil
from collections import defaultdict

def get_header_mappings(header_str):
    header_mapping = {}
    header_splits = header_str.rstrip().split("\t")
    index_count = 0
    for header in header_splits:
        header_mapping[header] = index_count
        index_count += 1
    return header_mapping

#Parses a filename and returns 2 things
#first is the number of lines, and then a map to lists with the key being the column.
def parse_table_with_headers(filename, skip_incomplete_lines=False, debug=False, delimiter="\t"):
    input_file = None
    try:
        input_file = open(filename, "r",encoding='ascii',errors='ignore')
    except:
        input_file = open(filename, "r")

    line_count = 0
    headers = []
    index_to_header_map = {}
    column_values = defaultdict(list)
    total_columns_count = 0
    for line in input_file:
        if len(line.rstrip()) == 0:
            continue

        line_count += 1
        if line_count == 1:
            headers = line.rstrip().split(delimiter)
            header_idx = 0
            for header in headers:
                index_to_header_map[header_idx] = header
                header_idx += 1
                if len(header) > 0:
                    column_values[header] = []
            total_columns_count = len(headers)
            continue

        line_splits = line.rstrip('\n').split(delimiter)

        column_count = 0

        if skip_incomplete_lines == True and len(line_splits) != total_columns_count:
            line_count -= 1
            continue

        for line_split in line_splits:
            if not column_count in index_to_header_map:
                continue
            header_name = index_to_header_map[column_count]

            if len(header_name) < 1:
                continue
            column_values[header_name].append(line_split)
            column_count += 1

    return (line_count-1, column_values)

def parse_table_with_headers_object_list(filename, delimiter="\t"):
    # row_count, table_data = parse_table_with_headers(filename, skip_incomplete_lines=True, delimiter=delimiter)
    #
    # output_object_list = []
    #
    # for i in range(row_count):
    #     my_object = {}
    #     for key in table_data:
    #         my_object[key] = table_data[key][i]
    #     output_object_list.append(my_object)
    #
    # return output_object_list

    output_object_list = []
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        for row in reader:
            output_object_list.append(row)

    return output_object_list


def parse_table_without_headers(filename):
    input_file = open(filename, "r")

    line_count = 0
    column_values = {}
    for line in input_file:
        line_splits = line.rstrip().split("\t")

        line_count += 1
        if line_count == 1:
            for i in range(len(line_splits)):
                column_values[i] = []


        column_count = 0
        for line_split in line_splits:
            column_values[column_count].append(line_split)
            column_count += 1

    return (line_count-1, column_values)

#Given a dictionary of header values to lists of column values
#Write out the file, each of the columns must have an equal number of rows
def write_dictionary_table_data(column_dictionary, output_filename, number_of_rows=0, header_list=[]):
    output_file = open(output_filename, "w")

    if number_of_rows == 0:
        if len(list(column_dictionary.keys())) == 0:
            return
        number_of_rows = len(column_dictionary[list(column_dictionary.keys())[0]])

        #Checking row counts
        for key in column_dictionary:
            if len(column_dictionary[key]) != number_of_rows:
                print("Invalid number of rows for key", key, len(column_dictionary[key]), number_of_rows)

    #Writing Header
    header_string = ""
    if len(header_list) == 0:
        header_list = list(column_dictionary.keys())
        header_list.sort()
    for header in header_list:
        header_string += header + "\t"

    output_file.write(header_string.rstrip() + "\n")

    for i in range(number_of_rows):
        output_array = []
        for header in header_list:
            try:
                if len(str(column_dictionary[header][i])) == 0:
                    output_array.append(" ")
                else:
                    output_array.append(str(column_dictionary[header][i]))
            except KeyboardInterrupt:
                raise
            except:
                try:
                    output_array.append(str(column_dictionary[header][i].encode('ascii', 'ignore')))
                except KeyboardInterrupt:
                    raise
                except:
                    output_array.append(str(column_dictionary[header][i].decode('utf-8')))

        output_file.write("\t".join(output_array) + "\n")

    output_file.close()

def write_list_dict_table_data(output_list, output_filename, header_list=[]):
    output_dict = defaultdict(list)
    for output_object in output_list:
        for key in output_object:
            output_dict[key].append(output_object[key])
    write_dictionary_table_data(output_dict, output_filename, header_list=header_list)


#Lists only files in directory, with prefix
def list_files_in_dir(directory):
    onlyfiles = [ os.path.join(directory,f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory,f)) ]
    return onlyfiles

#Recursive
def list_all_files_in_directory(directory):
    list_of_files = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            full_filename = os.path.join(root, filename)
            list_of_files.append(full_filename)
    return list_of_files

#Lists only folders in directory, with prefix
def list_folders_in_dir(directory):
    onlyfolders = [ os.path.join(directory,f) for f in os.listdir(directory) if os.path.isdir(os.path.join(directory,f)) ]
    onlyfolders.sort()
    return onlyfolders

#List all files in dir
def list_all_in_dir(directory):
    everything = [ os.path.join(directory,f) for f in os.listdir(directory) ]
    everything.sort()
    return everything

def list_files_in_dir_recursive(directory):
    everything = []
    for root, dirnames, filenames in os.walk(directory, followlinks=True):
        for filename in filenames:
            everything.append(os.path.join(root, filename))
    everything.sort()
    return everything

#Returns the leaf filename
def get_only_leaf_filename(path):
    return os.path.basename(path)

def get_only_filename_path_prefix(path):
    return os.path.dirname(path)

def get_filename_without_extension(path):
    return os.path.splitext(path)[0]

def get_filename_extension(path):
    return os.path.splitext(path)[1]

def is_path_present(path):
    return os.path.exists(path)

#Making sure directory exists, if not make it.
def make_sure_path_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def make_sure_file_directory_exists(file_path):
    make_sure_path_exists(get_only_filename_path_prefix(file_path))

def copy_file_validate_paths(source, destination):
    directory = get_only_filename_path_prefix(destination)
    make_sure_path_exists(directory)
    shutil.copyfile(source, destination)

def move_file_validate_paths(source, destination):
    directory = get_only_filename_path_prefix(destination)
    make_sure_path_exists(directory)
    shutil.move(source, destination)

def get_root_folder(file_path):
    base, right_piece = os.path.split(file_path)

    while(len(base) > 0):
        base, right_piece = os.path.split(base)

    return right_piece

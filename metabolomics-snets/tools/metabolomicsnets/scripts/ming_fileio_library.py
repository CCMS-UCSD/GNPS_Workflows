#!/usr/bin/python

import os

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
def parse_table_with_headers(filename):
    input_file = open(filename, "r")

    line_count = 0
    headers = []
    index_to_header_map = {}
    column_values = {}
    for line in input_file:
        line_count += 1
        if line_count == 1:
            headers = line.rstrip().split("\t")
            header_idx = 0
            for header in headers:
                index_to_header_map[header_idx] = header
                header_idx += 1
                if len(header) > 0:
                    column_values[header] = []
            continue

        line_splits = line.rstrip().split("\t")
        column_count = 0
        for line_split in line_splits:
            header_name = index_to_header_map[column_count]
            if len(header_name) < 1:
                continue
            column_values[header_name].append(line_split)
            column_count += 1

    return (line_count-1, column_values)

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
def write_dictionary_table_data(column_dictionary, output_filename, number_of_rows=0):
    output_file = open(output_filename, "w")

    if number_of_rows == 0:
        number_of_rows = len(column_dictionary[column_dictionary.keys()[0]])

    #Writing Header
    header_string = ""
    for header in column_dictionary.keys():
        header_string += header + "\t"

    output_file.write(header_string + "\n")

    for i in range(number_of_rows):
        output_line = ""
        for header in column_dictionary.keys():
            output_line += str(column_dictionary[header][i]) + "\t"
        output_file.write(output_line + "\n")

    output_file.close()

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
    return onlyfolders

#List all files in dir
def list_all_in_dir(directory):
    everything = [ os.path.join(directory,f) for f in os.listdir(directory) ]
    return everything

def list_files_in_dir_recursive(directory):
    everything = []
    for root, dirnames, filenames in os.walk(directory, followlinks=True):
        for filename in filenames:
            everything.append(os.path.join(root, filename))
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

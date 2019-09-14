#!/usr/bin/python


import sys
import getopt
import os
import math



def usage():
    print "<attributes grouping> <input clustersummary> <output clustersummary>"
    print "attributes formatting:"
    print "<New Column Header>=<Old Column Header For Count 1>;<Old Column Header For Count 2>"
    

def get_Attribute_String(headers_map, columns_list, line_split_list):
    attribute_string = ""
    
    for column_name in columns_list:
        if column_name in headers_map:
            column_index = headers_map[column_name]
            if int(line_split_list[column_index]) > 0:
                attribute_string += column_name + ","
    
    if len(attribute_string) > 0:
        return attribute_string[:-1]
    return " "
    
def get_Custom_Attributes(attributes_grouping_file):
    custom_attributes = []
    for line in attributes_grouping_file:
        if(len(line) < 2):
            continue;
        
        line_splits = line.rstrip().split("=");
        
        if(len(line_splits) != 2):
            print line + " IS BAD"
            continue
            
        column_header = line_splits[0]
        column_splits = line_splits[1].split(";")
        
        custom_attribute = [column_header, column_splits]
        custom_attributes.append(custom_attribute)
        
    return custom_attributes
        
    
def main():
    usage()
    
    print sys.argv
    
    if len(sys.argv) == 3:
        input_summary_file = open(sys.argv[1], "r")
        output_summary_file = open(sys.argv[2], "w")
        return
    
    input_summary_file = open(sys.argv[2], "r")
    output_summary_file = open(sys.argv[3], "w")
    
    
    if len(sys.argv[1]) < 3:
        return
    
    input_attribute_mapping_file = open(sys.argv[1], "r")
    
    print "READING SUMMARY FILE"
    
    custom_attributes = get_Custom_Attributes(input_attribute_mapping_file);
    #custom_attributes  = [["NEWHEADER", ["G1", "G2"]]];    #contains an array of custom attributes
    
    output_string = ""
    group_headers = []
    group_header_map = {}
    summary_line_count = 0
    for line in input_summary_file:
        summary_line_count += 1
        if summary_line_count == 1:
            #output_summary_file.write(line.rstrip() + "\tAllFiles\tAllGroups\tDefaultGroups\tRTMean\tRTStdErr" + "\n")
            group_headers = line.split("\t")
            for i in range(len(group_headers)):
                group_headers[i] = group_headers[i].rstrip().lstrip()
                group_header_map[group_headers[i]] = i
            
            output_summary_file.write(line.rstrip())
            for new_attribute in custom_attributes:
                attribute_header = new_attribute[0]
                output_summary_file.write("\t" + attribute_header)
            output_summary_file.write("\n")
            
            continue
        
        cluster_number = line.split("\t")[0]
        spectra_count = int(line.split("\t")[1])
        
        line_splits = line.split("\t")
        
        output_summary_file.write(line.rstrip('\n'));
        for new_attribute in custom_attributes:
            columns_list = new_attribute[1]
            attribute_string = get_Attribute_String(group_header_map, columns_list, line_splits)
            output_summary_file.write("\t" + attribute_string);
        output_summary_file.write("\n");
        
    
    
    
if __name__ == "__main__":
    main()
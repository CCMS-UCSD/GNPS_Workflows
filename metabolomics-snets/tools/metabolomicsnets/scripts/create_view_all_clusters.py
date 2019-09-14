#!/usr/bin/python


import sys
import getopt
import os
import math
from collections import defaultdict

def usage():
    print "<input paramx.xml> <input clustersummary> <input clusterinfo> <output clustersummary>"


def get_header_index(headers, search_header):
    index = 0
    for i in range(len(headers)):
        if headers[i].rstrip() == search_header:
            print "FOUND " + search_header
            return i

def main():
    usage()

    param_file = open(sys.argv[1], "r")
    input_summary_file = open(sys.argv[2], "r")
    input_clusterinfo_file = open(sys.argv[3], "r")
    output_summary_file = open(sys.argv[4], "w")

    file_mapping = {}

    for line in param_file:
      if line.find("upload_file_mapping") != -1:
        #print line.rstrip()
        parsed = line[len("<parameter name=\"upload_file_mapping\">"):].rstrip()
        parsed = parsed[: - len("</parameter>")]
        #print parsed
        split_mapping = parsed.split("|")

        if (len(split_mapping) == 2):
            file_key =  split_mapping[0]
            file_mapping[file_key] = os.path.basename(split_mapping[1])

    print file_mapping

    spectra_map = {}
    max_clusters = 10000000
    spectra_list = defaultdict(list)

    print "READING CLUSTER INFO FILE"

    count = 0
    #iterating through cluster info file
    for line in input_clusterinfo_file:
        if len(line) < 5:
            continue

        if line[0] == "#":
            continue

        count += 1
        if count % 1000 == 0:
            print count

        spectrum_key = line.split("\t")[0]

        spectra_list[spectrum_key].append(line)
        continue


    summary_line_count = 0

    #print spectra_list

    print "READING SUMMARY FILE"

    output_string = ""
    group_headers = []

    output_columns_indices = []
    cluster_index = -1
    file_name_index = -1
    intensity_index = -1
    retention_index = -1
    retention_err_index = -1
    parentmass_index = -1
    for line in input_summary_file:
        summary_line_count += 1
        if summary_line_count == 1:
            #output_summary_file.write(line.rstrip() + "\tIsCluster\tScanNumber\tProteosafeFilePath" + "\n")
            group_headers = line.split("\t")

            print group_headers

            cluster_index = get_header_index(group_headers, "cluster index")
            file_name_index = get_header_index(group_headers, "AllFiles")
            intensity_index = get_header_index(group_headers, "sum(precursor intensity)")
            retention_index = get_header_index(group_headers, "RTMean")
            retention_err_index = get_header_index(group_headers, "RTStdErr")
            parentmass_index = get_header_index(group_headers, "parent mass")

            output_columns_indices.append(cluster_index)
            output_columns_indices.append(file_name_index)
            output_columns_indices.append(intensity_index)
            output_columns_indices.append(retention_index)
            output_columns_indices.append(retention_err_index)
            output_columns_indices.append(parentmass_index)


            header_string = ""
            for index in output_columns_indices:
	      header_string += group_headers[index].rstrip() + "\t"

            output_summary_file.write(header_string + "ScanNumber\tProteosafeFilePath" + "\n")



            continue
        cluster_number = line.split("\t")[0]
        #print cluster_number

        line_splits = line.split("\t")


        #output_summary_file.write(line.rstrip() + "\t1\t-1\n")


        spectra_list_string = ""
        cluster_item = line.rstrip().split("\t")
        for spectra_string in spectra_list[cluster_number]:
            file_name_current = spectra_string.split()[1]
            intensity_current = spectra_string.split()[7]
            RT_current = spectra_string.split()[6]
            scan_current = spectra_string.split()[3]
            parentmass_current = spectra_string.split()[4]

            cluster_item[file_name_index] = file_name_current
            cluster_item[intensity_index] = intensity_current
            cluster_item[retention_index] = RT_current
            cluster_item[retention_err_index] = 0
            cluster_item[parentmass_index] = parentmass_current

            cluster_item_update_string = ""
            for index in output_columns_indices:
                cluster_item_update_string += str(cluster_item[index]) + "\t"

            proteosafe_path = file_name_current.split("/")[1].split("-")[0] + "/" + file_name_current.split("/")[1]

            cluster_item_update_string +=  str(scan_current) + "\t" + proteosafe_path

            output_summary_file.write(cluster_item_update_string.rstrip() + "\n")

if __name__ == "__main__":
    main()

#!/usr/bin/python


import sys
import getopt
import os
import math
import csv
import ming_proteosafe_library
from collections import defaultdict
import argparse

def main():
    parser = argparse.ArgumentParser(description='Creates enriched cluster info summary')
    parser.add_argument('param_xml', help='param_xml')
    parser.add_argument('input_clustersummary', help='input_clustersummary')
    parser.add_argument('input_clusterinfo', help='input_clusterinfo')
    parser.add_argument('output_clusterinfo', help='output_clusterinfo')
    args = parser.parse_args()

    params_object = ming_proteosafe_library.parse_xml_file(open(args.param_xml))
    mangled_mapping = ming_proteosafe_library.get_mangled_file_mapping(params_object)


    #Creating acceptable clusters to include in cluster info
    included_clusters = set()
    for row in csv.DictReader(open(args.input_clustersummary), delimiter='\t'):
        included_clusters.add(row["cluster index"])

    with open(args.input_clusterinfo) as input_clusterinfo:
        field_names = ["cluster index", "AllFiles", "sum(precursor intensity)", "RTMean", "RTStdErr", "parent mass", "ScanNumber", "ProteosafeFilePath", "Original_Path"]
        output_clusterinfo_writer = csv.DictWriter(open(args.output_clusterinfo, "w"), fieldnames=field_names, delimiter='\t')
        output_clusterinfo_writer.writeheader()

        input_clusterinfo_reader = csv.DictReader(input_clusterinfo, delimiter='\t')
        for row in input_clusterinfo_reader:
            if not (row["#ClusterIdx"] in included_clusters):
                continue
            output_dict = {}
            output_dict["cluster index"] = row["#ClusterIdx"]
            output_dict["AllFiles"] = row["#Filename"]
            output_dict["sum(precursor intensity)"] = row["#PrecIntensity"]
            output_dict["RTMean"] = row["#RetTime"]
            output_dict["RTStdErr"] = "0"
            output_dict["parent mass"] = row["#ParentMass"]
            output_dict["ScanNumber"] = row["#Scan"]
            output_dict["ProteosafeFilePath"] = os.path.join("spec", os.path.basename(row["#Filename"]))
            output_dict["Original_Path"] = "f." + mangled_mapping[os.path.basename(row["#Filename"])]
            output_clusterinfo_writer.writerow(output_dict)

    exit(0)

if __name__ == "__main__":
    main()

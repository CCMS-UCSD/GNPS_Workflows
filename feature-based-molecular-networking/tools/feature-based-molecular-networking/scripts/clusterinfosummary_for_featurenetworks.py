#!/usr/bin/python


import sys
import getopt
import os
import json
import argparse
import statistics
import glob
import ming_spectrum_library
import ming_proteosafe_library
from collections import defaultdict
import glob
import math
import pandas as pd

def determine_input_files(header_list):
    filenames = []
    filename_headers = []
    for header in header_list:
        #if header.find("mzXML") != -1 or header.find("mzML") != -1:
        if "Peak area" in header:
            filenames.append(header.replace("Peak area", "").replace("filtered", "").rstrip())
            filename_headers.append(header.rstrip("\n"))

    #If the set of filenames is empty, then we will fall back and use elimination
    blacklisted_headers = ["row ID", "row m/z", "row retention time"]
    if len(filenames) == 0:
        for header in header_list:
            if len(header) < 2:
                continue
            if header in blacklisted_headers:
                continue
            filenames.append(header.replace("Peak area", "").replace("filtered", "").rstrip())
            filename_headers.append(header)

    print(filename_headers, filenames)

    return filenames, filename_headers

def load_group_attribute_mappings(metadata_filename):
    filename_header = "filename"

    attributes_to_groups_mapping = defaultdict(set)
    group_to_files_mapping = defaultdict(list)
    
    metadata_df = pd.read_csv(metadata_filename, sep="\t", skip_blank_lines=True)
    print(metadata_df.head())
    record_list = metadata_df.to_dict(orient="records")
    for record in record_list:
        for header in record:
            if "ATTRIBUTE_" in header:
                try:
                    filename = record[filename_header].rstrip().replace('\n', '').replace('\r', '')
                    group_name = str(record[header]).rstrip().replace('\n', '').replace('\r', '')
                    attribute = header.rstrip().replace('\n', '').replace('\r', '')
                    if len(filename) > 2:
                        group_to_files_mapping[group_name].append(filename)
                        attributes_to_groups_mapping[attribute].add(group_name)
                except:
                    continue

    return group_to_files_mapping, attributes_to_groups_mapping

def determine_group_abundances(group_to_file_mapping, per_file_abundances, operation="Mean"):
    group_abundances_intermediate = defaultdict(list)
    group_abundances = defaultdict(lambda: 0.0)

    file_to_group_mapping = defaultdict(list)
    for group_name in group_to_file_mapping:
        for filename in group_to_file_mapping[group_name]:
            file_to_group_mapping[filename].append(group_name)

    for file_abundance in per_file_abundances:
        filename = file_abundance[0].replace("filtered", "").replace("Peak area", "").rstrip()
        intensity = file_abundance[1]
        for group in file_to_group_mapping[filename]:
            group_abundances_intermediate[group].append(intensity)


    for group in group_abundances_intermediate:
        if operation == "Sum":
            group_abundances[group] = sum(group_abundances_intermediate[group])
        if operation == "Mean":
            if len(group_abundances_intermediate[group]) == 0:
                group_abundances[group] = 0.0
            else:
                group_abundances[group] = statistics.mean(group_abundances_intermediate[group])

    return group_abundances

###Reading from Robin's output tool
def enrich_adduct_annotations(cluster_object, quant_table_object):
    if "correlation group ID" in quant_table_object:
        cluster_object["Correlated Features Group ID"] = quant_table_object["correlation group ID"]

    if "annotation network number" in quant_table_object:
        cluster_object["Annotated Adduct Features ID"] = quant_table_object["annotation network number"]

    if "best ion" in quant_table_object:
        cluster_object["Best Ion"] = quant_table_object["best ion"]

    if "neutral M mass" in quant_table_object:
        cluster_object["neutral M mass"] = quant_table_object["neutral M mass"]

    if "auto MS2 verify" in quant_table_object:
        cluster_object["MS2 Verification Comment"] = quant_table_object["auto MS2 verify"]

def process(input_param_xml, input_consensus_feature_file, metadata_files, input_mgf_filename, output_clusterinfo_summary):
    param_obj = ming_proteosafe_library.parse_xml_file(open(input_param_xml))

    task_id = param_obj["task"][0]

    group_to_files_mapping = defaultdict(list)
    attributes_to_groups_mapping = defaultdict(set)

    if len(metadata_files) == 1:
        group_to_files_mapping, attributes_to_groups_mapping = load_group_attribute_mappings(metadata_files[0])

    ROW_NORMALIZATION = "None"
    try:
        ROW_NORMALIZATION = param_obj["QUANT_FILE_NORM"][0]
    except:
        ROW_NORMALIZATION = "None"

    GROUP_COUNT_AGGREGATE_METHOD = "Mean"
    try:
        GROUP_COUNT_AGGREGATE_METHOD = param_obj["GROUP_COUNT_AGGREGATE_METHOD"][0]
    except:
        GROUP_COUNT_AGGREGATE_METHOD = "Mean"


    quantification_df = pd.read_csv(input_consensus_feature_file)
    quantification_list = quantification_df.to_dict(orient="records")

    input_filenames, input_filename_headers = determine_input_files(quantification_list[0].keys())

    ### Filling in Quantification table if it is missing values
    for quantification_object in quantification_list:
        ###Handling empty quantification
        for filename in input_filename_headers:
            try:
                if len(quantification_object[filename]) == 0:
                    #print(filename, quantification_object[filename], quantification_object["row ID"])
                    quantification_object[filename] = 0
            except:
                x = 1

    print("Number of Features", len(quantification_list))

    #Doing row sum normalization
    if ROW_NORMALIZATION == "RowSum":
        print("ROW SUM NORM")
        for filename_header in input_filename_headers:
            file_quants = [float(quantification_object[filename_header]) for quantification_object in quantification_list]
            summed_file_quants = sum(file_quants)
            #Handling zero column
            if summed_file_quants > 0:
                for quantification_object in quantification_list:
                    quantification_object[filename_header] = float(quantification_object[filename_header]) / sum(file_quants) * 1000000

    """Loading MS2 Spectra"""
    mgf_collection = ming_spectrum_library.SpectrumCollection(input_mgf_filename)
    mgf_collection.load_from_file()

    clusters_list = []
    for quantification_object in quantification_list:

        cluster_obj = {}
        
        cluster_obj["cluster index"] = str(int(quantification_object["row ID"]))
        cluster_obj["precursor mass"] = "{0:.4f}".format(float(quantification_object["row m/z"]))
        cluster_obj["RTConsensus"] = "{0:.4f}".format(float(quantification_object["row retention time"]))

        all_charges = []

        """Checking about the charge of this cluster"""
        try:
            spectrum_object = mgf_collection.scandict[int(cluster_obj["cluster index"])]
            charge = int(spectrum_object.charge)
        except:
            charge = 0

        """Checking if this spectrum has no peaks"""
        # try:
        #     spectrum_object = mgf_collection.scandict[int(cluster_obj["cluster index"])]
        #
        # except:
        #     continue

        all_files = [os.path.basename(filename) for filename in input_filename_headers if float(quantification_object[filename]) > 0]
        abundance_per_file = [(os.path.basename(filename), float(quantification_object[filename])) for filename in input_filename_headers]
        all_abundances = [float(quantification_object[filename]) for filename in input_filename_headers]

        if charge != 0:
            cluster_obj["parent mass"] = "{0:.4f}".format(float(quantification_object["row m/z"]) * charge - charge + 1)
        else:
            cluster_obj["parent mass"] = "{0:.4f}".format(float(quantification_object["row m/z"]))
        cluster_obj["precursor charge"] = charge

        try:
            cluster_obj["RTMean"] = statistics.mean(all_retention_times)
            cluster_obj["RTStdErr"] = statistics.stdev(all_retention_times)
        except:
            cluster_obj["RTMean"] = cluster_obj["RTConsensus"]
            cluster_obj["RTStdErr"] = 0

        cluster_obj["GNPSLinkout_Cluster"] = 'https://gnps.ucsd.edu/ProteoSAFe/result.jsp?task=%s&view=view_all_clusters_withID&show=true#{"main.cluster index_lowerinput":"%s","main.cluster index_upperinput":"%s"}' % (task_id, quantification_object["row ID"], quantification_object["row ID"])
        cluster_obj["sum(precursor intensity)"] = sum(all_abundances)
        cluster_obj["SumPeakIntensity"] = sum(all_abundances)
        cluster_obj["number of spectra"] = len(all_files)
        cluster_obj["UniqueFileSourcesCount"] = len(all_files)

        group_abundances = determine_group_abundances(group_to_files_mapping, abundance_per_file, operation=GROUP_COUNT_AGGREGATE_METHOD)

        default_groups = ["G1", "G2", "G3", "G4", "G5", "G6"]
        for group in group_to_files_mapping:
            group_header = "GNPSGROUP:" + group
            if group in default_groups:
                continue
            cluster_obj[group_header] = group_abundances[group]

        for group in default_groups:
            cluster_obj[group] = group_abundances[group]

        #Writing attributes
        for attribute in attributes_to_groups_mapping:
            groups_to_include = []
            for group in attributes_to_groups_mapping[attribute]:
                if group_abundances[group] > 0.0:
                    groups_to_include.append(group)
            if len(groups_to_include) == 0:
                cluster_obj[attribute] = ""
            else:
                cluster_obj[attribute] = ",".join(groups_to_include)


        """
        Enriching the cluster info with adduct collapsing information
        """
        enrich_adduct_annotations(cluster_obj, quantification_object)

        clusters_list.append(cluster_obj)

    pd.DataFrame(clusters_list).to_csv(output_clusterinfo_summary, sep="\t", index=False)

def main():
    parser = argparse.ArgumentParser(description='Creating Clustering Info Summary')
    parser.add_argument('params_xml', help='params_xml')
    parser.add_argument('consensus_feature_file', help='Consensus Quantification File')
    parser.add_argument('metadata_folder', help='metadata metadata_folder')
    parser.add_argument('mgf_filename', help='mgf_filename')
    parser.add_argument('output_clusterinfo_summary', help='output file')
    args = parser.parse_args()

    metadata_files = glob.glob(os.path.join(args.metadata_folder, "*"))

    process(args.params_xml, args.consensus_feature_file, metadata_files, args.mgf_filename, args.output_clusterinfo_summary)


if __name__ == "__main__":
    main()

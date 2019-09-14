#!/usr/bin/python


import sys
import getopt
import os
import ming_proteosafe_library
import argparse
import csv

def main():
    parser = argparse.ArgumentParser(description='Creates alan table')
    parser.add_argument('param_xml', help='param_xml')
    parser.add_argument('path_to_spectra_filename', help='path_to_spectra_filename')
    parser.add_argument('input_clusterinfosummary', help='input_clusterinfosummary')
    parser.add_argument('input_edges', help='input_edges')
    parser.add_argument('output_selfloop_edges', help='output_filtered_edges')
    parser.add_argument('output_display_edges', help='output_display_edges')
    parser.add_argument('output_bidirection_display_edges', help='output_bidirection_display_edges')
    args = parser.parse_args()

    #Creating output for self loop edges
    included_nodes_in_edges = set()
    edges_list = []
    for row in csv.reader(open(args.input_edges), delimiter='\t'):
        node1 = row[0]
        node2 = row[1]
        delta = row[2]
        score2 = row[3]
        cosine = row[4]
        score3 = row[5]
        component = row[6]

        included_nodes_in_edges.add(node1)
        included_nodes_in_edges.add(node2)

        edge_dict = {}
        edge_dict["CLUSTERID1"] = node1
        edge_dict["CLUSTERID2"] = node2
        edge_dict["DeltaMZ"] = delta
        edge_dict["MEH"] = score2
        edge_dict["Cosine"] = cosine
        edge_dict["OtherScore"] = score3
        edge_dict["ComponentIndex"] = component

        edges_list.append(edge_dict)

    for row in csv.DictReader(open(args.input_clusterinfosummary), delimiter='\t'):
        cluster_index = row["cluster index"]
        if not(cluster_index in included_nodes_in_edges):
            edge_dict = {}
            edge_dict["CLUSTERID1"] = cluster_index
            edge_dict["CLUSTERID2"] = cluster_index
            edge_dict["DeltaMZ"] = "0.0"
            edge_dict["MEH"] = "1.0"
            edge_dict["Cosine"] = "1.0"
            edge_dict["OtherScore"] = "1.0"
            edge_dict["ComponentIndex"] = "-1"

            edges_list.append(edge_dict)

    field_names = ["CLUSTERID1", "CLUSTERID2", "DeltaMZ", "MEH", "Cosine", "OtherScore", "ComponentIndex"]
    output_selfloop_writer = csv.DictWriter(open(args.output_selfloop_edges, "w"), fieldnames=field_names, delimiter='\t')
    output_selfloop_writer.writeheader()
    for edge_dict in edges_list:
        output_selfloop_writer.writerow(edge_dict)

    #Creating display objects
    display_edge_list = []
    bidirection_display_edge_list = []
    for row in csv.reader(open(args.input_edges), delimiter='\t'):
        node1 = row[0]
        node2 = row[1]
        delta = row[2]
        score2 = row[3]
        cosine = row[4]
        score3 = row[5]
        component = row[6]

        edge_dict = {}
        edge_dict["Node1"] = node1
        edge_dict["Node2"] = node2
        edge_dict["MzDiff"] = delta
        edge_dict["Cos_Score"] = cosine
        edge_dict["FileName"] = args.path_to_spectra_filename

        reverse_edge_dict = {}
        reverse_edge_dict["Node2"] = node1
        reverse_edge_dict["Node1"] = node2
        reverse_edge_dict["MzDiff"] = delta
        reverse_edge_dict["Cos_Score"] = cosine
        reverse_edge_dict["FileName"] = args.path_to_spectra_filename

        display_edge_list.append(edge_dict)
        bidirection_display_edge_list.append(edge_dict)
        bidirection_display_edge_list.append(reverse_edge_dict)


    field_names = ["Node1", "Node2", "MzDiff", "Cos_Score", "FileName"]
    output_display_edges_writer = csv.DictWriter(open(args.output_display_edges, "w"), fieldnames=field_names, delimiter='\t')
    output_display_edges_writer.writeheader()
    output_bidirection_display_edges_writer = csv.DictWriter(open(args.output_bidirection_display_edges, "w"), fieldnames=field_names, delimiter='\t')
    output_bidirection_display_edges_writer.writeheader()


    for edge_dict in display_edge_list:
        output_display_edges_writer.writerow(edge_dict)

    for edge_dict in bidirection_display_edge_list:
        output_bidirection_display_edges_writer.writerow(edge_dict)

if __name__ == "__main__":
    main()

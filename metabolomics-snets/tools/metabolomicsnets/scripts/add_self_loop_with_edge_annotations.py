#!/usr/bin/python


import sys
import getopt
import os



def usage():
    print "<input clustersummary> <input network edges> <output network egdes> <paramfiles>"

def parse_xml_file(input_file):
    key_value_pairs = {}
    for line in input_file:
        #print line
        new_line = line.rstrip().replace("<parameter name=\"", "")
        #new_line = new_line.replace("\">", "=")
        new_line = new_line.replace("</parameter>", "")

        splits = new_line.split("\">")
        #print splits
        if(len(splits) != 2):
            continue
        key_value_pairs[splits[0]] = splits[1]

    return key_value_pairs

def determine_delta_annotations(mass_delta, node_mz, list_of_annotations, ppm_accuracy):
    output_list_of_annotations = []

    for annotation in list_of_annotations:
        mass_of_annotation = annotation["mass"]
        ppm = (abs(mass_delta - mass_of_annotation)/node_mz) * 1000000
        if ppm < ppm_accuracy:
            output_list_of_annotations.append(annotation["tag"])

    return output_list_of_annotations

def get_cluster_to_mz(cluster_filename):
    print(cluster_filename)
    cluster_to_mz = {}
    input_summary_file = open(cluster_filename, "r")
    summary_line_count = 0
    for line in input_summary_file:
        summary_line_count += 1
        if summary_line_count == 1:
            continue

        splits = line.split()
        cluster_id = int(splits[0])
        mz = float(splits[2])
        cluster_to_mz[cluster_id] = mz
    return cluster_to_mz


def main():
    usage()

    input_summary_file = open(sys.argv[1], "r")
    input_network_edges_file = open(sys.argv[2], "r")
    output_network_file = open(sys.argv[3], "w")
    param_file = open(sys.argv[4], "r")
    params_map = parse_xml_file(param_file)
    min_cluster_size = int(params_map["CLUSTER_MIN_SIZE"])
    print "CLUSTER_MIN_SIZE " + str(min_cluster_size)
    #min_cluster_size = int(sys.argv[4])

    print "READING SUMMARY FILE"

    edges_already_in_network = {}

    summary_line_count = 0

    #Processing network edge annotation
    PPM_accuracy = 10.0
    pairs_annotation_list = []
    print(params_map)
    try:
        PPM_accuracy = float(params_map["PAIRS_PPM_ACCURACY"])

        parsed_anntation_list = params_map["USER_KNOWN_DELTAS"].split("|")

        for parsed_annotation in parsed_anntation_list:
            if len(parsed_annotation) < 3:
                continue

            mass = abs(float(parsed_annotation.split(":")[0]))
            tag = parsed_annotation.split(":")[1]

            tag_dict = {"mass" : mass, "tag" : tag}
            pairs_annotation_list.append(tag_dict)
    except KeyboardInterrupt:
        raise
    except:
        print("error parsing ppm accuracy for pairs or annotations")

    print(pairs_annotation_list)

    cluster_to_mz = get_cluster_to_mz(sys.argv[1])

    output_network_file.write("CLUSTERID1" + "\t" + "CLUSTERID2" + "\t" + "DeltaMZ" + "\t" + "MEH" +"\t" + "Cosine" + "\t" + "OtherScore" + "\t" + "ComponentIndex" + "\t" + "Annotation" + "\n");


    for line in input_network_edges_file:
        splits = line.rstrip().split()
        cluster_id_1 = int(splits[0])
        cluster_id_2 = int(splits[1])
        edges_already_in_network[cluster_id_1] = 1
        edges_already_in_network[cluster_id_2] = 1

        mass_delta = abs(float(splits[2]))

        cluster_id_1_mz = cluster_to_mz[cluster_id_1]
        cluster_id_2_mz = cluster_to_mz[cluster_id_2]

        all_delta_annotations = determine_delta_annotations(mass_delta, max(cluster_id_1_mz, cluster_id_2_mz), pairs_annotation_list, PPM_accuracy)

        delta_annotations_string  = "N/A"
        if len(all_delta_annotations) > 0:
            delta_annotations_string = ":".join(all_delta_annotations)
        if len(delta_annotations_string) == 0:
            delta_annotations_string = "N/A"

        splits.append(delta_annotations_string)

        output_network_file.write("\t".join(splits) + "\n")

    for line in input_summary_file:
        summary_line_count += 1
        if summary_line_count == 1:
            continue

        splits = line.split()
        if int(splits[1]) >= min_cluster_size:
            cluster_id = splits[0]

            if int(cluster_id) in edges_already_in_network:
                #print "already in network"
                continue

            output_network_file.write(cluster_id + "\t" + cluster_id + "\t" + "0.0" + "\t" + "1.0" + "\t" + "1.0" + "\t" + "1.0" + "\t" + "-1" + "\t" + "N/A" + "\n");
            #print line.rstrip()


        #return 0





if __name__ == "__main__":
    main()

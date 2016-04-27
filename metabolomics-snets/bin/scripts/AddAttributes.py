#!/usr/bin/python


import sys
import getopt
import os
import math



def usage():
    print "<input paramx.xml> <input clustersummary> <input clusterinfo> <output clustersummary> <proteosafe host>"
    
    
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
        
def get_param_value(param_map, key, default):
    if key in param_map.keys():
        return param_map[key]
        
    return default
    
def get_max_clusters(input_clusterinfo_file):
    cluster_count = 0
    
    #Counting number of clusters
    for line in input_clusterinfo_file:
        if len(line) < 5:
            continue
        if line[0] == "#":
            continue;
        
        spectrum_key = int(line.split("\t")[0])
        cluster_count = max(cluster_count, spectrum_key)
        
        
    print "CLUSTER COUNT: " + str(cluster_count)

    return cluster_count + 10
    
def main():
    usage()
    
    param_file = open(sys.argv[1], "r")
    input_summary_file = open(sys.argv[2], "r")
    input_clusterinfo_file = open(sys.argv[3], "r")
    output_summary_file = open(sys.argv[4], "w")
    
    proteosafe_host = "localhost"
    if(len(sys.argv) > 5):
        proteosafe_host = sys.argv[5]
    
    file_mapping = {}
    
    param_lines = []
    
    for line in param_file:
        param_lines.append(line)
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
    
    key_value_pairs = parse_xml_file(param_lines)
    CLUSTER_MIN_SIZE = int(get_param_value(key_value_pairs, "CLUSTER_MIN_SIZE", 1))
    print "CLUSTER_MIN_SIZE " + str(CLUSTER_MIN_SIZE)
    
    spectra_map = {}
    max_clusters = get_max_clusters(input_clusterinfo_file)
    spectra_list = []
    cluster_file_list = []
    spectra_retention_times = []
    
    input_clusterinfo_file = open(sys.argv[3], "r")
    
    for x in range(0,max_clusters):
        spectra_list.append([])
        cluster_file_list.append([])
        spectra_retention_times.append([])
        
    print "READING CLUSTER INFO FILE"
    
    count = 0
    #iterating through cluster info file
    for line in input_clusterinfo_file:
        if len(line) < 5:
            continue
        
        if line[0] == "#":
            continue;
        
        count += 1
        if count % 1000 == 0:
            print count
            
        spectrum_key = line.split("\t")[0]
        
        #print int(spectrum_key)
        spectra_list[int(spectrum_key)].append(file_mapping[os.path.basename(line.split("\t")[1])] + ":"+line.split("\t")[3] + "###")
        cluster_file_list[int(spectrum_key)].append(file_mapping[os.path.basename(line.split("\t")[1])])
        spectra_retention_times[int(spectrum_key)].append(float(line.split("\t")[6]))
        continue
        
        
    summary_line_count = 0
    
    #print spectra_list
    
    print "READING SUMMARY FILE"
    
    default_groups = ['G1','G2','G3','G4','G5','G6']
    
    output_string = ""
    group_headers = []
    for line in input_summary_file:
        summary_line_count += 1
        if summary_line_count == 1:
            output_summary_file.write(line.rstrip() + "\tAllFiles\tAllGroups\tDefaultGroups\tRTMean\tRTStdErr\tProteoSAFeClusterLink\tUniqueFileSourcesCount\tEvenOdd" + "\n")
            group_headers = line.split("\t")
            for i in range(len(group_headers)):
                group_headers[i] = group_headers[i].rstrip().lstrip()
            continue
        cluster_number = line.split("\t")[0]
        spectra_count = int(line.split("\t")[1])
        
        #Filtering on minimum Spectra
        if spectra_count < CLUSTER_MIN_SIZE:
            continue
        
        #print cluster_number
        #print spectra_count
        
        line_splits = line.split("\t")
        #print line_splits
        group_string = ""
        for i in range(6,len(line_splits)):
            #print line_splits[i]
            if int(line_splits[i]) > 0:
                if group_headers[i].find("EXCLUDEGROUP") != -1 or (group_headers[i] in default_groups):
                    continue
                group_string += group_headers[i].rstrip() + ","
                
        default_group_string = ""
        for i in range(6,len(line_splits)):
            #print line_splits[i]
            #print group_headers[i]
            #print default_groups
            if int(line_splits[i]) > 0:
                if (group_headers[i] in default_groups):
                    default_group_string += group_headers[i].rstrip() + ","
        
        #print spectra_list[int(cluster_number)]
        spectra_list_string = ""
        for spectra_string in spectra_list[int(cluster_number)]:
            spectra_list_string += spectra_string
            
        #Calculating RT Stats    
        RT_Total = 0.0
        for RT_value in spectra_retention_times[int(cluster_number)]:
            RT_Total += RT_value
        
        
        RT_mean = RT_Total / len(spectra_retention_times[int(cluster_number)])
        RT_Variance = 0.0
        for RT_value in spectra_retention_times[int(cluster_number)]:
            RT_Variance += (RT_mean - RT_value)*(RT_mean - RT_value)
        if(len(spectra_retention_times[int(cluster_number)]) == 1):
            RT_Variance = 0.0;
        else:
            RT_Variance = RT_Variance / (len(spectra_retention_times[int(cluster_number)]) - 1)
        RT_StdDev = math.sqrt(RT_Variance);
            
        if(len(group_string) == 0):
            group_string = " "
            
        if(len(default_group_string) == 0):
            default_group_string = " "
            
        myset = set(cluster_file_list[int(cluster_number)])
        
        precursor = float(line_splits[2])
        charge = int(line_splits[3])
        if charge == 0:
            charge = 1
        even_odd_number = precursor - charge
        even_odd_number = even_odd_number * 0.9995
        even_odd_value = int(even_odd_number) % 2
        
        
        
        proteosafe_link = proteosafe_host + "/ProteoSAFe/result.jsp?task=" + get_param_value(key_value_pairs, "task", "none") + "&view=cluster_details&protein=" + cluster_number
        output_summary_file.write(line.rstrip() + "\t" + spectra_list_string + "\t" + group_string + "\t" + default_group_string + "\t" + str(RT_mean) + "\t" + str(RT_StdDev) + "\t" + proteosafe_link + "\t" + str(len(myset)) + "\t" + str(even_odd_value) + "\n")
        
        
    #    print spectra_map[line.split("\t")[0]]
        
    
    
    
if __name__ == "__main__":
    main()
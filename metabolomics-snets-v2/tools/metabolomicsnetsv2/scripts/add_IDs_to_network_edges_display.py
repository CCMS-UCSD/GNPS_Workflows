#!/usr/bin/python


import sys
import getopt
import os
import math

class PeptideSpectruMatch:
    file_name = ""
    scan_num = -1
    identification = ""
    score = -1
    organism = ""
    def __repr__(self):
        return str(self.file_name) + "\t" + str(self.scan_num) + "\t" + str(self.identification) + "\t" + str(self.score)
    
class PeptideSpectrumMatchSet:
    identifications = []
    
    def create_map(self):
        identification_map = {}
        for psm in self.identifications:
            key = str(psm.scan_num)
            if key in identification_map:
                identification_map[key].append(psm)
            else:
                identification_map[key] = [psm]
        
        return identification_map
                
    def top_scoring_per_spectrum(self):
        top_scoring = PeptideSpectrumMatchSet()
        identification_map = self.create_map()
        for key in identification_map.keys():
            max_psm = PeptideSpectruMatch()
            for identification in identification_map[key]:
                if max_psm.score < identification.score:
                    max_psm = identification
                    print str(max_psm) + " max scoring"
            top_scoring.identifications.append(max_psm)
        return top_scoring
    
    def __init__(self):
        pass
        
    @staticmethod
    def PSMSet_File_Factory(input_ID_file):
        psms = PeptideSpectrumMatchSet()
        
        ID_line_count = 0
        
        filename_index = -1
        scan_index = -1
        ID_index = -1
        score_index = -1
        organism_index = -1
        for line in input_ID_file:
            if ID_line_count == 0:
                ID_headers = line.rstrip().split("\t");
                filename_index = get_header_index(ID_headers, "SpectrumFile")
                scan_index = get_header_index(ID_headers, "#Scan#")
                ID_index = get_header_index(ID_headers, "Compound_Name")
                score_index = get_header_index(ID_headers, "MQScore")
                organism_index = get_header_index(ID_headers, "Organism")
                
                #print ID_headers
                #print filename_index
                #print scan_index
                #print ID_index
                #print score_index
                ID_line_count += 1
                continue
            #print line
            line_splits = line.split("\t")
            psm = PeptideSpectruMatch();
            psm.file_name = line_splits[filename_index]
            psm.scan_num = line_splits[scan_index]
            psm.identification = line_splits[ID_index]
            psm.score = line_splits[score_index]
            psm.organism = line_splits[organism_index]
            
            psms.identifications.append(psm)
            print psm
            
            continue
        return psms
        

def usage():
    print "<input pairs> <input IDs> <output clustersummary>"
    

def get_header_index(headers, search_header):
    index = 0
    for i in range(len(headers)):
        if headers[i].rstrip() == search_header:
            print "FOUND " + search_header
            return i
            
def get_file_mapping(param_file):
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
    return file_mapping

def main():
    usage()
    
    input_pairs_file = open(sys.argv[1], "r")
    input_ID_file = open(sys.argv[2], "r")
    output_summary_file = open(sys.argv[3], "w")
    
    
    print "READING ID FILE"
    psm_set = PeptideSpectrumMatchSet.PSMSet_File_Factory(input_ID_file)
    all_psms_map = psm_set.create_map()
    top_1_psm_map = psm_set.top_scoring_per_spectrum().create_map()
    print top_1_psm_map
    
    pairs_line_count = 0
    for line in input_pairs_file:
        pairs_line_count += 1
        if pairs_line_count == 1:
            output_summary_file.write(line.rstrip() + "\tLibraryID" + "\n")
            continue;
        cluster_number = line.split("\t")[1]
        filename = line.split("\t")[4].rstrip()
        output_summary_file.write(line.rstrip())
        spectrum_key =  str(cluster_number)
        print spectrum_key
        if spectrum_key in top_1_psm_map:
            output_summary_file.write("\t" +  top_1_psm_map[spectrum_key][0].identification + "\n")
        else:
            output_summary_file.write("\t" +  " " + "\n")
      
    
    return 0
    
        
        
        
    
        
    
    
    
if __name__ == "__main__":
    main()

#!/usr/bin/python


import sys
import getopt
import os



def usage():
    print "<input group file> <flowparams> <output group file>"
    

    
    
def main():
    #usage()
    file_path_prefix = "inputspectra/"
    
    print sys.argv
    print len(sys.argv)
    
    #if len(sys.argv) == 3:
    #  open(sys.argv[2], "w").close()
    #  return
    
    #if len(sys.argv[1]) < 2:
    #  open(sys.argv[3], "w").close()
    #  return
    
    flowparams_idx = 2;
    if len(sys.argv) == 3:
        flowparams_idx = 1

    
    flowparams = open(sys.argv[flowparams_idx])
    
    file_mapping = {}
    all_mangled_files = []
    
    for line in flowparams:
        if line.find("upload_file_mapping") != -1:
            #print line.rstrip()
            parsed = line[len("<parameter name=\"upload_file_mapping\">"):].rstrip()
            parsed = parsed[: - len("</parameter>")]
            print parsed
            split_mapping = parsed.split("|")

            if (len(split_mapping) == 2):
                file_key = os.path.basename(split_mapping[1])
                file_mapping[file_key] = split_mapping[0]
                all_mangled_files.append(split_mapping[0])
      
    print file_mapping
    print all_mangled_files
    
    #opening output file
    output_file_arg_idx = 3;
    if len(sys.argv) == 3:
        output_file_arg_idx = 2

    
    if len(sys.argv[1]) < 2:
        output_file_arg_idx = 3

    output_group_file = open(sys.argv[output_file_arg_idx], "w")
    print "WRITING FILE: " + sys.argv[output_file_arg_idx]
    
    #Grouping default groups
    default_groupings = {'G1' : [] , 'G2' : [] ,'G3' : [] ,'G4' : [] ,'G5' : [] ,'G6' : [] }
    for mangled_name in all_mangled_files:
        if mangled_name.find("spec-") != -1:
            default_groupings['G1'].append(mangled_name.rstrip())
        if mangled_name.find("spectwo-") != -1:
            default_groupings['G2'].append(mangled_name.rstrip())
        if mangled_name.find("specthree-") != -1:
            default_groupings['G3'].append(mangled_name.rstrip())
        if mangled_name.find("specfour-") != -1:
            default_groupings['G4'].append(mangled_name.rstrip())
        if mangled_name.find("specfive-") != -1:
            default_groupings['G5'].append(mangled_name.rstrip())
        if mangled_name.find("specsix-") != -1:
            default_groupings['G6'].append(mangled_name.rstrip())
        
    for default_group_key in default_groupings.keys():
        default_group_string = ""
        default_group_string += "GROUP_" + default_group_key +"="
        for mangled_name in default_groupings[default_group_key]:
            default_group_string += file_path_prefix + mangled_name + ";"
        if len(default_groupings[default_group_key]) > 0:
            default_group_string = default_group_string[:-1]
        output_group_file.write(default_group_string + "\n")
        print default_group_string
    
    
    #Checking if input file exists
    if (len(sys.argv) == 3) or (len(sys.argv[1]) < 2):
        return

    input_group_file = open(sys.argv[1])
    
    files_mapped = 0
    for line in input_group_file:
      #print line.rstrip()
      splits = line.rstrip().split("=")
      
      if len(splits) < 2:
        continue
      
      #print splits
      file_names = splits[1:]
      #print file_names[0].split(",")
      output_line = splits[0] + "="
      for file_name in file_names[0].split(";"):
        #print file_name
        if file_name in file_mapping.keys():
          #print file_mapping[file_name]
          output_line += (file_path_prefix + file_mapping[file_name] + ';')
          files_mapped += 1
          
      if files_mapped > 0:
          output_line = output_line[:-1]
      print output_line
      output_group_file.write(output_line + "\n")

      
    
if __name__ == "__main__":
    main()
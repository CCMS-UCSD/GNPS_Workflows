#!/usr/bin/python


import sys
import getopt
import os
import shutil


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
          

        if(splits[0] in key_value_pairs.keys()):
          key_value_pairs[splits[0]].append(splits[1])
        else:
          key_value_pairs[splits[0]] = []
          key_value_pairs[splits[0]].append(splits[1])
        
        
    return key_value_pairs

def get_mangled_file_mapping(params):
    all_mappings = params["upload_file_mapping"]
    mangled_mapping = {}
    for mapping in all_mappings:
        #print mapping
        splits = mapping.split("|")
        mangled_name = splits[0]
        original_name = splits[1]
        mangled_mapping[mangled_name] = original_name
    
    return mangled_mapping


def usage():
    print "<input folder> <executable path> <params file>"




def main():
    #usage()

    input_folder_path = sys.argv[1]
    output_folder_path = "temp_converted"
    convert_path = sys.argv[2]
    
    params = parse_xml_file(open(sys.argv[3], 'r'))
    manged_mapping = get_mangled_file_mapping(params)
    
    
    os.mkdir(output_folder_path)
    
    files = os.listdir(input_folder_path)
    
    input_output_map = {};
    all_input_files = []
    
    for input_file in files:
      fileName, fileExtension = os.path.splitext(input_file)
      input_file_param = input_folder_path + "/" + input_file
      output_file_param = output_folder_path + "/" + fileName + ".pklbin"
      cmd = convert_path + " " + input_file_param + " " + output_file_param
      
      input_output_map[input_file_param] = output_file_param
      all_input_files.append(input_file_param)
      cmd += " 2> /dev/null > /dev/null"
      #print cmd
      os.system(cmd)
      
    exit_in_error = False;
    for input_file in all_input_files:
        if (not os.path.isfile(input_output_map[input_file])):
            print manged_mapping[os.path.basename(input_file)] + " is not loadable, please check it out"
            exit_in_error = True;
            continue;
        if (os.path.getsize(input_output_map[input_file]) < 100):
            print manged_mapping[os.path.basename(input_file)] + " is not loadable, please check it out"
            exit_in_error = True;
            continue;
        
    shutil.rmtree(output_folder_path)
    if exit_in_error:
        print "Exiting in Error"
        #exit(1)
    return 0
        
    
    

if __name__ == "__main__":
    main()

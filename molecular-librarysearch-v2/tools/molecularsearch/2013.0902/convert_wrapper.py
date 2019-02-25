#!/usr/bin/python


import sys
import getopt
import os



def usage():
    print "<input folder> <output folder> <executable path>"




def main():
    usage()

    input_folder_path = sys.argv[1]
    output_folder_path = sys.argv[2]
    convert_path = sys.argv[3]

    files = os.listdir(input_folder_path)

    for input_file in files:
        fileName, fileExtension = os.path.splitext(input_file)
        print(fileExtension)
        if input_file.find("mzXML") != -1 or input_file.find("mzxml") != -1 or input_file.find("mzML") != -1:
            cmd = convert_path + " " + input_folder_path + "/" + input_file + " " + output_folder_path + "/" + fileName + ".pklbin"
        else:
            cmd = "cp " + input_folder_path + "/" + input_file + " " + output_folder_path + "/" + input_file
        #print cmd
        os.system(cmd)

if __name__ == "__main__":
    main()

import os
import sys
import shutil
import xmltodict as xtd

OUTPUT_DIR_INDEX = -1

if __name__ == '__main__':
    print("===PARSE OUTPUT===")

    openms_output = ["iniFiles", "featurelinkerunlabeled", "filefilter", "textexporter", "gnpsexport"]
    download_all_files = ["featurefindermetabo", "idmapper", "mapalignerposeclustering", "metaboliteadductdecharger"]

    #debug what folders are left
    # print os.listdir(os.path.abspath('.'))
    print("current dir...")
    for dir in os.listdir(os.path.abspath('.')):
        if len(os.listdir(os.path.abspath(dir))) > 0:
            print("\t", dir, os.listdir(os.path.abspath(dir)))

    #parse output diretory
    print(sys.argv[OUTPUT_DIR_INDEX])
    output_dir = sys.argv[OUTPUT_DIR_INDEX]

    #download openms output
    # os.mkdir(output_dir+'/openms-output')
    for dir in openms_output:
        # os.mkdir('openms-output/'+dir)
        shutil.copytree(os.path.abspath(dir), os.path.abspath(sys.argv[OUTPUT_DIR_INDEX]+"/openms_output/"+dir))
        # shutil.copytree(os.path.abspath(dir), os.path.abspath(sys.argv[OUTPUT_DIR_INDEX]+dir))


    # os.system("echo 'hello' > " + str(sys.argv[OUTPUT_DIR_INDEX]) + "/log.txt")
    print("\n\n\n"+sys.argv[OUTPUT_DIR_INDEX], os.listdir(sys.argv[OUTPUT_DIR_INDEX]))

    #download all files
    # os.mkdir(output_dir+'/download-all-files')
    for dir in download_all_files:
        shutil.copytree(os.path.abspath(dir), os.path.abspath(sys.argv[OUTPUT_DIR_INDEX]+'/workflow_files/'+dir))

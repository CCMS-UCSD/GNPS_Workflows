import os
import shutil
import sys
import xmltodict as xtd

'''
#6 module: gnps export
'''
def gnpssiriusexport(featurelinker_file, inputFiles_port, ini_file, output_type, out_port):
    in_cm = featurelinker_file

    # in_cm = in_port+'/'+get_port_outputs(in_port)[0]
    output = out_port + '/' + "gnpsexport.mgf"
    # in_cm = in_port+'/'+get_port_outputs(in_port)[0]
    output = out_port + '/' + "gnpssiriusexport.mgf"

    command = "GNPSSiriusExport -ini " + ini_file + " -in_cm " + in_cm + " -in_mzml "
    for file in os.listdir(inputFiles_port):
        command += inputFiles_port+'/'+file + " "
    command += "-out " + output + " -output_type " + output_type + ' >> ' + out_port+'/logfile.txt'

    print("COMMAND: " + command + "\n")
    os.system(command)



if __name__ == '__main__':
    print("===GNPS SIRIUS EXPORT===")

    # set env
    if os.environ.has_key("LD_LIBRARY_PATH"):
        os.environ["SANS_LD_LIBRARY_PATH"] = os.environ["LD_LIBRARY_PATH"]
    os.environ["LD_LIBRARY_PATH"] = "/data/beta-proteomics2/tools/openms_2.4/openms-env/conda/lib"

    if os.environ.has_key("PATH"):
        os.environ["SANS_PATH"] = os.environ["PATH"]
    os.environ["PATH"] = "/data/beta-proteomics2/tools/openms_2.4/openms-env/conda/bin:/data/beta-proteomics2/tools/openms_2.4/openms-env/openms-build/bin:$PATH"

    openms_data_path = '/data/beta-proteomics2/tools/openms_2.4/openms-env/share'
    os.environ["OPENMS_DATA_PATH"] = os.path.abspath(openms_data_path)

    # output type
    output_type = 'merged_spectra'
    with open(sys.argv[3], 'r') as fp:
        params = xtd.parse(fp.read())
        for param in params['parameters']['parameter']:
            if param['@name'] == "gnpsexport.output_type":
                output_type = param['#text']


    curr_dir = os.listdir('.')
    print(curr_dir)
    for dir in curr_dir:
        print(dir+":")
        print(os.listdir(dir))


    # ini file
    ini_file = 'iniFiles/'+os.listdir('iniFiles')[0]
    # shutil.copyfile(ini_file, sys.argv[3])

    gnpssiriusexport(sys.argv[1], sys.argv[2], ini_file, output_type, sys.argv[5])

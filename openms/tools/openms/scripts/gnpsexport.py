import os
import shutil
import sys
import xmltodict as xtd
import openms_workflow as wrkflw


'''
#6 module: gnps export
'''
def gnpsexport(input_port, inputFiles_port, ini_file, out_port):
    for input_file,file_count in list(wrkflw.parsefolder(input_port, whitelist=['consensusXML'])):
        output = out_port+'/'+out_port+"-"+file_count+".mgf"

        command = "GNPSExport"
        if ini_file is not None:
            command += " -ini " + ini_file
        command += " -in_cm " + input_file + " -in_mzml"
        # command = "GNPSExport -ini " + ini_file + " -in_cm " + input_file + " -in_mzml "

        file_maps = dict()
        with open(input_file, 'r') as fp:
            params = xtd.parse(fp.read())
            for map in params['consensusXML']['mapList']['map']:
                # print (map['@id'], map['@name'])
                file_maps[int(map['@id'])] = map['@name']

        for input_file,file_count in sorted(list(wrkflw.parsefolder(inputFiles_port, whitelist=['mzML']))):
            command += " " + input_file
        command += " -out " + output
        command += '> ' + out_port+'/logfile-00000.txt'
        # command += ' -log ' + out_port+'/logfile-00000.txt'

        print("COMMAND: " + command + "\n")
        os.system(command)



if __name__ == '__main__':
    print("===GNPS EXPORT===")

    # set env
    os.environ["LD_LIBRARY_PATH"] = "{}:{}".format(sys.argv[1],sys.argv[2])    
    os.environ["PATH"] = "{}:{}".format(sys.argv[3],sys.argv[4])
    os.environ["OPENMS_DATA_PATH"] = os.path.abspath(sys.argv[5])

    in_port = sys.argv[6]
    inputFiles_port = sys.argv[7]
    out_port = sys.argv[9]


    # ini file = sys.argv[8]
    ini_file = None
    if os.path.exists('iniFiles'):
        ini_dir = list(wrkflw.parsefolder('iniFiles'))
        if len(ini_dir) > 0:
            ini_file = ini_dir[0][0]
    # shutil.copyfile(ini_file, sys.argv[3])

    gnpsexport(in_port, inputFiles_port, ini_file, out_port)

    # wrkflw.postvalidation( \
    #   modulename="gnps export", \
    #   inpath=in_port, \
    #   outpath=out_port, \
    #   logtype=wrkflw.LogType.SINGLE, \
    #   output_per_job=0
    # )

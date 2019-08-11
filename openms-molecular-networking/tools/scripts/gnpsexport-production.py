import os
import shutil
import sys
import xmltodict as xtd
import openms_workflow as wrkflw


def parse_folder(dir):
    if not os.path.exists(dir):
        yield None
    for file in sorted(os.listdir(dir)):
        if "log" not in file:
            yield (dir+"/"+file, os.path.splitext(file)[0].split('-')[1])


'''
#6 module: gnps export
'''
def gnpsexport(input_port, inputFiles_port, ini_file, out_port):
    assert len(list(parse_folder(input_port))) > 0

    for input_file,file_count in list(parse_folder(input_port)):
        output = out_port+'/'+out_port+"-"+file_count+".mgf"

        command = "GNPSExport-prod "
        if ini_file is not None:
            command += "-ini " + ini_file + " "
        command += "-in_cm " + input_file + " -in_mzml "
        # command = "GNPSExport -ini " + ini_file + " -in_cm " + input_file + " -in_mzml "

        file_maps = dict()
        with open(input_file, 'r') as fp:
            params = xtd.parse(fp.read())
            for map in params['consensusXML']['mapList']['map']:
                # print (map['@id'], map['@name'])
                file_maps[int(map['@id'])] = map['@name']

        for input_file,file_count in sorted(list(parse_folder(inputFiles_port))):
            command += input_file + " "
        command += "-out " + output + ' '
        command += '> ' + out_port+'/logfile.txt'
        # command += '-log ' + out_port+'/logfile.txt'

        print("COMMAND: " + command + "\n")
        os.system(command)



if __name__ == '__main__':
    print("===GNPS EXPORT===")

    # set env
    os.environ["LD_LIBRARY_PATH"] = sys.argv[1]
    os.environ["PATH"] = sys.argv[2]
    os.environ["OPENMS_DATA_PATH"] = os.path.abspath(sys.argv[3])

    in_port = sys.argv[4]
    inputFiles_port = sys.argv[5]
    out_port = sys.argv[7]


    # ini file
    ini_file = None
    if os.path.exists('iniFiles'):
        ini_dir = list(parse_folder('iniFiles'))
        if len(ini_dir) > 0:
            ini_file = ini_dir[0][0]
    # shutil.copyfile(ini_file, sys.argv[3])

    gnpsexport(in_port, inputFiles_port, ini_file, out_port)

    # wrkflw.postvalidation(modulename="gnps-export", outpath=out_port)

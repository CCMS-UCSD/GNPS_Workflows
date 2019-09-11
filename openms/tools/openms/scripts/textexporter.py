import os
import shutil
import sys
import xmltodict as xtd

def parse_folder(dir):
    if not os.path.exists(dir):
        yield None
    for file in os.listdir(dir):
        if "log" not in file:
            yield (dir+"/"+file, os.path.splitext(file)[0].split('-')[1])

'''
#6 module: text export
'''
def textexporter(input_port, ini_file, out_port):
    assert len(list(parse_folder(input_port))) > 0
    for input_file,file_count in list(parse_folder(input_port)):
        # command = "TextExporter -ini " + ini_file + " -in " + input_file + " -out " + out_port+'/'+out_port+'-'+file_count+'.csv' + ' >> ' + out_port+'/logfile.txt'
        command = "TextExporter -ini " + ini_file + " -in " + input_file + " -out " + out_port+'/'+out_port+'-'+file_count+'.csv' + ' -log ' + out_port+'/logfile.txt'

        print("COMMAND: " + command + "\n")
        os.system(command)

    # with open(out_port+'/textexporter.csv', "rt") as fin:
    #     with open(out_port+'/textexporter_mapped.csv', "wt") as fout:
    #         for line in fin:
    #             if "MAP" in line:
    #                 fout.write(line)



if __name__ == '__main__':
    print("===TEXT EXPORTER===")

    # set env
    os.environ["LD_LIBRARY_PATH"] = sys.argv[1]
    os.environ["PATH"] = sys.argv[2]
    os.environ["OPENMS_DATA_PATH"] = os.path.abspath(sys.argv[3])

    # ini file
    ini_file = None
    if os.path.exists('iniFiles'):
        ini_dir = list(parse_folder('iniFiles'))
        if len(ini_dir) > 0:
            ini_file = ini_dir[0][0]

    textexporter(sys.argv[4], ini_file, sys.argv[6])

import os
import shutil
import sys
import multiprocessing as mp
from subprocess import Popen
import ming_parallel_library as mpl
import openms_workflow as wrkflw

def get_exec_cmd(input_file, file_count, out_port):
    output = out_port+'/'+out_port+'-'+file_count+'.mzML'

    command = 'FileConverter'
    command += ' -in ' + input_file + ' -out ' + output + ' -log ' + out_port+'/logfile-'+file_count+'.txt'

    print("COMMAND: " + command + '\n')
    return command


'''
#1 module: feature finder metabo
'''
def fileconverter(input_port, out_port):
    commands = []
    for input_file,file_count in wrkflw.parsefolder(input_port, blacklist=["log"]):
        if any([ext.lower() in input_file.lower() for ext in ['mzData', 'mzXML',\
                'cachedMzML', 'dta', 'dta2d', 'mgf', 'featureXML',\
                'consensusXML', 'ms2', 'fid', 'tsv', 'peplist', 'kroenik',\
                'edta']]):
          cmd = get_exec_cmd(input_file,file_count,out_port)
          commands.append(cmd)
        elif "mzml" in input_file.lower():
          shutil.copyfile(input_file, out_port+"/"+out_port+"-"+file_count+".mzML")
          os.system("echo \"original file format for {} is mzml\" >> {}".format(input_file,out_port+"/logfile-"+file_count+".txt"))
        else:
          continue
    mpl.run_parallel_shellcommands(commands,8)


if __name__ == '__main__':
    print("===CONVERT MZXML TO MZML===")

    # set env
    os.environ["LD_LIBRARY_PATH"] = sys.argv[1]
    os.environ["PATH"] = sys.argv[2]
    # os.environ["OPENMS_DATA_PATH"] = os.path.abspath(sys.argv[3])

    # ini file
    ini_file = None
    if os.path.exists('iniFiles'):
        ini_dir = list(wrkflw.parsefolder('iniFiles'))
        if len(ini_dir) > 0:
            ini_file = ini_dir[0][0]

    in_port = sys.argv[4]
    out_port = sys.argv[5]

    fileconverter(in_port, out_port)



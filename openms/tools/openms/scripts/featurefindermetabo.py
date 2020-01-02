import os
import shutil
import sys
import multiprocessing as mp
from subprocess import Popen
import ming_parallel_library as mpl
import openms_workflow as wrkflw


def get_exec_cmd(input_file, file_count, ini_file, out_port):
    output = out_port+'/'+out_port+'-'+file_count+'.featureXML'

    command = 'FeatureFinderMetabo '
    if ini_file is not None:
        command += '-ini ' + ini_file + ' '
    command += '-in ' + input_file + ' -out ' + output 
    command +=  '-algorithm:epd:enabled false'
    command += ' > ' + out_port+'/logfile-'+file_count+'.txt'    
    # command += '-in ' + input_file + ' -out ' + output + ' -log ' + out_port+'/logfile-'+file_count+'.txt'
    return command


'''
#1 module: feature finder metabo
'''
def featurefindermetabo(input_port, ini_file, out_port):
    commands = []
    for input_file,file_count in wrkflw.parsefolder(input_port, blacklist=['log']):
        cmd = get_exec_cmd(input_file,file_count,ini_file,out_port)
        commands.append(cmd)

    mpl.run_parallel_shellcommands(commands,8)


if __name__ == '__main__':
    print("===FEATURE FINDER METABO===")

    # print(sys.argv[1])
    # print(sys.argv[2])
    # print(sys.argv[3])

    # set env
    os.environ["LD_LIBRARY_PATH"] = sys.argv[1]
    os.environ["PATH"] = sys.argv[2]
    os.environ["OPENMS_DATA_PATH"] = sys.argv[3]

    # ini file
    ini_file = None
    if os.path.exists('iniFiles'):
        ini_dir = list(wrkflw.parsefolder('iniFiles'))
        if len(ini_dir) > 0:
            ini_file = ini_dir[0][0]

    # parse parameters
    in_port = sys.argv[4]
    out_port = sys.argv[6]

    # execute module
    featurefindermetabo(in_port, ini_file, out_port)

    wrkflw.postvalidation(modulename="feature finder metabo", inpath=in_port, outpath=out_port)

import os
import shutil
import sys
from subprocess import Popen
import ming_parallel_library as mpl
import openms_workflow as wrkflw


def get_exec_cmd(input_file, file_count, ini_file, out_port):
    command = "MetaboliteAdductDecharger"
    if ini_file is not None:
        command += " -ini " + ini_file
    command += " -in " + input_file
    command += " -out_fm " + out_port+'/'+out_port+'-'+file_count+'.featureXML'
    command += " -out_cm " + out_port+'/'+out_port+'-'+file_count+'.consensusXML'
    command += "> " + out_port+'/logfile-'+file_count+'.txt'
    # command += " -log " + out_port+'/logfile-'+file_count+'.txt'


    print("COMMAND: " + command + "\n")
    return command

'''
#4 module: metabolite adduct decharger
'''
def metaboliteadductdecharger(input_port, ini_file, out_port):
    commands = []
    for input_file,file_count in wrkflw.parsefolder(input_port, blacklist=['log']):
        cmd = get_exec_cmd(input_file,file_count,ini_file,out_port)
        commands.append(cmd)

    mpl.run_parallel_shellcommands(commands,8)

if __name__ == '__main__':
    print("===METABOLITE ADDUCT DECHARGER===")

    in_port = sys.argv[6]
    out_port = sys.argv[8]

    # set env
    os.environ["LD_LIBRARY_PATH"] = "{}:{}".format(sys.argv[1],sys.argv[2])    
    os.environ["PATH"] = "{}:{}".format(sys.argv[3],sys.argv[4])
    os.environ["OPENMS_DATA_PATH"] = os.path.abspath(sys.argv[5])

    # ini file
    ini_file = None
    if os.path.exists('iniFiles'):
        ini_dir = list(wrkflw.parsefolder('iniFiles'))
        if len(ini_dir) > 0:
            ini_file = ini_dir[0][0]

    metaboliteadductdecharger(in_port, ini_file, out_port)

    wrkflw.postvalidation( \
      modulename="metabolite adduct decharger", \
      inpath=in_port, \
      outpath=out_port, \
      output_per_job=2
    )

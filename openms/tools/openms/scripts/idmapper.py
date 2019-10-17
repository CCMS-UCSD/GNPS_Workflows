import os
import shutil
import sys
from subprocess import Popen
import ming_parallel_library as mpl
import openms_workflow as wrkflw


def get_exec_cmd(input_file, file_count, ini_file, idxml_path, input_port, out_port):
    command = 'IDMapper '
    if ini_file is not None:
        command += '-ini ' + ini_file + ' '
    command += '-in ' + input_file + ' -id ' + idxml_path + ' '
    command += '-spectra:in ' + input_port+'/'+input_port+'-'+file_count+".mzML "
    command += '-out ' + out_port+'/'+out_port+'-'+file_count+'.featureXML '
    command += '> ' + out_port+'/logfile-'+file_count+'.txt'
    # command += '-log ' + out_port+'/logfile-'+file_count+'.txt'


    print("COMMAND: " + command + '\n')
    return command


'''
#2 module: id mapper
'''
def idmapper(input_port, ini_file, idxml_path, featurefinder_port, out_port):
    commands = []
    for input_file,file_count in wrkflw.parsefolder(featurefinder_port, blacklist=['log']):
        cmd = get_exec_cmd( \
          input_file, \
          file_count, \
          ini_file, \
          idxml_path, \
          input_port, \
          out_port
        )
        commands.append(cmd)

    mpl.run_parallel_shellcommands(commands,8)


if __name__ == '__main__':
    print("===ID Mapper===")

    mzml_port = sys.argv[4]
    featurefinder_port = sys.argv[7]
    out_port = sys.argv[8]

    # validate previous module output
    # wrkflw.prevalidation("feature-finder-metabo", featurefinder_port)

    # set env
    os.environ["LD_LIBRARY_PATH"] = sys.argv[1]
    os.environ["PATH"] = sys.argv[2]
    os.environ["OPENMS_DATA_PATH"] = os.path.abspath(sys.argv[3])

    # ini file
    ini_file = None
    if os.path.exists('iniFiles'):
        ini_dir = list(wrkflw.parsefolder('iniFiles'))
        if len(ini_dir) > 0:
            ini_file = ini_dir[0][0]

    idmapper(mzml_port, ini_file, sys.argv[6], featurefinder_port, out_port)

    wrkflw.postvalidation(modulename="id mapper", inpath=mzml_port, outpath=out_port)

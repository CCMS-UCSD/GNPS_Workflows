import os
import shutil
import sys
import openms_workflow as wrkflw

'''
#3 module: map aligner pose clustering
'''
def mapalignerposeclustering(input_port, ini_file, out_port):
    command = "MapAlignerPoseClustering"
    if ini_file is not None:
        command += " -ini " + ini_file

    command += " -in"
    outputs = []
    for input_file,file_count in wrkflw.parsefolder(input_port, blacklist=['log']):
        command += ' {}'.format(input_file)
        outputs.append("{out}/{out}-{filec}.featureXML ".format(out=out_port,filec=file_count))
        # command += input_file + ' '
    command += '-out' + ' '.join(outputs)
    # command += '> ' + out_port+'/logfile-00000.txt'
    command += '-log ' + out_port+'/logfile-00000.txt'

    print("COMMAND: " + command + "\n")
    os.system(command)


if __name__ == '__main__':
    print("===MAP ALIGNER POSE CLUSTERING===")

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


    mapalignerposeclustering(in_port, ini_file, out_port)

    wrkflw.postvalidation(modulename="map aligner pose-clustering", \
      inpath=in_port, \
      outpath=out_port, \
      logtype=wrkflw.LogType.SINGLE
    )

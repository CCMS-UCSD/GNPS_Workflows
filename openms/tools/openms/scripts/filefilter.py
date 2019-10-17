import os
import shutil
import sys
import xmltodict as xtd
import openms_workflow as wrkflw


'''
#6 module: gnps export
'''
def filefilter(input_port, out_port):
    #only one job
    for input_file,file_count in wrkflw.parsefolder(input_port, blacklist=['log']):
        # in_cm = in_port+'/'+get_port_outputs(in_port)[0]
        output = out_port+'/'+out_port+"-"+file_count+".consensusXML"

        command = "FileFilter -id:remove_unannotated_features -in " + input_file + " "
        command += "-out " + output + ' '
        command += '> ' + out_port+'/logfile-00000.txt'
        # command += '-log ' + out_port+'/logfile-00000.txt'

        print("COMMAND: " + command + "\n")
        os.system(command)



if __name__ == '__main__':
    print("===FILE FILTER===")

    in_port = sys.argv[4]
    out_port = sys.argv[5]

    # validate previous module's output
    # wrkflw.prevalidation("feature-linker-unlabeled", in_port, logtype="single", output_per_job=0)

    # set env
    os.environ["LD_LIBRARY_PATH"] = sys.argv[1]
    os.environ["PATH"] = sys.argv[2]
    os.environ["OPENMS_DATA_PATH"] = os.path.abspath(sys.argv[3])

    filefilter(sys.argv[4], sys.argv[5])

    wrkflw.postvalidation( \
      modulename="file filter", \
      inpath=in_port, \
      outpath=out_port, \
      logtype=wrkflw.LogType.SINGLE, \
      output_per_job=1
    )

import os
import shutil
import sys
import xmltodict as xtd
import openms_workflow as wrkflw


'''
#6 module: text export
'''
def textexporter(input_port, ini_file, out_port):
  for input_file,file_count in list(wrkflw.parsefolder(input_port, blacklist=['log'])):
    command = "TextExporter -ini " + ini_file + " -in " + input_file + " -out " + out_port+'/'+out_port+'-'+file_count+'.csv' + ' -log ' + out_port+'/logfile-00000.txt'
    # command = "TextExporter -ini " + ini_file + " -in " + input_file + " -out " + out_port+'/'+out_port+'-'+file_count+'.csv' + ' > ' + out_port+'/logfile-00000.txt'

    print("COMMAND: " + command + "\n")
    os.system(command)


if __name__ == '__main__':
  print("===TEXT EXPORTER===")

  # set env
  os.environ["LD_LIBRARY_PATH"] = "{}:{}".format(sys.argv[1],sys.argv[2])
  os.environ["PATH"] = "{}:{}".format(sys.argv[3],sys.argv[4])
  os.environ["OPENMS_DATA_PATH"] = os.path.abspath(sys.argv[5])

  # ini file = sys.argv[7]
  ini_file = None
  if os.path.exists('iniFiles'):
    ini_dir = list(wrkflw.parsefolder('iniFiles'))
    if len(ini_dir) > 0:
      ini_file = ini_dir[0][0]

  textexporter(sys.argv[6], ini_file, sys.argv[8])

import os
import shutil
import sys
import xmltodict as xtd
import openms_workflow as wrkflw

'''
#5 module: feature linker unlabeled kd
'''
def featurelinkerunlabeledkd(input_port, ini_file, out_port):
    command = "FeatureLinkerUnlabeledKD "
    if ini_file is not None:
        command += "-ini " + ini_file + " "
    command += "-in "
    for input_file,file_count in wrkflw.parsefolder(input_port,whitelist=["featureXML"]):
        command += input_file + " "
    command += "-out " + out_port+"/"+out_port+"-00000.consensusXML "
    command += '> ' + out_port+'/logfile-00000.txt'
    # command += '-log ' + out_port+'/logfile-00000.txt'

    print("COMMAND: " + command + "\n")
    os.system(command)

    # delete featureXML file
    # if os.path.exists(out_port+"/featurelinker-tmp.consensusXML"):
    #     os.remove(out_port+"/featurelinker-tmp.consensusXML")


'''
#5 module: feature linker unlabeled qt
'''
def featurelinkerunlabeledqt(input_port, ini_file, out_port):
    command = "FeatureLinkerUnlabeledQT "
    if ini_file is not None:
        command += "-ini " + ini_file + " "
    command += "-in "
    for input_file,file_count in wrkflw.parsefolder(input_port, whitelist=["featureXML"]):
        command += input_file + " "
    command += "-out " + out_port+"/"+out_port+"-00000.consensusXML "
    command += '-log ' + out_port+'/logfile-00000.txt'

    print("COMMAND: " + command + "\n")
    os.system(command)


def fix_filenames(out_port, mapping_file):
    print("correcting filenames in featurelinker step...")

    files = dict()
    with open(mapping_file) as f:
        file_dict = xtd.parse(f.read())
        for map_line in file_dict['parameters']['parameter']:
            if "upload_file_mapping" in map_line['@name'] and "inputFiles" in map_line['#text']:
                map = map_line['#text'].split('|')
                raw_file_path = os.path.splitext(map[0])[0].split('-')[1]

                print("mapping",raw_file_path,"->",map[1])
                files[int(raw_file_path)] = map[1]

    # print(list(wrkflw.parsefolder(out_port)))
    for input_file,file_count in wrkflw.parsefolder(out_port):
        with open(input_file) as f:
            file_dict = xtd.parse(f.read())

        for map in file_dict['consensusXML']['mapList']['map']:
            print("\tid:", map['@id'], '\t', map['@name'], '\t-->\t', files[int(map['@id'])])
            map['@name'] = files[int(map['@id'])]

        # export file_dict
        out = xtd.unparse(file_dict, pretty=True)
        with open(input_file, 'w') as file:
            file.write(out)

    print("out port dir:", os.listdir(out_port))


if __name__ == '__main__':
    print("\n==FEATURE LINKER UNLABELED QT==")

    in_port = sys.argv[4]
    out_port = sys.argv[6]

    # validate previous module's output
    # wrkflw.prevalidation("metabolite-adduct-decharger",in_port,output_per_job=2)

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

    # tool type
    linker_tool = "Feature Linker Unlabeled QT"
    with open(sys.argv[7], "r") as f:
        params = xtd.parse(f.read())
        for param in params['parameters']['parameter']:
            if param['@name'] == "featurelinkerunlabeled.tool_type":
                linker_tool = param['#text']

    if linker_tool == "Feature Linker Unlabeled QT":
        featurelinkerunlabeledqt(in_port, ini_file, out_port)
    else:
        featurelinkerunlabeledkd(in_port, ini_file, out_port)

    # wrkflw.postvalidation(modulename="feature-linker-unlabeled", outpath=out_port,\
    # logtype="single", output_per_job=0)

    fix_filenames(out_port, sys.argv[7])

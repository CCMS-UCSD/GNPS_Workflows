'''
This workflow script was intended to integrate OpenMS modules with GNPS.

The workflow operates as follows:
1.  mzml(s)          -> FeatureFinderMetabo          -> featureXML(s)
    featureXML(s)    -> IDMapper                     -> featureXML(s)
2.  featureXML(s)    -> MapAlignerPoseClustering     -> featureXML(s)
3.  featureXML       -> FeautureLinkerUnlabeledKD    -> consensusXML
    consensusXML     -> FileConverter                -> featureXML
4.  featureXML       -> MetaboliteAdductDecharger    -> featureXML & consensusXML
5.  consensusXML     -> GNPSExport                   -> mgf
'''

import os
import shutil
import sys
import xmltodict as xtd


def_ini_dir = "/data/beta-proteomics2/tools/openms/ini-steps"

command_dir = "/data/beta-proteomics2/tools/openms/openms-env/openms-build/bin/"

'''
#1 module: feature finder metabo
'''
def featurefindermetabo(input_port, ini_file, out_port):
    for file in os.listdir(input_port):
        filename = os.path.splitext(file)[0].split('-')[1]
        # output = curr_port + '/out-' + filename + '.featureXML'
        output = out_port + '/featurefinder-' + filename + '.featureXML'

        command = 'FeatureFinderMetabo -ini ' + ini_file + ' -in ' + input_port+'/'+file + ' -out ' + output + ' >> ' + out_port+'/logfile.txt'

        print("COMMAND: " + command + '\n')
        os.system(command)


'''
#2 module: id mapper
'''
def idmapper(input_port, ini_file, idxml_path, featurefinder_port, out_port):
    print("\n==ID MAPPER==")
    for file in os.listdir(featurefinder_port):
        print(file)
        filename = ""
        if 'log' not in file:
            filename = os.path.splitext(file)[0].split('-')[1]
        else:
            continue

        input = featurefinder_port + '/' + file
        # input = featurefindermetabo_port + '/featurefinder-' + filename + '.featureXML'
        output = out_port + '/idmapper-' + filename + '.featureXML'
        # output = curr_port + '/out-' + filename + '.featureXML'

        command = 'IDMapper -ini ' + ini_file + ' -in ' + input + ' -id ' + idxml_path + ' -spectra:in '
        command += input_port+'/'+os.listdir(input_port)[int(filename)] + ' '
        # command += input_port+'/'+file + ' '
        command += '-out ' + output + ' >> ' + out_port+'/logfile.txt'

        print("COMMAND: " + command + '\n')
        os.system(command)


'''
#3 module: map aligner pose clustering
'''
def mapalignerposeclustering(idmapper_port, ini_file, out_port):
    command = "MapAlignerPoseClustering -ini " + ini_file + " -in "
    output = ""

    for file in os.listdir(idmapper_port):
        if 'log' not in file:
            command += idmapper_port+'/'+file + ' '

    command += '-out '
    for file in os.listdir(idmapper_port):
        if 'log' not in file:
            filename = os.path.splitext(file)[0].split('-')[1]
            command += out_port+"/mapaligner-"+filename+".featureXML "
    command += ' >> ' + out_port+'/logfile.txt'

    print("COMMAND: " + command + "\n")
    os.system(command)


'''
#4 module: metabolite adduct decharger
'''
def metaboliteadductdecharger(mapaligner_port, ini_file, out_port):
    print("\n==METABOLITE ADDUCT DECHARGER==")
    for file in os.listdir(mapaligner_port):
        if 'log' not in file:
            command = "MetaboliteAdductDecharger -ini " + ini_file + " -in " + mapaligner_port+'/'+file + " "
            command += "-out_fm " + out_port+'/adductdecharger.featureXML' + " -out_cm " + out_port+'/adductdecharger.consensusXML' + ' >> ' + out_port+'/logfile.txt'

            print("COMMAND: " + command + "\n")
            os.system(command)


'''
#5 module: feature linker unlabeled kd
'''
def featurelinkerunlabeledkd(adductdecharger_port, ini_file, out_port):
    print("\n==FEATURE LINKER UNLABELED KD==")

    command = "FeatureLinkerUnlabeledKD -ini " + ini_file + " -in "
    for file in os.listdir(adductdecharger_port):
        if 'log' not in file:
            command += mapaligner_port + '/' + file + " "
    command += " -out " + out_port+"/featurelinker.consensusXML" + ' >> ' + out_port+'/logfile.txt'
    # command += " -out " + curr_port+"/tmp.consensusXML"

    print("COMMAND: " + command + "\n")
    os.system(command)

    # delete featureXML file
    # if os.path.exists(out_port+"/featurelinker-tmp.consensusXML"):
    #     os.remove(out_port+"/featurelinker-tmp.consensusXML")


'''
#6 module: gnps export
'''
def gnpsexport(use_featurelinker, featurelinker_port, adductdecharger_port, inputFiles_port, ini_file, output_type, out_port):
    in_cm = ""
    if use_featurelinker:
        in_cm = featurelinker_port+'/'+"featurelinker.consensusXML"
    else:
        in_cm = adductdecharger_port+'/'+"adductdecharger.consensusXML"

    # in_cm = in_port+'/'+get_port_outputs(in_port)[0]
    output = out_port + '/' + "gnpsexport.mgf"

    command = "GNPSExport -ini " + ini_file + " -in_cm " + in_cm + " -in_mzml "
    for file in os.listdir(inputFiles_port):
        command += inputFiles_port+'/'+file + " "
    command += "-out " + output + " -output_type " + output_type + ' >> ' + out_port+'/logfile.txt'

    print("COMMAND: " + command + "\n")
    os.system(command)


'''
#6 module: gnps export
'''
def textexporter(adductdecharger_port, ini_file, out_port):
    file = adductdecharger_port+'/'+"adductdecharger.consensusXML"
    # file = in_port+'/'+get_port_outputs(in_port)[0]
    command = "TextExporter -ini " + ini_file + " -in " + file + " -out " + out_port+'/textexporter.csv' + ' >> ' + out_port+'/logfile.txt'
    # command = command_dir+"TextExporter -ini " + ini_file + " -in " + file + " -out " + curr_port+'/out.csv'

    print("COMMAND: " + command + "\n")
    os.system(command)


if __name__ == '__main__':
    featurefindermetabo("inputFiles", "iniFiles-featurefinder/1-featurefindermetabo", "featurefindermetabo")
    idmapper("inputFiles", "iniFiles-idmapper/1b-idmapper", "iniFiles-idmapper/empty.idXML", "featurefindermetabo", "idmapper")
    mapalignerposeclustering("idmapper", "iniFiles-mapaligner/2-mapalignerposeclustering", "mapalignerposeclustering")
    metaboliteadductdecharger("mapalignerposeclustering", "iniFiles-adductdecharger/4-metaboliteadductdecharger", "metaboliteadductdecharger")
    use_featurelinker = featurelinkerunlabeledkd("metaboliteadductdecharger", "iniFiles-featurelinker/3-featurelinkerunlabeledkd", "featurelinkerunlabeledkd")
    gnpsexport(use_featurelinker, "featurelinkerunlabeledkd", "metaboliteadductdecharger", "inputFiles", "iniFiles-gnpsexport/5-gnpsexport", "merged_spectra", "gnpsexport")

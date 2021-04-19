#!/usr/bin/python


import sys
import getopt
import requests
import requests_cache
import json
import os

requests_cache.install_cache('demo_cache', allowable_codes=(200, 404))


def usage():
    print("<input txt> <output mgf> <output batch file>")
    print("Takes MZVault TXT file to convert to MGF and batch file")

def inchikey_to_inchi_smiles_pubchem(inchikey):
    url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/inchikey/%s/JSON" % (inchikey)
    #print(url)
    inchi = "N/A"
    smiles = "N/A"

    try:
        r = requests.get(url)
        if r.status_code == 200:
            json_obj = json.loads(r.text)
            for compound_property in json_obj["PC_Compounds"][0]["props"]:
                if compound_property["urn"]["label"] == "InChI":
                    inchi = compound_property["value"]["sval"]
                if compound_property["urn"]["label"] == "SMILES" and compound_property["urn"]["name"] == "Canonical":
                    smiles = compound_property["value"]["sval"]

    except KeyboardInterrupt:
        raise
    except:
        raise
        return inchi, smiles
    return inchi, smiles

def inchikey_to_inchi_chemspider(inchikey):
    url = "http://www.chemspider.com/InChI.asmx/InChIKeyToInChI"
    payload = {'inchi_key': inchikey}
    inchi = "N/A"
    try:
        r = requests.get(url, params=payload)
        if r.status_code == 200:
            inchi = xmltodict.parse(r.text)["string"]["#text"]
    except KeyboardInterrupt:
        raise
    except:
        return inchi
    return inchi

def inchi_to_smiles_chemspider(inchi):
    url = "http://www.chemspider.com/InChI.asmx/InChIToSMILES"
    payload = {'inchi': inchi}
    smiles = "N/A"
    try:
        r = requests.get(url, params=payload)
        if r.status_code == 200:
            smiles = xmltodict.parse(r.text)["string"]["#text"]
    except KeyboardInterrupt:
        raise
    except:
        return smiles
    return smiles

def main():
    usage()
    # input file, mgf output, batch file
    convert(sys.argv[1], sys.argv[2], sys.argv[3])

def convert(input_filename, mgf_filename, batch_filename):
    txt_file = open(input_filename, "r")
    mgf_file = open(mgf_filename, "w")
    batch_file = open(batch_filename, "w")

    json_mapping_cache_filename = "mapping_cache.json"
    inchikey_to_structure_map = {}
    if os.path.isfile(json_mapping_cache_filename):
        inchikey_to_structure_map = json.loads(open(json_mapping_cache_filename).read())

    acceptable_ionization = set(["ESI", "APCI"])
    acceptable_instruments = set(["ESI-IT-MS/MS", "ESI-QqIT-MS/MS", "ESI-QqQ-MS/MS", "ESI-QqTOF-MS/MS", "FAB-EBEB", "LC-APPI-QQ", "LC-ESI-IT", "LC-ESI-ITFT", "LC-ESI-ITTOF", "LC-ESI-QIT", "LC-ESI-QQ", "LC-ESI-QTOF"  ])

    peptide = "*..*"
    smiles = "N/A"
    inchi = "N/A"
    pepmass = ""
    title = ""
    instrument = "Orbitrap"
    compound_name = ""
    peaks = []
    retentiontime = ""
    ion_mode = ""
    peaks_start = 0
    exactmass = "0"
    cas_number = "N/A"
    adduct = "M+H"
    spectrum_level = 0
    ionization_mode = ""
    collision_energy = ""

    pi = "Madeleine Ernst"
    data_collector = "Anna Abrahamsson"
    library_level = "1"

    read_peaks = False

    scan_number = 1

    #Writing Batch Headers
    batch_file.write("FILENAME\tSEQ\tCOMPOUND_NAME\tMOLECULEMASS\tINSTRUMENT\tIONSOURCE\tEXTRACTSCAN\t")
    batch_file.write("SMILES\tINCHI\tINCHIAUX\tCHARGE\tIONMODE\tPUBMED\tACQUISITION\tEXACTMASS\tDATACOLLECTOR\t")
    batch_file.write("ADDUCT\tINTEREST\tLIBQUALITY\tGENUS\tSPECIES\tSTRAIN\tCASNUMBER\tPI\n")

    for line in txt_file:
        if "MS:1009003|Name" in line:
            compound_name = line.split(" = ")[-1].strip()

        if "Positive scan" in line:
            ion_mode = "Positive"

        if "Negative scan" in line:
            ion_mode = "Negative"

        if "MS:1000073|Electrosprary ionization" in line:
            ionization_mode = "ESI"

        if "Smiles" in line:
            smiles = line.split(" = ")[-1].rstrip()

        if "MS:1000744|Selected Ion m/z" in line:
            pepmass = line.split(" = ")[-1].rstrip()

        if "MS:1009100|CASNo" in line:
            cas_number = line.split(" = ")[-1].rstrip()

        if "MS:1000045|Collision_energy" in line:
            collision_energy = line.split(" = ")[-1].rstrip().lstrip()

        if "Adduct" in line:
            adduct = line.split(" = ")[-1].rstrip().lstrip()

        if "Num peaks:" in line or "Num Peaks: " in line or "number of peaks" in line:
            peaks = []
            read_peaks = True
            continue

        if len(line.strip()) < 1:
            #End of spectrum, writing spectrum
            spectrum_string = ""
            spectrum_string += "BEGIN IONS\n"
            spectrum_string += "SEQ=" + peptide + "\n"
            spectrum_string += "PEPMASS=" + pepmass + "\n"
            spectrum_string += "SMILES=" + smiles + "\n"
            spectrum_string += "INCHI=" + inchi + "\n"
            spectrum_string += "SOURCE_INSTRUMENT=" + instrument + "\n"
            spectrum_string += "NAME=" + compound_name + "\n"
            spectrum_string += "SCANS=" + str(scan_number) + "\n"

            for peak in peaks:
                spectrum_string += peak + "\n"


            peaks = []
            spectrum_string += "END IONS\n"
            #print spectrum_string
            mgf_file.write(spectrum_string)
            read_peaks = False

            #writing batch file
            batch_file.write(mgf_filename + "\t")
            batch_file.write(peptide + "\t")
            batch_file.write("{} - {} eV".format(compound_name, collision_energy) + "\t")
            batch_file.write(pepmass + "\t")
            batch_file.write(instrument + "\t")
            batch_file.write(ionization_mode + "\t")
            batch_file.write(str(scan_number) + "\t")
            batch_file.write(smiles + "\t")
            batch_file.write(inchi + "\t")
            batch_file.write("N/A" + "\t")
            batch_file.write("1" + "\t")
            batch_file.write(ion_mode + "\t")
            batch_file.write("N/A" + "\t")
            batch_file.write("Isolated" + "\t")
            batch_file.write("0" + "\t")
            batch_file.write(data_collector + "\t")
            batch_file.write(adduct + "\t")
            batch_file.write("N/A" + "\t")
            batch_file.write(library_level + "\t")
            batch_file.write("N/A" + "\t")
            batch_file.write("N/A" + "\t")
            batch_file.write("N/A" + "\t")
            batch_file.write(cas_number + "\t")
            batch_file.write(pi + "\n")

            scan_number += 1

            cas_number = "N/A"
            smiles = "N/A"
            inchi = "N/A"

            #Saving out cache
            if scan_number % 1000 == 0:
                open(json_mapping_cache_filename, "w").write(json.dumps(inchikey_to_structure_map))

        if read_peaks == True:
            try:
                peaks.append(" ".join(line.rstrip().split(" ")[:2]))
            except:
                pass

    return 0




if __name__ == "__main__":
    main()

#!/usr/bin/python


import sys
import getopt
import requests
import json
import os

try:
    import requests_cache
    requests_cache.install_cache('demo_cache', allowable_codes=(200, 404))
except:
    pass


def usage():
    print("<input txt> <output mgf> <output batch file>")
    print("Takes NIST MSP file to convert to MGF and batch file")

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
    instrument = ""
    compound_name = ""
    peaks = []
    retentiontime = ""
    ion_mode = ""
    peaks_start = 0;
    exactmass = "0"
    cas_number = "N/A"
    adduct = "M+H"
    spectrum_level = 0
    ionization_mode = ""
    nist_no = " "

    read_peaks = False

    scan_number = 1

    #Writing Batch Headers
    batch_file.write("FILENAME\tSEQ\tCOMPOUND_NAME\tMOLECULEMASS\tINSTRUMENT\tIONSOURCE\tEXTRACTSCAN\t")
    batch_file.write("SMILES\tINCHI\tINCHIAUX\tCHARGE\tIONMODE\tPUBMED\tACQUISITION\tEXACTMASS\tDATACOLLECTOR\t")
    batch_file.write("ADDUCT\tINTEREST\tLIBQUALITY\tGENUS\tSPECIES\tSTRAIN\tCASNUMBER\tPI\n")

    for line in txt_file:
        if line.find("Name:") != -1:
            compound_name = line.strip()[len("Name: "):]
            #print line.rstrip()

        if line.find("Synon: $:06") != -1:
            instrument = line[len("Synon: $:06"):].rstrip()

        if line.find("Instrument_type") != -1:
            instrument = line[len("Instrument_type: "):].rstrip()

        if line.find("Synon: $:00") != -1:
            ms_level = line[len("Synon: $:00"):].rstrip()

        if line.find("Synon: $:10") != -1:
            ionization_mode = line[len("Synon: $:10"):].rstrip()

        if line.find("Ionization: ") != -1:
            ionization_mode = line[len("Ionization: "):].rstrip()

        if "Synon: $:03" in line or "Precursor_type" in line:
            adduct = line.replace("Synon: $:03", "").replace("Precursor_type: ", "").rstrip()
            if adduct[-1] == "+":
                ion_mode = "Positive"
            if adduct[-1] == "-":
                ion_mode = "Negative"
            adduct = adduct[:-1]

        if line.find("Synon: $:28") != -1:
            inchi_key = line[len("Synon: $:28"):].rstrip()
            if not inchi_key in inchikey_to_structure_map:
                inchi, smiles = inchikey_to_inchi_smiles_pubchem(inchi_key)
                if inchi == "N/A":
                    inchi = inchikey_to_inchi_chemspider(inchi_key)
                if smiles == "N/A":
                    smiles = inchi_to_smiles_chemspider(inchi)
                inchikey_to_structure_map[inchi_key] = (inchi, smiles)
            else:
                inchi, smiles = inchikey_to_structure_map[inchi_key]
            print(inchi_key, inchi, smiles)

        if line.find("NISTNO:") != -1:
            nist_no = line[len("NISTNO: "):].rstrip()

        if line.find("PrecursorMZ: ") != -1:
            pepmass = line[len("PrecursorMZ: "):].rstrip()

        if line.find("CASNO: ") != -1:
            cas_number = line[len("CASNO: "):].rstrip()


        if "Num peaks:" in line or "Num Peaks: " in line:
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
            spectrum_string += "NAME=" + "NIST:" + nist_no + " " + compound_name + "\n"
            spectrum_string += "ORGANISM=NIST\n"
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
            batch_file.write(compound_name + "\t")
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
            batch_file.write("NIST" + "\t")
            batch_file.write(adduct[1:-1] + "\t")
            batch_file.write("N/A" + "\t")
            batch_file.write("3" + "\t")
            batch_file.write("N/A" + "\t")
            batch_file.write("N/A" + "\t")
            batch_file.write("N/A" + "\t")
            batch_file.write(cas_number + "\t")
            batch_file.write("NIST" + "\n")


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

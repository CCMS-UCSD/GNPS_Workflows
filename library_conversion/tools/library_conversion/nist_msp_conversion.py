#!/usr/bin/python

import sys
import getopt
import requests
import json
import os

import xmltodict

try:
    import requests_cache

    requests_cache.install_cache('demo_cache', allowable_codes=(200, 404))
except:
    pass


def inchikey_to_inchi_smiles_pubchem(inchikey):
    url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/inchikey/%s/JSON" % (inchikey)
    # print(url)
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


def convert(input_filename, mgf_filename, batch_filename, pi_name, collector_name):
    # open input and output files
    with open(input_filename, "r") as txt_file, \
            open(mgf_filename, "w") as mgf_file, \
            open(batch_filename, "w") as batch_file:

        json_mapping_cache_filename = "mapping_cache.json"
        inchikey_to_structure_map = {}
        if os.path.isfile(json_mapping_cache_filename):
            inchikey_to_structure_map = json.loads(open(json_mapping_cache_filename).read())

        acceptable_ionization = set(["ESI", "APCI"])
        acceptable_instruments = set(
            ["ESI-IT-MS/MS", "ESI-QqIT-MS/MS", "ESI-QqQ-MS/MS", "ESI-QqTOF-MS/MS", "FAB-EBEB", "LC-APPI-QQ",
             "LC-ESI-IT", "LC-ESI-ITFT", "LC-ESI-ITTOF", "LC-ESI-QIT", "LC-ESI-QQ", "LC-ESI-QTOF"])

        peptide = "*..*"
        smiles = "N/A"
        inchi = "N/A"
        pepmass = ""
        title = ""
        instrument = ""
        instrument_type = ""
        compound_name = ""
        peaks = []
        retentiontime = ""
        ion_mode = ""
        peaks_start = 0;
        exactmass = "0"
        cas_number = "N/A"
        adduct = ""
        spectrum_level = 0
        ionization_mode = ""
        nist_no = " "
        read_peaks = False

        pi = (pi_name if pi_name is not None else "")
        data_collector = (collector_name if collector_name is not None else "")
        scan_number = 1

        # Writing Batch Headers
        batch_file.write("FILENAME\tSEQ\tCOMPOUND_NAME\tMOLECULEMASS\tINSTRUMENT\tIONSOURCE\tEXTRACTSCAN\t")
        batch_file.write("SMILES\tINCHI\tINCHIAUX\tCHARGE\tIONMODE\tPUBMED\tACQUISITION\tEXACTMASS\tDATACOLLECTOR\t")
        batch_file.write("ADDUCT\tINTEREST\tLIBQUALITY\tGENUS\tSPECIES\tSTRAIN\tCASNUMBER\tPI\n")

        for line in txt_file:
            line_lower = line.lower()
            if line_lower.find("name:") != -1:
                compound_name = line.strip()[len("Name: "):]
                # print line.rstrip()

            # LC-ESI-QTOF ...
            if line_lower.find("synon: $:06") != -1:
                instrument_type = line[len("Synon: $:06"):].rstrip()

            # LC-ESI-QTOF ...
            if line_lower.find("instrument_type") != -1:
                instrument_type = line[len("Instrument_type: "):].rstrip()

            # QExactive, Bruker maXis, etc
            if line_lower.find("instrument") != -1:
                instrument = line[len("instrument: "):].rstrip()

            if line_lower.find("synon: $:00") != -1:
                ms_level = line[len("Synon: $:00"):].rstrip()

            if line_lower.find("synon: $:10") != -1:
                ionization_mode = line[len("Synon: $:10"):].rstrip()

            if line_lower.find("ionization: ") != -1:
                ionization_mode = line[len("Ionization: "):].rstrip()

            # P or N
            if line_lower.find("ion_mode: ") != -1:
                ion_mode = line_lower[len("ion_mode: "):].rstrip()
                if ion_mode == "p" or "pos" in ion_mode:
                    ion_mode = "Positive"
                elif ion_mode == "n" or "neg" in ion_mode:
                    ion_mode = "Negative"

            if "synon: $:03" in line_lower or "precursor_type" in line_lower:
                adduct = line.replace("Synon: $:03", "").replace("Precursor_type: ", "").rstrip()
                if len(adduct) > 1:
                    if adduct[-1] == "+":
                        ion_mode = "Positive"
                    elif adduct[-1] == "-":
                        ion_mode = "Negative"
                    # for doubly charged: [M+2H]+2
                    elif adduct[-2] == "+":
                        ion_mode = "Positive"
                    elif adduct[-2] == "-":
                        ion_mode = "Negative"
                    adduct = adduct[:-1]

            if "synon: $:28" in line_lower or "inchikey" in line_lower:
                inchi_key = line.replace("Synon: $:28", "").replace("inchikey: ", "").rstrip()
                # cache inchi and smiles for inchi_key
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

            if line_lower.find("nistno:") != -1:
                nist_no = line[len("NISTNO: "):].rstrip()

            if line_lower.find("precursormz: ") != -1:
                pepmass = line[len("PrecursorMZ: "):].rstrip()

            if line_lower.find("casno: ") != -1:
                cas_number = line[len("CASNO: "):].rstrip()
            if line_lower.find("cas: ") != -1:
                cas_number = line[len("cas: "):].rstrip()
            if line_lower.find("cas#: ") != -1:
                cas_number = line[len("cas#: "):].rstrip()

            if "num peaks:" in line_lower:
                peaks = []
                read_peaks = True
                continue

            # check for empty line or EOF (line without break)
            if read_peaks == True and (len(line.strip()) < 1 or line.find("\n") == -1):
                # End of spectrum, writing spectrum
                spectrum_string = ""
                spectrum_string += "BEGIN IONS\n"
                spectrum_string += "SEQ=" + peptide + "\n"
                spectrum_string += "PEPMASS=" + pepmass + "\n"
                spectrum_string += "SMILES=" + smiles + "\n"
                spectrum_string += "INCHI=" + inchi + "\n"
                spectrum_string += "SOURCE_INSTRUMENT=" + instrument_type + "\n"
                spectrum_string += "NAME=" + "NIST:" + nist_no + " " + compound_name + "\n"
                spectrum_string += "ORGANISM=NIST\n"
                spectrum_string += "SCANS=" + str(scan_number) + "\n"

                for peak in peaks:
                    spectrum_string += peak + "\n"

                peaks = []
                spectrum_string += "END IONS\n"
                # print spectrum_string
                mgf_file.write(spectrum_string)
                read_peaks = False

                # writing batch file
                batch_file.write(mgf_filename + "\t")
                batch_file.write(peptide + "\t")
                batch_file.write(compound_name + "\t")
                batch_file.write(pepmass + "\t")
                # instrument names
                if len(instrument) > 0:
                    batch_file.write(instrument + "\t")
                else:
                    batch_file.write(instrument_type + "\t")
                # LC-ESI ....
                if len(ionization_mode) > 0:
                    batch_file.write(ionization_mode + "\t")
                elif len(instrument_type) > 0:
                    batch_file.write(instrument_type + "\t")
                else:
                    batch_file.write("\t")
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
                batch_file.write(adduct[1:-1] + "\t")
                batch_file.write("N/A" + "\t")
                batch_file.write("3" + "\t")
                batch_file.write("N/A" + "\t")
                batch_file.write("N/A" + "\t")
                batch_file.write("N/A" + "\t")
                batch_file.write(cas_number + "\t")
                batch_file.write(pi + "\n")

                scan_number += 1

                # reset all values
                peptide = "*..*"
                smiles = "N/A"
                inchi = "N/A"
                pepmass = ""
                instrument = ""
                instrument_type = ""
                compound_name = ""
                peaks = []
                ion_mode = ""
                cas_number = "N/A"
                adduct = ""
                ionization_mode = ""
                nist_no = " "

                # Saving out cache
                if scan_number % 1000 == 0:
                    open(json_mapping_cache_filename, "w").write(json.dumps(inchikey_to_structure_map))

            if read_peaks == True:
                try:
                    peaks.append(" ".join(line.rstrip().split(" ")[:2]))
                except:
                    pass

        return 0


if __name__ == "__main__":
    import library_conversion

    library_conversion.main()

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
    # count number of library entries
    number_of_entries = 0
    line_number = 0

    try:
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

            scan_number = 1

            # replace PI name if provided
            replace_pi_name = pi_name is not None and len(str(pi_name).strip())>0
            replace_collector_name = collector_name is not None and len(str(collector_name).strip())>0

            # Writing Batch Headers
            batch_file.write("FILENAME\tSEQ\tCOMPOUND_NAME\tMOLECULEMASS\tINSTRUMENT\tIONSOURCE\tEXTRACTSCAN\t")
            batch_file.write("SMILES\tINCHI\tINCHIAUX\tCHARGE\tIONMODE\tPUBMED\tACQUISITION\tEXACTMASS\tDATACOLLECTOR\t")
            batch_file.write("ADDUCT\tINTEREST\tLIBQUALITY\tGENUS\tSPECIES\tSTRAIN\tCASNUMBER\tPI\n")

            for line in txt_file:
                line_number += 1
                # is a json lines format with one entry per line
                spectrum_json = json.loads(line)

                pi = (pi_name if replace_pi_name else str(spectrum_json["PI"]))
                data_collector = (collector_name if replace_collector_name is not None else str(spectrum_json["DATACOLLECTOR"]))

                peptide = "*..*"
                compound_name = str(spectrum_json["COMPOUND_NAME"])
                adduct = str(spectrum_json["ADDUCT"])
                charge = str(spectrum_json["CHARGE"])
                cas_number = str(spectrum_json["CASNUMBER"])
                pubmed = str(spectrum_json["PUBMED"])
                inchi_key = str(spectrum_json["INCHIAUX"])
                inchi = str(spectrum_json["INCHI"])
                smiles = str(spectrum_json["SMILES"])
                # precursor mz
                pepmass = str(spectrum_json["MZ"])
                # exact neutral mass
                exact_mass = str(spectrum_json["EXACTMASS"])
                formula = str(spectrum_json["FORMULA"])
                instrument_type = str(spectrum_json["INSTRUMENT"])
                instrument = str(spectrum_json["INSTRUMENT_NAME"])
                ionization_mode = str(spectrum_json["IONSOURCE"])
                acquisition = str(spectrum_json["ACQUISITION"])
                ion_mode = str(spectrum_json["IONMODE"])

                # sanity check
                if len(compound_name.strip()) <= 0:
                    raise Exception(
                        "No compound name in MZmine .json entry. Building triggered at line number {}".format(
                            str(line_number)))
                if len(str(pepmass).strip()) <= 0:
                    raise Exception(
                        "No compound mass in MZmine .json entry. Building triggered at line number {}".format(
                            str(line_number)))

                # resolve inchikey if no inchi or smiles
                if len(inchi_key) > 0 and (len(inchi) <= 0 or len(smiles) <= 0):
                    inchi, smiles = resolve_inchikey(inchi_key, inchikey_to_structure_map)

                # End of spectrum, writing spectrum
                spectrum_string = ""
                spectrum_string += "BEGIN IONS\n"
                spectrum_string += "SEQ=" + peptide + "\n"
                spectrum_string += "PEPMASS=" + pepmass + "\n"
                spectrum_string += "CHARGE=" + charge + "\n"
                spectrum_string += "MSLEVEL=2\n"
                spectrum_string += "SMILES=" + smiles + "\n"
                spectrum_string += "INCHI=" + inchi + "\n"
                spectrum_string += "SOURCE_INSTRUMENT=" + instrument_type + "\n"
                spectrum_string += "NAME=" + compound_name + "\n"
                spectrum_string += "ORGANISM=NIST\n"
                spectrum_string += "SCANS=" + str(scan_number) + "\n"

                for peak in spectrum_json["peaks"]:
                    spectrum_string += "{0} {1}\n".format(str(peak[0]), str(peak[1]))

                spectrum_string += "END IONS\n"
                # print(spectrum_string)
                mgf_file.write(spectrum_string)

                # writing batch file
                batch_file.write(mgf_filename + "\t")
                batch_file.write(peptide + "\t")
                batch_file.write(compound_name + "\t")
                batch_file.write(pepmass + "\t")
                # instrument names
                batch_file.write(instrument_type + "\t")
                # LC-ESI ....
                batch_file.write(ionization_mode + "\t")
                batch_file.write(str(scan_number) + "\t")
                batch_file.write(smiles + "\t")
                batch_file.write(inchi + "\t")
                batch_file.write(inchi_key + "\t")
                batch_file.write(str(charge) + "\t")
                batch_file.write(ion_mode + "\t")
                batch_file.write(pubmed + "\t")
                batch_file.write(acquisition + "\t")
                batch_file.write(exact_mass + "\t")
                batch_file.write(data_collector + "\t")
                batch_file.write(adduct + "\t")
                batch_file.write("N/A" + "\t")
                batch_file.write("3" + "\t")
                batch_file.write("N/A" + "\t")
                batch_file.write("N/A" + "\t")
                batch_file.write("N/A" + "\t")
                batch_file.write(cas_number + "\t")
                batch_file.write(pi + "\n")

                scan_number += 1
                number_of_entries += 1

                # Saving out cache
                if scan_number % 1000 == 0:
                    open(json_mapping_cache_filename, "w").write(json.dumps(inchikey_to_structure_map))

    except Exception as e:
        raise Exception("MZmine .json (json lines) format error in file {}".format(str(input_filename))) from e

    # all lines processed - return number of entries
    if number_of_entries == 0:
        raise Exception("No MZmine .json entries in file {}".format(str(input_filename)))
    else:
        return number_of_entries


def resolve_inchikey(inchi_key, inchikey_to_structure_map):
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
    # print(inchi_key, inchi, smiles)
    return inchi, smiles


if __name__ == "__main__":
    import library_conversion

    library_conversion.main()

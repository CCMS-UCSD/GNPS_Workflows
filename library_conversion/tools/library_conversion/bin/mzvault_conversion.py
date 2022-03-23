#!/usr/bin/python
import sys
import getopt
import requests
from requests import HTTPError
import json
import os
import logging_utils

# get logger
logger = logging_utils.get_logger(__name__)


def determine_adduct(smiles, mz):
    params = {"smiles": smiles, "mz": mz}
    url = "http://gnpsserver1.ucsd.edu:5066/adductcalc"
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()

        adducts_sorted = sorted(r.json(), key=lambda x: abs(x["delta"]))
        smallest_delta = adducts_sorted[0]["delta"]
        if abs(smallest_delta) < 0.1:
            return adducts_sorted[0]["adduct"], r.json()
        return None, r.json()
    except HTTPError as error:
        logger.exception(error)
        raise error


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
            adduct = ""
            spectrum_level = 0
            ionization_mode = "ESI"
            collision_energy = ""

            # set some defaults
            pi = (pi_name if pi_name is not None else "")
            data_collector = (collector_name if collector_name is not None else "")
            library_level = "1"

            read_peaks = False

            scan_number = 1

            # Writing Batch Headers
            batch_file.write("FILENAME\tSEQ\tCOMPOUND_NAME\tMOLECULEMASS\tINSTRUMENT\tIONSOURCE\tEXTRACTSCAN\t")
            batch_file.write(
                "SMILES\tINCHI\tINCHIAUX\tCHARGE\tIONMODE\tPUBMED\tACQUISITION\tEXACTMASS\tDATACOLLECTOR\t")
            batch_file.write("ADDUCT\tINTEREST\tLIBQUALITY\tGENUS\tSPECIES\tSTRAIN\tCASNUMBER\tPI\n")

            for line in txt_file:
                line_number += 1

                if "MS:1009003|Name" in line:
                    compound_name = line.split(" = ")[-1].strip()

                if "Positive scan" in line:
                    ion_mode = "Positive"

                if "Negative scan" in line:
                    ion_mode = "Negative"

                if "MS:1000073|Electrosprary ionization" in line:
                    ionization_mode = "ESI"

                if "Smiles" in line or "MS:1000868|Smiles" in line:
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

                if read_peaks == True and len(line.strip()) < 1:
                    # sanity check
                    if len(compound_name.strip()) <= 0 or len(str(pepmass).strip()) <= 0:
                        raise Exception(
                            "No compound name in MZvault entry. Building triggered at line number {}".format(
                                str(line_number)))
                    if len(str(pepmass).strip()) <= 0:
                        raise Exception(
                            "No compound mass in MZvault entry. Building triggered at line number {}".format(
                                str(line_number)))

                    # End of spectrum
                    if adduct == "":
                        try:
                            adduct, adducts_sorted_json = determine_adduct(smiles, pepmass)
                            if adduct == None:
                                adduct = "Unknown"
                                # logger.debug("Missing adduct: %s, %s", compound_name, smiles)
                                # print("MISSING ADDUCT", adducts_sorted_json, compound_name, smiles)
                        except:
                            adduct = 'Unknown'

                    # Writing spectrum
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
                    # print spectrum_string
                    mgf_file.write(spectrum_string)
                    read_peaks = False

                    # writing batch file
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
                    number_of_entries += 1

                    # reset important fields
                    compound_name = ""
                    pepmass = ""
                    cas_number = "N/A"
                    smiles = "N/A"
                    inchi = "N/A"
                    adduct = ""

                    # Saving out cache
                    if scan_number % 1000 == 0:
                        open(json_mapping_cache_filename, "w").write(json.dumps(inchikey_to_structure_map))

                if read_peaks == True:
                    try:
                        peaks.append(" ".join(line.rstrip().split(" ")[:2]))
                    except:
                        pass
    except Exception as e:
        raise Exception("MZvault format error in file {}".format(str(input_filename))) from e

    # all lines processed - return number of entries
    if number_of_entries == 0:
        raise Exception("No MZvault entries in file {}".format(str(input_filename)))
    else:
        return number_of_entries


if __name__ == "__main__":
    import library_conversion

    library_conversion.main()

import sys
import logging_utils
import getopt
import json
import os
import pandas as pd
import requests
from requests import HTTPError
from urllib.parse import quote

# get logger
logger = logging_utils.get_logger(__name__)


def convert(input_filename, mgf_filename, batch_filename, pi_name, collector_name):
    input_file = open(input_filename, "r")
    mgf_file = open(mgf_filename, "w")
    batch_file = open(batch_filename, "w")

    # Writing Batch Headers
    batch_file.write(
        "FILENAME\tSEQ\tCOMPOUND_NAME\tMOLECULEMASS\tINSTRUMENT\tIONSOURCE\tEXTRACTSCAN\tSMILES\tINCHI\tINCHIAUX"
        "\tCHARGE\tIONMODE\tPUBMED\tACQUISITION\tEXACTMASS\tDATACOLLECTOR\tADDUCT\tINTEREST\tLIBQUALITY\tGENUS"
        "\tSPECIES\tSTRAIN\tCASNUMBER\tPI\n")

    # main stuff
    pi = (pi_name if pi_name is not None else "")
    data_collector = (collector_name if collector_name is not None else "")

    read_peaks = False
    scan_number = 1

    for line in input_file:
        if "NAME:" in line:
            compound_name = line.split(" = ")[-1].rstrip()

        if "PRECURSORMZ:" in line:
            pepmass = line.split(" = ")[-1].rstrip()

        if "PRECURSORTYPE:" in line:
            precursortype = line.split(" = ")[-1].strip()

        if "FORMULA:" in line:
            formula = line.split(" = ")[-1].strip()

        if "RETENTIONTIME:" in line:
            retentiontime = line.split(" = ")[-1].strip()

        if "CCS:" in line:
            CCS = "-1"

        if "IONMODE:" in line:
            ionmode = "Positive"

        if "INSTRUMENTTYPE:" in line:
            insttype = "ESI"

        if "INSTRUMENT:" in line:
            instrument = "N/A"

        if "COLLISIONENERGY" in line:
            collision_energy = "N/A"

        if "Comment:" in line:
            comment = "N/A"

        if "SMILES:" in line:
            smiles = line.split(" = ")[-1].strip()
            smiles_str = smiles.replace('SMILES: ', '')

            # initialize values in case of error
            exact_mass_str = "N/A"
            inchi_convert_str = "N/A"

            if smiles_str is not None:
                try:
                    inchi_convert_results = requests.get(
                        f'https://gnps-structure.ucsd.edu/inchi?smiles={quote(smiles_str)}')
                    # if error code - raise exception for logging also see request.ok
                    inchi_convert_results.raise_for_status()
                    # set value
                    inchi_convert_str = str(inchi_convert_results.text).replace('InChI=', "")
                except HTTPError as error:
                    inchi_convert_str = "N/A"
                    logger.warning("Failed to get InChI from SMILES at: %s", inchi_convert_results.request.url)
                    logger.exception(error)

                # calculate exact mass here
                try:
                    exact_mass_results = requests.get(
                        f'https://gnps-structure.ucsd.edu/structuremass?smiles={quote(smiles_str)}')
                    exact_mass_results.raise_for_status()
                    exact_mass_str = str(exact_mass_results.text)
                except HTTPError as error:
                    exact_mass_str = "N/A"
                    logger.warning("Failed to get exact mass from SMILES at: %s", exact_mass_results.request.url)
                    logger.exception(error)

        if "Num peaks:" in line or "Num Peaks: " in line or "number of peaks" in line:
            peaks = []
            read_peaks = True
            continue

        if len(line.strip()) < 1:
            # End of spectrum, writing spectrum
            spectrum_string = ""
            spectrum_string += "BEGIN IONS\n"
            spectrum_string += "PEPMASS=" + pepmass.replace('PRECURSORMZ: ', "") + "\n"
            spectrum_string += "SMILES=" + smiles_str + "\n"
            # spectrum_string += "SMILES=" + smiles.replace('SMILES: ','') + "\n"
            spectrum_string += "INCHI=" + inchi_convert_str + "\n"
            # spectrum_string += "SOURCE_INSTRUMENT=" + instrument + "\n"
            spectrum_string += "NAME=" + compound_name.replace('NAME: ', '') + "\n"
            spectrum_string += "SCANS=" + str(scan_number) + "\n"

            for peak in peaks:
                spectrum_string += peak + "\n"

            peaks = []
            spectrum_string += "END IONS\n"
            # print spectrum_string
            mgf_file.write(spectrum_string)
            read_peaks = False

            # writing batch file
            batch_file.write("BMDMS_mgf.mgf" + "\t")
            batch_file.write("*..*" + "\t")
            batch_file.write(compound_name.replace('NAME: ', '') + "\t")
            batch_file.write(pepmass.replace('PRECURSORMZ: ', "") + "\t")
            batch_file.write("Orbitrap" + "\t")
            batch_file.write(insttype + "\t")
            batch_file.write(str(scan_number) + "\t")
            batch_file.write(smiles_str + "\t")
            batch_file.write(inchi_convert_str + "\t")
            batch_file.write("N/A" + "\t")
            batch_file.write("1" + "\t")
            batch_file.write(ionmode + "\t")
            batch_file.write("N/A" + "\t")
            batch_file.write("Commercial standard" + "\t")
            batch_file.write(exact_mass_str + "\t")
            batch_file.write(data_collector + "\t")
            batch_file.write(precursortype.replace('PRECURSORTYPE: ', '') + "\t")
            batch_file.write("N/A" + "\t")
            batch_file.write("1" + "\t")
            batch_file.write("N/A" + "\t")
            batch_file.write("N/A" + "\t")
            batch_file.write("N/A" + "\t")
            batch_file.write("N/A" + "\t")
            batch_file.write(pi + "\n")

            scan_number += 1

            cas_number = "N/A"
            smiles = "N/A"
            inchi = "N/A"

            # Saving out cache
            # if scan_number % 1000 == 0:
            # open(json_mapping_cache_filename, "w").write(json.dumps(inchikey_to_structure_map))

        if read_peaks == True:
            try:
                peaks.append(" ".join(line.rstrip().split(" ")[:2]))
            except:
                pass


if __name__ == "__main__":
    import library_conversion

    library_conversion.main()

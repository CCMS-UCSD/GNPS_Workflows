#!/usr/bin/env python

import os
import pymzml
import pandas as pd
import shutil
import urllib.request as request
from contextlib import closing



def process_masst_xic(input_filename):
    df = pd.read_csv(input_filename, sep="\t")

    ms2_records = df.to_dict(orient="records")
    for record in ms2_records:
        # Making data file available
        ftp_url = "ftp://massive.ucsd.edu/" + record["filename"][2:]
        local_filename = os.path.basename(record["filename"])
        with closing(request.urlopen(ftp_url)) as r:
            with open(local_filename, 'wb') as f:
                shutil.copyfileobj(r, f)

        # Finding the scan
        run = pymzml.run.Reader(local_filename)

        target_scan = record["filescan"]
        for spectrum in run:
            if str(spectrum.ID) == str(target_scan):
                selected_precursors = spectrum.selected_precursors
                precursor_dict = selected_precursors[0]
                precursor_mz = precursor_dict["mz"]
                precursor_i = precursor_dict["i"]

                record["precursor_mz"] = precursor_mz
                record["precursor_i"] = precursor_i
                record["rt"] = spectrum.scan_time_in_minutes()        

        # Perform XIC
        target_mz = record["precursor_mz"]
        lower_rt = record["rt"] - 0.1
        upper_rt = record["rt"] + 0.1
        run = pymzml.run.Reader(local_filename, MS_precisions={1 : 5e-6, 2 : 20e-6})
        time_dependent_intensities = []

        for spectrum in run:
            spectrum_rt = float(spectrum.scan_time_in_minutes())
            if spectrum_rt < lower_rt or spectrum_rt > upper_rt:
                continue
            
            if spectrum.ms_level == 1:
                has_peak_matches = spectrum.has_peak(target_mz)
                if has_peak_matches != []:
                    for mz, I in has_peak_matches:
                        time_dependent_intensities.append(
                            [spectrum.scan_time_in_minutes(), I, mz]
                        )

        intensity = sum([peak[2] for peak in time_dependent_intensities])
        record["xic_sum"] = (intensity)

        print(record)

        os.remove(local_filename)

    return pd.DataFrame(ms2_records)


def main():
    """
    Demonstration of the extraction of a specific ion chromatogram, i.e. XIC or EIC

    All intensities and m/z values for a target m/z are extracted.

    usage:

        ./extract_ion_chromatogram.py

    """

    example_file = os.path.join(
        os.path.dirname(__file__), os.pardir, "tests", "data", "example.mzML"
    )
    run = pymzml.run.Reader(example_file)
    time_dependent_intensities = []

    MZ_2_FOLLOW = 70.06575775

    for spectrum in run:
        if spectrum.ms_level == 1:
            has_peak_matches = spectrum.has_peak(MZ_2_FOLLOW)
            if has_peak_matches != []:
                for mz, I in has_peak_matches:
                    time_dependent_intensities.append(
                        [spectrum.scan_time_in_minutes(), I, mz]
                    )
    print("RT   \ti   \tmz")
    for rt, i, mz in time_dependent_intensities:
        print("{0:5.3f}\t{1:13.4f}\t{2:10}".format(rt, i, mz))
    return


if __name__ == "__main__":
    main()
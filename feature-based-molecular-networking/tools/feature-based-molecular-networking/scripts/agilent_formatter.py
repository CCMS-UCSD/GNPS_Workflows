
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Mingxun Wang
@purpose: to convert the agilent output into a diserable format
"""
from io import StringIO
import pandas as pd
import sys
import os
import ming_spectrum_library

#TODO: Ask about why there are two column headers of the same name
def convert_to_feature_and_mgf_csv(input_mgf, output_quant, output_mgf):
    spectrum_collection = ming_spectrum_library.SpectrumCollection(input_mgf)
    spectrum_collection.load_from_file()

    #spectrum_collection = ming_spectrum_library.load_mgf_file(input_mgf)
    #print(len(spectrum_collection))

    # Outputting MGF
    spectrum_collection.make_scans_sequential()
    spectrum_collection.save_to_mgf(open(output_mgf, "w"))

    output_list = []
    for spectrum in spectrum_collection.spectrum_list:
        output_dict = {}
        output_dict["row ID"] = spectrum.scan
        output_dict["row m/z"] = spectrum.mz
        output_dict["row retention time"] = 0

        output_list.append(output_dict)

    df = pd.DataFrame(output_list)
    df[os.path.basename(input_mgf) + " Peak area"] = 1

    print(df)

    df.to_csv(output_quant, sep=",", index=False)


if __name__=="__main__":
    # there should be obly one input file
   convert_to_feature_and_mgf_csv(sys.argv[1], sys.argv[2], sys.argv[3])

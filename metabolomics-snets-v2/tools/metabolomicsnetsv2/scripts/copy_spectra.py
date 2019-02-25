import shutil
import sys
import os

input_spectra_folder = sys.argv[1]
output_filename = sys.argv[2]

input_specs_ms = os.path.join(input_spectra_folder, "specs_ms.mgf")

shutil.copyfile(input_specs_ms, output_filename)

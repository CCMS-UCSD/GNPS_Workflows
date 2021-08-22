import sys
import os
import glob
import requests
import pandas as pd

input_filename = sys.argv[1]
output_filename = sys.argv[2]

input_files = pd.read_csv(input_filename)
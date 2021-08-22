import sys
import os
import glob
import pandas as pd

input_filename = sys.argv[1]
output_filename = sys.argv[2]

df = pd.DataFrame()
filenames = glob.glob(os.path.join(input_filename, "**/*"), recursive=True)
filenames = [f for f in filenames if os.path.isfile(f)]

df["filename"] = filenames
df["filename2"]  = df["filename"]

df.to_csv(output_filename, sep="\t", index=False)
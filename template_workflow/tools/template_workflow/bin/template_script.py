import sys
import os
import glob
import pandas as pd

input_filename = sys.argv[1]
output_filename = sys.argv[2]

df = pd.DataFrame()
df["filename"] = glob.glob(os.path.join(input_filename, "*"))

df.to_csv(output_filename, sep="\t", index=False)
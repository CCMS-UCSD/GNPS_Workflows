import os
import sys
import pandas as pd

import argparse
import ming_proteosafe_library

from plotnine import *


def main():
    parser = argparse.ArgumentParser(description='Creating Demangling')
    parser.add_argument('extracted_results', help='extracted_results')
    parser.add_argument('output_folder', help='output_folder')
    
    args = parser.parse_args()

    extraction_df = pd.read_csv(args.extracted_results, sep="\t")


    p = (
        ggplot(extraction_df, aes(x='rt', y='int', color='filename'))
        + geom_line() # line plot
        + labs(x='RT', y='Intensity')
        theme(figure_size=(30,20))
    )

    p.save(os.path.join(args.output_folder, "merged.png"))

    # TODO: Drawing individual per file



if __name__ == "__main__":
    main()

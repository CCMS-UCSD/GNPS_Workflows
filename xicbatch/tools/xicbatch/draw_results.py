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
        + theme(figure_size=(20,16))
    )

    p.save(os.path.join(args.output_folder, "merged.png"), limitsize=False)

    # TODO: Drawing individual per file
    all_filenames = list(set(extraction_df["filename"]))
    all_queries = list(set(extraction_df["query"]))
    for filename in all_filenames:
        for query in all_queries:
            output_filename = "{}_{}.png".format(filename, query)
            filtered_df = extraction_df[extraction_df["filename"] == filename]
            filtered_df = filtered_df[filtered_df["query"] == query]

            print(filtered_df)
            print(len(filtered_df))

            p = (
                ggplot(filtered_df, aes(x='rt', y='int'))
                + geom_line() # line plot
                + labs(x='RT', y='Intensity')
                + theme(figure_size=(15,10))
            )

            p.save(os.path.join(args.output_folder, output_filename), limitsize=False)

        
        


if __name__ == "__main__":
    main()

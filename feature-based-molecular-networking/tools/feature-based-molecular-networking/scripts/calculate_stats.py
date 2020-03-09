#import_all_modules
import sys
import argparse
import plotnine as p9

import metadata_permanova_prioritizer

def calculate_statistics(input_quant_filename, input_metadata_file, metadata_column=None):
    if metadata_colums is None or metadata_column == "None":
        print("Consider all columns")

def main():
    parser = argparse.ArgumentParser(description='Calculate some stats')
    parser.add_argument('metadata_folder', help='metadata_folder')
    parser.add_argument('quantification_file', help='mzmine2 style quantification filename')
    parser.add_argument('output_images_folder', help='output_images_folder')
    parser.add_argument('output_stats_folder', help='output_stats_folder')
    args = parser.parse_args()



if __name__ == "__main__":
    main()

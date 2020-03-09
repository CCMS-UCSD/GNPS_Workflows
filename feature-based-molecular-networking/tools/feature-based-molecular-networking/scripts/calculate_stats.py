import os
import sys
import argparse
import pandas as pd
from plotnine import *
import glob
from scipy.stats import mannwhitneyu

import metadata_permanova_prioritizer

def calculate_statistics(input_quant_filename, input_metadata_file, 
                            output_summary_folder, 
                            output_plots_folder=None, 
                            metadata_column=None, 
                            condition_first=None, 
                            condition_second=None,
                            metadata_facet_column=None):
    ## Loading feature table
    features_df = pd.read_csv(input_quant_filename, sep=",")
    metadata_df = pd.read_csv(input_metadata_file, sep="\t")

    # removing peak area from columns
    features_df.index = features_df["row ID"]
    metabolite_id_list = list(features_df["row ID"])[:50]
    headers_to_keep = [header for header in features_df.columns if "Peak area" in header]
    features_df = features_df[headers_to_keep]
    column_mapping = {headers:headers.replace(" Peak area", "") for headers in features_df.columns}
    features_df = features_df.rename(columns=column_mapping)

    # Transpose
    features_df = features_df.T
    
    # Merging with Metadata
    features_df["filename"] = features_df.index
    features_df = features_df.merge(metadata_df, how="inner", on="filename")

    # If we do not select a column, we don't calculate stats, but we do generate nice box plots
    if metadata_column is None or metadata_column == "None":
        output_boxplot_list = []

        columns_to_consider = metadata_permanova_prioritizer.permanova_validation(input_metadata_file)

        # HACK TO MAKE FASTER
        if len(columns_to_consider) > 0:
            columns_to_consider = columns_to_consider[:1]

        for column_to_consider in columns_to_consider:
            # Loop through all metabolites, and create plots
            if output_plots_folder is not None:
                for metabolite_id in metabolite_id_list:
                    long_data_df = pd.melt(features_df, id_vars=[column_to_consider], value_vars=[metabolite_id])
                    output_filename = os.path.join(output_plots_folder, "{}_{}.png".format(column_to_consider, metabolite_id))

                    p = (
                        ggplot(long_data_df)
                        + geom_boxplot(aes(x="factor({})".format(column_to_consider), y="value", fill=column_to_consider))
                    )
                    p.save(output_filename)

                    output_dict = {}
                    output_dict["metadata_column"] = column_to_consider
                    output_dict["boxplotimg"] = os.path.basename(output_filename)
                    output_dict["scan"] = metabolite_id

                    output_boxplot_list.append(output_dict)

        metadata_all_columns_summary_df = pd.DataFrame(output_boxplot_list)
        metadata_all_columns_summary_df.to_csv(os.path.join(output_summary_folder, "all_columns.tsv"), sep="\t", index=False)

    # TODO: implement plotting on a specific column
    if metadata_column in features_df:
        output_stats_list = []

        features_df = features_df[features_df[metadata_column].isin([condition_first, condition_second])]

        data_first_df = features_df[features_df[metadata_column] == condition_first]
        data_second_df = features_df[features_df[metadata_column] == condition_second]

        for metabolite_id in metabolite_id_list:
            stat, pvalue = mannwhitneyu(data_first_df[metabolite_id], data_second_df[metabolite_id])
            long_data_df = pd.melt(features_df, id_vars=["filename"], value_vars=[metabolite_id])
            long_data_df = long_data_df.merge(metadata_df, how="inner", on="filename")

            output_filename = os.path.join(output_plots_folder, "chosen_{}_{}.png".format(metadata_column, metabolite_id))

            p = (
                ggplot(long_data_df)
                + geom_boxplot(aes(x="factor({})".format(metadata_column), y="value", fill=metadata_column))
            )

            if metadata_facet_column is not None and metadata_facet_column != "None":
                p = p + facet_wrap(facets=metadata_facet_column)

            p.save(output_filename)

            output_stats_dict = {}
            output_stats_dict["metadata_column"] = metadata_column
            output_stats_dict["condition_first"] = condition_first
            output_stats_dict["condition_second"] = condition_second
            output_stats_dict["stat"] = stat
            output_stats_dict["pvalue"] = pvalue
            output_stats_dict["boxplotimg"] = os.path.basename(output_filename)

            output_stats_list.append(output_stats_dict)

        metadata_columns_summary_df = pd.DataFrame(output_stats_list)
        metadata_columns_summary_df.to_csv(os.path.join(output_summary_folder, "chosen_columns.tsv"), sep="\t", index=False)



def main():
    parser = argparse.ArgumentParser(description='Calculate some stats')
    parser.add_argument('quantification_file', help='mzmine2 style quantification filename')
    parser.add_argument('metadata_folder', help='metadata_folder')
    parser.add_argument('output_stats_folder', help='output_stats_folder')
    parser.add_argument('output_images_folder', help='output_images_folder')
    parser.add_argument('--metadata_column', help='metadata_column', default=None)
    parser.add_argument('--condition_first', help='condition_first', default=None)
    parser.add_argument('--condition_second', help='condition_second', default=None)
    parser.add_argument('--metadata_facet_column', help='metadata_facet_column', default=None)
    args = parser.parse_args()

    metadata_files = glob.glob(os.path.join(args.metadata_folder, "*"))

    print(metadata_files)

    if len(metadata_files) == 1:
        calculate_statistics(args.quantification_file, 
            metadata_files[0], 
            args.output_stats_folder, 
            output_plots_folder=args.output_images_folder,
            metadata_column=args.metadata_column,
            condition_first=args.condition_first,
            condition_second=args.condition_second,
            metadata_facet_column=args.metadata_facet_column)

if __name__ == "__main__":
    main()

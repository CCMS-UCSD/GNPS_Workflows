import os
import sys
import argparse
import pandas as pd
from plotnine import *
import glob
from scipy.stats import mannwhitneyu

import metadata_permanova_prioritizer
import ming_parallel_library

GLOBAL_DF = None

# Lets refer to data as a global, bad practice, but we need speed
def plot_box(input_params):
    # Making sure if we have plotting problems, we ignore them
    try:
        global GLOBAL_DF
        variable_value = int(input_params["variable_value"])
        metadata_column = input_params["metadata_column"]
        long_form_df = GLOBAL_DF

        # Filtering the data
        if "metadata_conditions" in input_params:
            if input_params["metadata_conditions"] is not None:
                metadata_conditions = input_params["metadata_conditions"].split(";")
                long_form_df = long_form_df[long_form_df[metadata_column].isin(metadata_conditions)]

        long_form_df = long_form_df[long_form_df["featureid"] == variable_value]
        p = (
            ggplot(long_form_df)
            + geom_boxplot(aes(x="factor({})".format(metadata_column), y="featurearea", fill=metadata_column))
        )

        if "metadata_facet" in input_params:
            if input_params["metadata_facet"] is not None and input_params["metadata_facet"] != "None":
                p = p + facet_wrap(facets=input_params["metadata_facet"])

        output_filename = input_params["output_filename"]
        p.save(output_filename)
    except KeyboardInterrupt:
        raise
    except:
        pass

    return None

def calculate_statistics(input_quant_filename, input_metadata_file, 
                            output_summary_folder, 
                            output_plots_folder=None, 
                            metadata_column=None, 
                            condition_first=None, 
                            condition_second=None,
                            metadata_facet_column=None,
                            run_stats=True,
                            PARALLELISM=8,
                            libraryidentifications_df=None):
    ## Loading feature table
    features_df = pd.read_csv(input_quant_filename, sep=",")
    metadata_df = pd.read_csv(input_metadata_file, sep="\t")

    # removing peak area from columns
    feature_information_df = features_df[["row ID", "row retention time", "row m/z"]]
    features_df.index = features_df["row ID"]
    metabolite_id_list = list(features_df["row ID"])
    headers_to_keep = [header for header in features_df.columns if "Peak area" in header]
    features_df = features_df[headers_to_keep]
    column_mapping = {headers:headers.replace(" Peak area", "") for headers in features_df.columns}
    features_df = features_df.rename(columns=column_mapping)

    # Transpose
    features_df = features_df.T
    
    # Merging with Metadata
    features_df["filename"] = features_df.index
    features_df = features_df.merge(metadata_df, how="inner", on="filename")

    # Format Long version for later plotting
    long_form_df = pd.melt(features_df, id_vars=metadata_df.columns, value_vars=metabolite_id_list)
    long_form_df = long_form_df.rename(columns={"variable":"featureid", "value":"featurearea"})

    # Adding in feature information
    feature_information_df = feature_information_df.rename(columns={"row ID":"featureid", "row retention time":"featurert", "row m/z":"featuremz"})
    long_form_df = long_form_df.merge(feature_information_df, how="left", on="featureid")

    # Adding Library Searhc Inforamtion
    try:
        long_form_df = long_form_df.merge(libraryidentifications_df, how="left", left_on="featureid", right_on="#Scan#")
        long_form_df = long_form_df.drop(columns=["#Scan#"])
    except:
        pass

    long_form_df.to_csv(os.path.join(output_summary_folder, "data_long.csv"), index=False)

    global GLOBAL_DF
    GLOBAL_DF = long_form_df

    metabolite_id_list = metabolite_id_list

    if run_stats == False:
        return

    param_candidates = []
    # If we do not select a column, we don't calculate stats or do any plots
    if metadata_column in features_df:
        output_boxplot_list = []

        columns_to_consider = metadata_permanova_prioritizer.permanova_validation(input_metadata_file) # Ignore
        columns_to_consider = [metadata_column]

        # HACK TO MAKE FASTER
        if len(columns_to_consider) > 0:
            columns_to_consider = columns_to_consider[:5]

        for column_to_consider in columns_to_consider:
            # Loop through all metabolites, and create plots
            if output_plots_folder is not None:
                for metabolite_id in metabolite_id_list:
                    output_filename = os.path.join(output_plots_folder, "{}_{}.png".format(column_to_consider, metabolite_id))

                    input_params = {}
                    input_params["metadata_column"] = column_to_consider
                    input_params["output_filename"] = output_filename
                    input_params["variable_value"] = metabolite_id

                    param_candidates.append(input_params)

                    output_dict = {}
                    output_dict["metadata_column"] = column_to_consider
                    output_dict["boxplotimg"] = os.path.basename(output_filename)
                    output_dict["scan"] = metabolite_id

                    output_boxplot_list.append(output_dict)

        metadata_all_columns_summary_df = pd.DataFrame(output_boxplot_list)
        metadata_all_columns_summary_df.to_csv(os.path.join(output_summary_folder, "all_columns.tsv"), sep="\t", index=False)

    # plotting on a specific column
    if metadata_column in features_df:
        if condition_first is None or condition_second is None:
            continue

        if condition_first == "None" or condition_second == "None":
            continue

        output_stats_list = []

        features_df = features_df[features_df[metadata_column].isin([condition_first, condition_second])]

        data_first_df = features_df[features_df[metadata_column] == condition_first]
        data_second_df = features_df[features_df[metadata_column] == condition_second]

        for metabolite_id in metabolite_id_list:
            try:
                stat, pvalue = mannwhitneyu(data_first_df[metabolite_id], data_second_df[metabolite_id])
            except KeyboardInterrupt:
                raise
            except:
                continue

            output_filename = os.path.join(output_plots_folder, "chosen_{}_{}.png".format(metadata_column, metabolite_id))

            input_params = {}
            input_params["metadata_column"] = metadata_column
            input_params["output_filename"] = output_filename
            input_params["variable_value"] = metabolite_id
            input_params["metadata_facet"] = metadata_facet_column
            input_params["metadata_conditions"] = condition_first + ";" + condition_second
            
            param_candidates.append(input_params)

            output_stats_dict = {}
            output_stats_dict["metadata_column"] = metadata_column
            output_stats_dict["condition_first"] = condition_first
            output_stats_dict["condition_second"] = condition_second
            output_stats_dict["stat"] = stat
            output_stats_dict["pvalue"] = pvalue
            output_stats_dict["boxplotimg"] = os.path.basename(output_filename)
            output_stats_dict["scan"] = metabolite_id

            output_stats_list.append(output_stats_dict)

        metadata_columns_summary_df = pd.DataFrame(output_stats_list)
        metadata_columns_summary_df.to_csv(os.path.join(output_summary_folder, "chosen_columns.tsv"), sep="\t", index=False)

    print("Calculate Plots", len(param_candidates))
    ming_parallel_library.run_parallel_job(plot_box, param_candidates, PARALLELISM, backend="multiprocessing")



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
    parser.add_argument('--libraryidentifications_file', help='libraryidentifications_file', default=None)
    parser.add_argument('--run', help='run', default="Yes")
    args = parser.parse_args()

    metadata_files = glob.glob(os.path.join(args.metadata_folder, "*"))
    if len(metadata_files) != 1:
        exit(0)

    # In case people don't want to run this
    if args.run == "Yes":
        run_stats = True
    else:
        run_stats = False

    libraryidentifications_df = None
    try:
        if libraryidentifications_file is not None and libraryidentifications_file != "None":
            if os.path.exists(libraryidentifications_file):
                libraryidentifications_df = pd.read_csv(libraryidentifications_file, sep="\t", error_bad_lines=False)
                libraryidentifications_df = libraryidentifications_df[["#Scan#", "Compound_Name", "Smiles", "INCHI"]]
    except:
        pass

    try:
        calculate_statistics(args.quantification_file, 
            metadata_files[0], 
            args.output_stats_folder, 
            output_plots_folder=args.output_images_folder,
            metadata_column=args.metadata_column,
            condition_first=args.condition_first,
            condition_second=args.condition_second,
            metadata_facet_column=args.metadata_facet_column,
            run_stats=run_stats,
            libraryidentifications_df=libraryidentifications_df,
            PARALLELISM=20)
    except KeyboardInterrupt:
        raise
    except:
        raise
        pass

if __name__ == "__main__":
    main()

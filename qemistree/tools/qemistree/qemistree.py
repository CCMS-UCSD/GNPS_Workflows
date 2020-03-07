#!/usr/bin/python
import sys
import getopt
import os
import pandas as pd
import argparse
import glob

def main():
    parser = argparse.ArgumentParser(description='Annotate spectra')
    parser.add_argument("input_sirius_mgf")
    parser.add_argument("input_quant_table")
    parser.add_argument("input_metadata_folder")
    parser.add_argument("input_library_identifications_folder")
    parser.add_argument("output_folder")
    parser.add_argument("conda_activate_bin")
    parser.add_argument("conda_environment")
    parser.add_argument("sirius_bin")
    parser.add_argument("--instrument", default="orbitrap")
    parser.add_argument("--sample_metadata_column", default="None")

    args = parser.parse_args()

    instrument = args.instrument
    if instrument == "orbitrap":
        ppm_max = "15"
    else:
        #This means its qtof
        ppm_max = "20"

    output_feature_qza = os.path.join(args.output_folder, "feature-table.qza")
    output_mgf_qza = os.path.join(args.output_folder, "sirius.mgf.qza")
    output_fragtree_qza = os.path.join(args.output_folder, "fragmentation-trees.qza")
    output_formula_qza = os.path.join(args.output_folder, "formula.qza")
    output_fingerprints_qza = os.path.join(args.output_folder, "fingerprints.qza")
    output_qemistree_qza = os.path.join(args.output_folder, "qemistree.qza")
    output_qemistree_pruned_qza = os.path.join(args.output_folder, "qemistree-pruned-smiles.qza")
    output_qemistree_grouped_table_qza = os.path.join(args.output_folder, "qemistree-grouped-table.qza")
    output_merged_feature_table_qza = os.path.join(args.output_folder, "merged-feature-table.qza")
    output_classified_feature_data_qza = os.path.join(args.output_folder, "classified-feature-data.qza")
    output_merged_data_qza = os.path.join(args.output_folder, "merged-feature-data.qza")
    output_distance_matrix_qza = os.path.join(args.output_folder, "distance-matrix.qza")
    output_pcoa_qza = os.path.join(args.output_folder, "pcoa.qza")
    output_emperor_qza = os.path.join(args.output_folder, "emperor.qzv")
    output_qemistree_itol_qzv = os.path.join(args.output_folder, "qemistree-itol.qzv")

    all_cmd = []

    if ".biom" in args.input_quant_table:
        cmd = "source {} {} && LC_ALL=en_US.UTF-8 && export LC_ALL && qiime tools import --input-path {} --output-path {} --type FeatureTable[Frequency]".format(args.conda_activate_bin, args.conda_environment, args.input_quant_table, output_feature_qza)
        all_cmd.append(cmd)
    elif ".qza" in args.input_quant_table:
        cmd = "cp {} {}".format(args.input_quant_table, output_feature_qza)
        all_cmd.append(cmd)
    elif ".csv" in args.input_quant_table:
        print("TODO: Will handle mzmine2 input, would recommend using FMBN first to generate valid qza.")
        exit(1)

    cmd = "source {} {} && LC_ALL=en_US.UTF-8 && export LC_ALL && qiime tools import --input-path {} --output-path {} --type MassSpectrometryFeatures".format(args.conda_activate_bin, args.conda_environment, args.input_sirius_mgf, output_mgf_qza)
    all_cmd.append(cmd)

    cmd = 'source {} {} && LC_ALL=en_US.UTF-8 && export LC_ALL && qiime qemistree compute-fragmentation-trees --p-sirius-path {} \
    --i-features {} \
    --p-ppm-max {} \
    --p-profile {} \
    --p-ionization-mode positive \
    --p-java-flags "-Djava.io.tmpdir=./temp -Xms16G -Xmx64G" \
    --o-fragmentation-trees {}'.format(args.conda_activate_bin, args.conda_environment, args.sirius_bin, output_mgf_qza, ppm_max, instrument, output_fragtree_qza)
    all_cmd.append(cmd)

    cmd = 'source {} {} && LC_ALL=en_US.UTF-8 && export LC_ALL && qiime qemistree rerank-molecular-formulas --p-sirius-path {} \
    --i-features {} \
    --i-fragmentation-trees {} \
    --p-zodiac-threshold 0.98 \
    --p-java-flags "-Djava.io.tmpdir=./temp -Xms16G -Xmx64G" \
    --o-molecular-formulas {}'.format(args.conda_activate_bin, args.conda_environment, args.sirius_bin, output_mgf_qza, output_fragtree_qza, output_formula_qza)
    all_cmd.append(cmd)

    cmd = 'source {} {} && LC_ALL=en_US.UTF-8 && export LC_ALL && qiime qemistree predict-fingerprints --p-sirius-path {} \
    --i-molecular-formulas {} \
    --p-ppm-max {} \
    --p-java-flags "-Djava.io.tmpdir=./temp -Xms16G -Xmx64G" \
    --o-predicted-fingerprints {}'.format(args.conda_activate_bin, args.conda_environment, args.sirius_bin, output_formula_qza, ppm_max, output_fingerprints_qza)
    all_cmd.append(cmd)

    input_library_identifications_files = glob.glob(os.path.join(args.input_library_identifications_folder, "*"))

    # TODO: Add in library identifications to be imported, need to write import statement
    if len(input_library_identifications_files) == 1:
        identifications_qza = os.path.join(args.output_folder, "library_identifications.qza")
        cmd = 'source {} {} && LC_ALL=en_US.UTF-8 && export LC_ALL && qiime tools import \
        --input-path {} \
        --output-path {} \
        --type FeatureData[Molecules]'.format(args.conda_activate_bin, args.conda_environment, \
            input_library_identifications_files[0], \
            identifications_qza)
        all_cmd.append(cmd)

        cmd = 'source {} {} && LC_ALL=en_US.UTF-8 && export LC_ALL && qiime qemistree make-hierarchy \
        --i-csi-results {} \
        --i-feature-tables {} \
        --i-library-matches {}\
        --p-metric euclidean \
        --o-tree {} \
        --o-feature-table {} \
        --o-feature-data {}'.format(args.conda_activate_bin, args.conda_environment, \
            output_fingerprints_qza, \
            output_feature_qza, \
            identifications_qza, \
            output_qemistree_qza, \
            output_merged_feature_table_qza, \
            output_merged_data_qza)
        all_cmd.append(cmd)
    else:
        cmd = 'source {} {} && LC_ALL=en_US.UTF-8 && export LC_ALL && qiime qemistree make-hierarchy \
        --i-csi-results {} \
        --i-feature-tables {} \
        --p-metric euclidean \
        --o-tree {} \
        --o-feature-table {} \
        --o-feature-data {}'.format(args.conda_activate_bin, args.conda_environment, \
            output_fingerprints_qza, \
            output_feature_qza, \
            output_qemistree_qza, \
            output_merged_feature_table_qza, \
            output_merged_data_qza)
        all_cmd.append(cmd)

    # Interfaces with Classyfire
    cmd = 'source {} {} && LC_ALL=en_US.UTF-8 && export LC_ALL && qiime qemistree get-classyfire-taxonomy \
    --i-feature-data {} \
    --o-classified-feature-data {}'.format(args.conda_activate_bin, args.conda_environment, \
        output_merged_data_qza, \
        output_classified_feature_data_qza)
    all_cmd.append(cmd)

    # Prune Tree
    cmd = f'source {args.conda_activate_bin} {args.conda_environment} && LC_ALL=en_US.UTF-8 && export LC_ALL && qiime qemistree prune-hierarchy \
    --i-feature-data {output_classified_feature_data_qza} \
    --p-column smiles \
    --i-tree {output_qemistree_qza} \
    --o-pruned-tree {output_qemistree_pruned_qza}'
    all_cmd.append(cmd)

    cmd = 'source {} {} && LC_ALL=en_US.UTF-8 && export LC_ALL && qiime diversity beta-phylogenetic \
    --i-table {} \
    --i-phylogeny {} \
    --p-metric "weighted_unifrac" \
    --o-distance-matrix {}'.format(args.conda_activate_bin, args.conda_environment, \
        output_merged_feature_table_qza, \
        output_qemistree_qza, \
        output_distance_matrix_qza)
    all_cmd.append(cmd)

    cmd = 'source {} {} && LC_ALL=en_US.UTF-8 && export LC_ALL && qiime diversity pcoa \
    --i-distance-matrix {} \
    --o-pcoa {}'.format(args.conda_activate_bin, args.conda_environment, \
        output_distance_matrix_qza, \
        output_pcoa_qza)
    all_cmd.append(cmd)

    input_metadata_folder = args.input_metadata_folder
    metadata_files = glob.glob(os.path.join(input_metadata_folder, "*"))
    if len(metadata_files) == 1:
        cmd = 'source {} {} && LC_ALL=en_US.UTF-8 && export LC_ALL && qiime emperor plot \
        --i-pcoa {} \
        --m-metadata-file {} \
        --p-ignore-missing-samples \
        --o-visualization {}'.format(args.conda_activate_bin, args.conda_environment, \
            output_pcoa_qza, \
            metadata_files[0], \
            output_emperor_qza)
        all_cmd.append(cmd)

        # Feature Grouping by Metadata
        cmd = f'source {args.conda_activate_bin} {args.conda_environment} && LC_ALL=en_US.UTF-8 && export LC_ALL && qiime feature-table group \
        --i-table {output_feature_qza} \
        --m-metadata-column {args.sample_metadata_column} \
        --p-axis sample \
        --m-metadata-file {metadata_files[0]} \
        --o-grouped-table {output_qemistree_grouped_table_qza} \
        --p-mode mean-ceiling'
        all_cmd.append(cmd)

        # Plotting
        cmd = f'source {args.conda_activate_bin} {args.conda_environment} && LC_ALL=en_US.UTF-8 && export LC_ALL && qiime qemistree plot \
        --i-tree {output_qemistree_pruned_qza} \
        --i-feature-metadata {output_classified_feature_data_qza} \
        --i-grouped-table {output_qemistree_grouped_table_qza} \
        --p-category direct_parent \
        --p-ms2-label False \
        --p-parent-mz True \
        --o-visualization {output_qemistree_itol_qzv}'
        all_cmd.append(cmd)

    #Actually running all the commands
    for cmd in all_cmd:
        print(cmd)
        os.system(cmd)

if __name__ == "__main__":
    main()

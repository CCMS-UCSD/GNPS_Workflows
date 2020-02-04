import argparse
import os
import requests
import shutil
import pandas as pd
import proteosafe
import MetaboDistTrees

parser = argparse.ArgumentParser()
parser.add_argument('GNPS', help='enter your GNPS job ID')
parser.add_argument('molnetenhancer_input_folder', help='molnetenhancer_input')
parser.add_argument('output_folder', help='output_folder')
parser.add_argument("conda_activate_bin")
parser.add_argument("conda_environment")
args = parser.parse_args()

task_id = args.GNPS

task_information = proteosafe.get_task_information("gnps.ucsd.edu", task_id)
print(task_information)

classyfire_result_filename = os.path.join(args.molnetenhancer_input_folder, "ClassyFireResults_Network.txt")

if task_information["workflow"] == "METABOLOMICS-SNETS-V2":

    try:
        manifest_url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&block=main&file=qiime2_output/qiime2_manifest.tsv".format(task_id)
        metadata_url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&block=main&file=qiime2_output/qiime2_metadata.tsv".format(task_id)
        quantification_url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&block=main&file=cluster_buckets/".format(task_id)

        manifest_filename = os.path.join(args.output_folder, "qiime2_manifest.tsv")
        metadata_filename = os.path.join(args.output_folder, "qiime2_metadata.tsv")
        quantification_filename = os.path.join(args.output_folder, "quantification.tsv")
        
        #Pull down the qiime2 data
        with open(manifest_filename, 'wb') as f:
            f.write(requests.get(manifest_url).content)

        with open(metadata_filename, 'wb') as f:
            f.write(requests.get(metadata_url).content)

        with open(quantification_filename, 'wb') as f:
            f.write(requests.get(quantification_url).content)

        bucket_table_df = pd.read_csv(quantification_filename, sep="\t")

        #Performing the MetaboDistTrees
        classyfire_df = pd.read_csv(classyfire_result_filename, sep = '\t')
        lev = ['CF_class','CF_subclass', 'CF_Dparent','cluster.index']

        local_classytree_folder = "classytree"
        MetaboDistTrees.get_classytrees(classyfire_df, bucket_table_df, lev, method='average', metric='jaccard', outputdir=local_classytree_folder)

        #Visualizing in Qiime2
        local_qza_table = os.path.join(args.output_folder, "qiime2_table.qza")
        local_qza_tree = os.path.join(args.output_folder, "qiime2_tree.qza")
        local_qza_distance = os.path.join(args.output_folder, "qiime2_distance.qza")
        local_qza_pcoa = os.path.join(args.output_folder, "qiime2_pcoa.qza")
        local_qzv_emperor = os.path.join(args.output_folder, "qiime2_emperor.qzv")

        all_cmd = []
        all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
            qiime metabolomics import-mzmine2 \
            --p-manifest {} \
            --p-quantificationtable {} \
            --o-feature-table {}".format(args.conda_activate_bin, args.conda_environment, manifest_filename, quantification_filename, local_qza_table))

        classytree_tree_filename = os.path.join(local_classytree_folder, "NewickTree_cluster.index.txt")
        all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
            qiime tools import --type 'Phylogeny[Rooted]' \
            --input-path {} \
            --output-path {}".format(classytree_tree_filename, local_qza_tree))

        all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
            qiime diversity beta \
            --i-table {} \
            --i-phylogeny {} \
            --p-metric weighted_unifrac \
            --o-distance-matrix {}".format(args.conda_activate_bin, args.conda_environment, local_qza_table, local_qza_tree, local_qza_distance))

        all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
            qiime diversity pcoa \
            --i-distance-matrix {} \
            --o-pcoa {}".format(args.conda_activate_bin, args.conda_environment, local_qza_distance, local_qza_pcoa))

        all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
            qiime emperor plot \
            --i-pcoa {} \
            --m-metadata-file {} \
            --o-visualization {} \
            --p-ignore-missing-samples".format(args.conda_activate_bin, args.conda_environment, local_qza_pcoa, output_metadata_filename, local_qzv_emperor))

        for cmd in all_cmd:
            os.system(cmd)

    except KeyboardInterrupt:
        raise
    except:
        print("Error")
        exit(0)

if task_information["workflow"] == "FEATURE-BASED-MOLECULAR-NETWORKING":
    #Workflow versions will eventually be supported
    # task_information["workflow_version"] not in ["1.2.3", "1.2.5", "release_8"]

    try:
        manifest_url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&block=main&file=qiime2_output/qiime2_manifest.tsv".format(task_id)
        metadata_url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&block=main&file=qiime2_output/qiime2_metadata.tsv".format(task_id)
        quantification_url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&block=main&file=quantification_table_reformatted/".format(task_id)

        manifest_filename = os.path.join(args.output_folder, "qiime2_manifest.tsv")
        metadata_filename = os.path.join(args.output_folder, "qiime2_metadata.tsv")
        quantification_filename = os.path.join(args.output_folder, "quantification.tsv")
        
        #Pull down the qiime2 data
        with open(manifest_filename, 'wb') as f:
            f.write(requests.get(manifest_url).content)

        with open(metadata_filename, 'wb') as f:
            f.write(requests.get(metadata_url).content)

        with open(quantification_filename, 'wb') as f:
            f.write(requests.get(quantification_url).content)

        #Rewriting the quantification file format
        bucket_table_df  = pd.read_csv(quantification_filename, sep = ',')
        bucket_table_df.columns = bucket_table_df.columns.str.replace(' Peak area','')
        bucket_table_df.columns = bucket_table_df.columns.str.replace('.mzXML','')
        bucket_table_df.columns = bucket_table_df.columns.str.replace('.mzML','')
        bucket_table_df.columns = bucket_table_df.columns.str.replace('.mgf','')
        if 'row number of detected peaks' in bucket_table_df.columns:
        	bucket_table_df = bucket_table_df.drop(['row m/z', 'row number of detected peaks', 'row retention time'], axis=1)
        else:
        	bucket_table_df = bucket_table_df.drop(['row m/z', 'row retention time'], axis=1)
        bucket_table_df = bucket_table_df.rename(columns = {'row ID':'#OTU ID'})

        cols = [c for c in bucket_table_df.columns if not("Unnamed: " in c)]
        bucket_table_df = bucket_table_df[cols]

        #Performing the MetaboDistTrees
        classyfire_df = pd.read_csv(classyfire_result_filename, sep = '\t')
        lev = ['CF_class','CF_subclass', 'CF_Dparent','cluster.index']

        local_classytree_folder = "classytree"
        MetaboDistTrees.get_classytrees(classyfire_df, bucket_table_df, lev, method='average', metric='jaccard', outputdir=local_classytree_folder)

        #Visualizing in Qiime2
        local_qza_table = os.path.join(args.output_folder, "qiime2_table.qza")
        local_qza_tree = os.path.join(args.output_folder, "qiime2_tree.qza")
        local_qza_distance = os.path.join(args.output_folder, "qiime2_distance.qza")
        local_qza_pcoa = os.path.join(args.output_folder, "qiime2_pcoa.qza")
        local_qzv_emperor = os.path.join(args.output_folder, "qiime2_emperor.qzv")

        all_cmd = []
        all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
            qiime metabolomics import-mzmine2 \
            --p-manifest {} \
            --p-quantificationtable {} \
            --o-feature-table {}".format(args.conda_activate_bin, args.conda_environment, manifest_filename, quantification_filename, local_qza_table))

        classytree_tree_filename = os.path.join(local_classytree_folder, "NewickTree_cluster.index.txt")
        all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
            qiime tools import --type 'Phylogeny[Rooted]' \
            --input-path {} \
            --output-path {}".format(classytree_tree_filename, local_qza_tree))

        all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
            qiime diversity beta \
            --i-table {} \
            --i-phylogeny {} \
            --p-metric weighted_unifrac \
            --o-distance-matrix {}".format(args.conda_activate_bin, args.conda_environment, local_qza_table, local_qza_tree, local_qza_distance))

        all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
            qiime diversity pcoa \
            --i-distance-matrix {} \
            --o-pcoa {}".format(args.conda_activate_bin, args.conda_environment, local_qza_distance, local_qza_pcoa))

        all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
            qiime emperor plot \
            --i-pcoa {} \
            --m-metadata-file {} \
            --o-visualization {} \
            --p-ignore-missing-samples".format(args.conda_activate_bin, args.conda_environment, local_qza_pcoa, output_metadata_filename, local_qzv_emperor))

        for cmd in all_cmd:
            os.system(cmd)

    except KeyboardInterrupt:
        raise
    except:
        print("Error")
        exit(0)
    
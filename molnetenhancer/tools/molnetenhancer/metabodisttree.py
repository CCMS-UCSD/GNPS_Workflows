import argparse
import os
import requests
import shutil
import pandas as pd
import proteosafe
import MetaboDistTrees

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('GNPS', help='enter your GNPS job ID')
    parser.add_argument('output_folder', help='output_folder')
    parser.add_argument("conda_activate_bin")
    parser.add_argument("conda_environment")
    parser.add_argument('--molnetenhancer',default=None,help='enter MolNetEnhancer ID')
    parser.add_argument('--molnetenhancerfolder',default=None,help='enter MolNetEnhancer classyfire folder')
	
    args = parser.parse_args()
    process(args.GNPS,
        molnetenhancer_id = args.molnetenhancer, 
        molnetenhancer_classyfire_folder = args.molnetenhancerfolder,
        output_folder = args.output_folder,
        local_classytree_folder = 'classytree/', 
        conda_activate_bin = args.conda_activate_bin, 
        conda_environment = args.conda_environment)

# Processing metabodisttree, requires either an existing molnetenhancer job or the file within the workflow
def process(task_id, 
    molnetenhancer_id = None, 
    molnetenhancer_classyfire_folder = None, 
    output_folder = None,
    local_classytree_folder = None, 
    conda_activate_bin = None, 
    conda_environment = None):
    
    classyfire_result_filename = os.path.join(output_folder, "ClassyFireResults_Network.txt")
    task_information = proteosafe.get_task_information("gnps.ucsd.edu", task_id)

    if task_information["workflow"] == "METABOLOMICS-SNETS-V2":

        try:
            manifest_url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&block=main&file=qiime2_output/qiime2_manifest.tsv".format(task_id)
            metadata_url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&block=main&file=qiime2_output/qiime2_metadata.tsv".format(task_id)
            quantification_url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&block=main&file=cluster_buckets/".format(task_id)

            manifest_filename = os.path.join(output_folder, "qiime2_manifest.tsv")
            metadata_filename = os.path.join(output_folder, "qiime2_metadata.tsv")
            quantification_filename = os.path.join(output_folder, "quantification.tsv")
            molnetenhancer_filename = os.path.join(output_folder, "ClassyFireResults_Network.txt")

            os.makedirs(os.path.dirname(manifest_filename), exist_ok=True)
            
            #Pull down the qiime2 data
            with open(manifest_filename, 'wb') as f:
                f.write(requests.get(manifest_url).content)

            with open(metadata_filename, 'wb') as f:
                f.write(requests.get(metadata_url).content)

            with open(quantification_filename, 'wb') as f:
                f.write(requests.get(quantification_url).content)
            
            if molnetenhancer_id is not None:
                # If there is a task, or a path
                molnetenhancer_url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&block=main&folder=output_network/ClassyFireResults_Network.txt".format(molnetenhancer_id)
                with open(molnetenhancer_filename, 'wb') as f:
                    f.write(requests.get(molnetenhancer_url).content)
            else:
                input_filename = os.path.join(molnetenhancer_classyfire_folder, "ClassyFireResults_Network.txt")
                shutil.copyfile(input_filename, molnetenhancer_filename)

            #Reformating metadata
            md  = pd.read_csv(metadata_filename, sep = '\t')
            md['#SampleID'] = md['#SampleID'].str.replace(' Peak area','')
            md['#SampleID'] = md['#SampleID'].str.replace('.mzXML','')
            md['#SampleID'] = md['#SampleID'].str.replace('.mzML','')
            md['#SampleID'] = md['#SampleID'].str.replace('.mgf','')

            md.to_csv(metadata_filename, sep='\t', index = False)
            
            bucket_table_df = pd.read_csv(quantification_filename, sep="\t")

            #Performing the MetaboDistTrees
            classyfire_df = pd.read_csv(classyfire_result_filename, sep = '\t')
            lev = ['CF_class','CF_subclass', 'CF_Dparent','cluster.index']

            MetaboDistTrees.get_classytrees(classyfire_df, bucket_table_df, lev, method='average', metric='jaccard', outputdir=local_classytree_folder)

            #Visualizing in Qiime2
            local_biom_table = os.path.join(output_folder, "qiime2_table.biom")
            local_qza_table = os.path.join(output_folder, "qiime2_table.qza")
            local_qza_tree = os.path.join(output_folder, "qiime2_tree.qza")
            local_qza_distance = os.path.join(output_folder, "qiime2_distance.qza")
            local_qza_pcoa = os.path.join(output_folder, "qiime2_pcoa.qza")
            local_qzv_emperor = os.path.join(output_folder, "qiime2_emperor.qzv")

            quantification_filename = os.path.join(local_classytree_folder,'Buckettable_ChemicalClasses.tsv')

            all_cmd = []
            all_cmd.append("LC_ALL=en_US.UTF-8 && export LC_ALL && source {} {} && \
                biom convert \
                -i {} \
                -o {} \
                --table-type 'OTU table' \
                --to-hdf5".format(conda_activate_bin, conda_environment, quantification_filename, local_biom_table))

            all_cmd.append("LC_ALL=en_US.UTF-8 && export LC_ALL && source {} {} && \
                qiime tools import \
                --type 'FeatureTable[Frequency]' \
                --input-path {} \
                --output-path {}".format(conda_activate_bin, conda_environment, local_biom_table, local_qza_table))
                
            classytree_tree_filename = os.path.join(local_classytree_folder, "NewickTree_cluster.index.txt")
            all_cmd.append("LC_ALL=en_US.UTF-8 && export LC_ALL && source {} {} && \
                qiime tools import --type 'Phylogeny[Rooted]' \
                --input-path {} \
                --output-path {}".format(conda_activate_bin, conda_environment,classytree_tree_filename, local_qza_tree))

            all_cmd.append("LC_ALL=en_US.UTF-8 && export LC_ALL && source {} {} && \
                qiime diversity beta-phylogenetic \
                --i-table {} \
                --i-phylogeny {} \
                --p-metric weighted_unifrac \
                --o-distance-matrix {}".format(conda_activate_bin, conda_environment, local_qza_table, local_qza_tree, local_qza_distance))

            all_cmd.append("LC_ALL=en_US.UTF-8 && export LC_ALL && source {} {} && \
                qiime diversity pcoa \
                --i-distance-matrix {} \
                --o-pcoa {}".format(conda_activate_bin, conda_environment, local_qza_distance, local_qza_pcoa))

            all_cmd.append("LC_ALL=en_US.UTF-8 && export LC_ALL && source {} {} && \
                qiime emperor plot \
                --i-pcoa {} \
                --m-metadata-file {} \
                --o-visualization {} \
                --p-ignore-missing-samples".format(conda_activate_bin, conda_environment, local_qza_pcoa, metadata_filename, local_qzv_emperor))

            for cmd in all_cmd:
                print(cmd)
                os.system('/bin/bash -c "{}"'.format(cmd))

        except KeyboardInterrupt:
            raise
        except:
            print("Error")
            raise

    if task_information["workflow"] == "FEATURE-BASED-MOLECULAR-NETWORKING":
        #Workflow versions will eventually be supported
        # task_information["workflow_version"] not in ["1.2.3", "1.2.5", "release_8"]

        try:
            manifest_url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&block=main&file=qiime2_output/qiime2_manifest.tsv".format(task_id)
            metadata_url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&block=main&file=qiime2_output/qiime2_metadata.tsv".format(task_id)
            quantification_url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&block=main&file=quantification_table_reformatted/".format(task_id)

            manifest_filename = os.path.join(output_folder, "qiime2_manifest.tsv")
            metadata_filename = os.path.join(output_folder, "qiime2_metadata.tsv")
            quantification_filename = os.path.join(output_folder, "quantification.tsv")
            molnetenhancer_filename = os.path.join(output_folder, "ClassyFireResults_Network.txt")
            
            os.makedirs(os.path.dirname(manifest_filename), exist_ok=True)

            #Pull down the qiime2 data
            with open(manifest_filename, 'wb') as f:
                f.write(requests.get(manifest_url).content)

            with open(metadata_filename, 'wb') as f:
                f.write(requests.get(metadata_url).content)

            with open(quantification_filename, 'wb') as f:
                f.write(requests.get(quantification_url).content)

            if molnetenhancer_id is not None:
                # If there is a task, or a path
                molnetenhancer_url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&block=main&folder=output_network/ClassyFireResults_Network.txt".format(molnetenhancer_id)
                with open(molnetenhancer_filename, 'wb') as f:
                    f.write(requests.get(molnetenhancer_url).content)
            else:
                input_filename = os.path.join(molnetenhancer_classyfire_folder, "ClassyFireResults_Network.txt")
                shutil.copyfile(input_filename, molnetenhancer_filename)

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

            #Reformating metadata
            md  = pd.read_csv(metadata_filename, sep = '\t')
            md.sample_name = md.sample_name.str.replace(' Peak area','')
            md.sample_name = md.sample_name.str.replace('.mzXML','')
            md.sample_name = md.sample_name.str.replace('.mzML','')
            md.sample_name = md.sample_name.str.replace('.mgf','')

            md.to_csv(metadata_filename, sep='\t', index = False)

            #Performing the MetaboDistTrees
            classyfire_df = pd.read_csv(classyfire_result_filename, sep = '\t')
            lev = ['CF_class','CF_subclass', 'CF_Dparent','cluster.index']

            MetaboDistTrees.get_classytrees(classyfire_df, bucket_table_df, lev, method='average', metric='jaccard', outputdir=local_classytree_folder)

            #Visualizing in Qiime2
            local_biom_table = os.path.join(output_folder, "qiime2_table.biom")
            local_qza_table = os.path.join(output_folder, "qiime2_table.qza")
            local_qza_tree = os.path.join(output_folder, "qiime2_tree.qza")
            local_qza_distance = os.path.join(output_folder, "qiime2_distance.qza")
            local_qza_pcoa = os.path.join(output_folder, "qiime2_pcoa.qza")
            local_qzv_emperor = os.path.join(output_folder, "qiime2_emperor.qzv")

            quantification_filename = os.path.join(local_classytree_folder,'Buckettable_ChemicalClasses.tsv')

            all_cmd = []
            all_cmd.append("LC_ALL=en_US.UTF-8 && export LC_ALL && source {} {} && \
                biom convert \
                -i {} \
                -o {} \
                --table-type 'OTU table' \
                --to-hdf5".format(conda_activate_bin, conda_environment, quantification_filename, local_biom_table))

            all_cmd.append("LC_ALL=en_US.UTF-8 && export LC_ALL && source {} {} && \
                qiime tools import \
                --type 'FeatureTable[Frequency]' \
                --input-path {} \
                --output-path {}".format(conda_activate_bin, conda_environment, local_biom_table, local_qza_table))

            classytree_tree_filename = os.path.join(local_classytree_folder, "NewickTree_cluster.index.txt")
            all_cmd.append("LC_ALL=en_US.UTF-8 && export LC_ALL && source {} {} && \
                qiime tools import --type 'Phylogeny[Rooted]' \
                --input-path {} \
                --output-path {}".format(conda_activate_bin, conda_environment, classytree_tree_filename, local_qza_tree))

            all_cmd.append("LC_ALL=en_US.UTF-8 && export LC_ALL && source {} {} && \
                qiime diversity beta-phylogenetic \
                --i-table {} \
                --i-phylogeny {} \
                --p-metric weighted_unifrac \
                --o-distance-matrix {}".format(conda_activate_bin, conda_environment, local_qza_table, local_qza_tree, local_qza_distance))

            all_cmd.append("LC_ALL=en_US.UTF-8 && export LC_ALL && source {} {} && \
                qiime diversity pcoa \
                --i-distance-matrix {} \
                --o-pcoa {}".format(conda_activate_bin, conda_environment, local_qza_distance, local_qza_pcoa))

            all_cmd.append("LC_ALL=en_US.UTF-8 && export LC_ALL && source {} {} && \
                qiime emperor plot \
                --i-pcoa {} \
                --m-metadata-file {} \
                --o-visualization {} \
                --p-ignore-missing-samples".format(conda_activate_bin, conda_environment, local_qza_pcoa, metadata_filename, local_qzv_emperor))

            for cmd in all_cmd:
                print(cmd)
                os.system('/bin/bash -c "{}"'.format(cmd))

        except KeyboardInterrupt:
            raise
        except:
            print("Error")
            raise

if __name__=="__main__":
    main()
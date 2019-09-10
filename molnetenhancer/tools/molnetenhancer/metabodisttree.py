import argparse
import os
import requests
import shutil
import pandas as pd
import proteosafe


parser = argparse.ArgumentParser()
parser.add_argument('GNPS', help='enter your GNPS job ID')
parser.add_argument('molnetenhancer_input_folder', help='molnetenhancer_input')
parser.add_argument('output_folder', help='output_folder')
args = parser.parse_args()

task_id = args.GNPS

SERVER_BASE = "http://dorresteinappshub.ucsd.edu:5024"
task_information = proteosafe.get_task_information("gnps.ucsd.edu", task_id)
print(task_information)

classyfire_result_filename = os.path.join(args.molnetenhancer_input_folder, "ClassyFireResults_Network.txt")

if task_information["workflow"] == "METABOLOMICS-SNETS-V2":
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

    metabodist_endpoint = SERVER_BASE + "/processmetabodisttree"

    files = {'manifest': open(manifest_filename, 'r'), \
        'metadata': open(metadata_filename, 'r'), \
        'quantification': open(quantification_filename, 'r'), \
        'classyfireresult': open(classyfire_result_filename, 'r')}

    r_post = requests.post(metabodist_endpoint, files=files, data={"type":"classical"})
    response_dict = r_post.json()
    
    with open(os.path.join(args.output_folder, "metabodistree_table.qza"), 'wb') as f:
        r = requests.get(SERVER_BASE + response_dict["table_qza"], stream=True)
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)

    with open(os.path.join(args.output_folder, "metabodistree_emperor.qzv"), 'wb') as f:
        r = requests.get(SERVER_BASE + response_dict["emperor_qzv"], stream=True)
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)

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
        bucket_table_df = bucket_table_df.drop(['row m/z', 'row number of detected peaks', 'row retention time'], axis=1)
        bucket_table_df = bucket_table_df.rename(columns = {'row ID':'#OTU ID'})

        cols = [c for c in bucket_table_df.columns if not("Unnamed: " in c)]
        bucket_table_df = bucket_table_df[cols]

        bucket_table_df.to_csv(quantification_filename, sep="\t", index=False)

        
        metabodist_endpoint = SERVER_BASE + "/processmetabodisttree"

        files = {'manifest': open(manifest_filename, 'r'), \
            'metadata': open(metadata_filename, 'r'), \
            'quantification': open(quantification_filename, 'r'), \
            'classyfireresult': open(classyfire_result_filename, 'r')}

        r_post = requests.post(metabodist_endpoint, files=files)
        response_dict = r_post.json()
        
        with open(os.path.join(args.output_folder, "metabodistree_table.qza"), 'wb') as f:
            r = requests.get(SERVER_BASE + response_dict["table_qza"], stream=True)
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

        with open(os.path.join(args.output_folder, "metabodistree_emperor.qzv"), 'wb') as f:
            r = requests.get(SERVER_BASE + response_dict["emperor_qzv"], stream=True)
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

    except KeyboardInterrupt:
        raise
    except:
        print("Error")
        exit(0)
    
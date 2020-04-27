import argparse
import requests
import os

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('gnps_task', help="input GNPS molecular networking task id")
parser.add_argument('output_folder', help="output folder with results")
parser.add_argument("conda_activate_bin")
parser.add_argument("conda_environment")

args = parser.parse_args()

# Check type of task
status_url = "https://gnps.ucsd.edu/ProteoSAFe/status_json.jsp?task={}".format(args.gnps_task)
status_json = requests.get(status_url).json()

workflow_name = status_json["workflow"]

if workflow_name == "METABOLOMICS-SNETS-V2":
    table_qza = os.path.join(args.output_folder, "qiime2_table.qza")
    pairs_tsv = os.path.join(args.output_folder, "network_edges.tsv")
    cscs_distance_qza = os.path.join(args.output_folder, "cscs_distance.qza")
    local_qza_pcoa = os.path.join(args.output_folder, "cscs_pcoa.qza")
    metadata_tsv = os.path.join(args.output_folder, "qiime2_metadata.tsv")
    local_qzv_emperor = os.path.join(args.output_folder, "qiime2_emperor.qzv")

    # This is to pull down data for classical molecular networking
    bucket_url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&file=qiime2_output/qiime2_table.qza&block=main".format(args.gnps_task)
    print(bucket_url)
    with open(table_qza, "wb") as outfile:
        outfile.write(requests.get(bucket_url).content)

    # This is to pull down data for classical molecular networking
    pairs_url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&file=networkedges_selfloop/&block=main".format(args.gnps_task)
    print(pairs_url)
    with open(pairs_tsv, "w") as outfile:
        outfile.write(requests.get(pairs_url).text)

    # This is to pull down data for classical molecular networking
    metadata_url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&file=qiime2_output/qiime2_metadata.tsv&block=main".format(args.gnps_task)
    print(metadata_url)
    with open(metadata_tsv, "w") as outfile:
        outfile.write(requests.get(metadata_url).text)

    all_cmd = []

    all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
                qiime cscs cscs \
                --p-css-edges {} \
                --i-features {} \
                --p-cosine-threshold 0.5 \
                --p-normalization \
                --o-distance-matrix {}".format(args.conda_activate_bin, args.conda_environment, pairs_tsv, table_qza, cscs_distance_qza))

    all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
                qiime diversity pcoa \
                --i-distance-matrix {} \
                --o-pcoa {}".format(args.conda_activate_bin, args.conda_environment, cscs_distance_qza, local_qza_pcoa))

    all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
            qiime emperor plot \
            --i-pcoa {} \
            --m-metadata-file {} \
            --o-visualization {} \
            --p-ignore-missing-samples".format(args.conda_activate_bin, args.conda_environment, local_qza_pcoa, metadata_tsv, local_qzv_emperor))

    for cmd in all_cmd:
        print(cmd)
        os.system(cmd)


import argparse
import pyCSCS
import requests

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('gnps_task', help="input GNPS molecular networking task id")
parser.add_argument('output_folder', help="output folder with results")

args = parser.parse_args()

# Check type of task
status_url = "https://gnps.ucsd.edu/ProteoSAFe/status_json.jsp?task={}".format(args.gnps_task)
status_json = requests.get(status_url).json()

workflow_name = status_json["workflow"]

if workflow_name == "METABOLOMICS-SNETS-V2":
    # This is to pull down data for classical molecular networking
    bucket_url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&file=cluster_buckets/&block=main".format(args.gnps_task)
    print(bucket_url)
    with open("bucket_table.tsv", "w") as outfile:
        outfile.write(requests.get(bucket_url).text)

    # This is to pull down data for classical molecular networking
    pairs_url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&file=networkedges_selfloop/&block=main".format(args.gnps_task)
    print(pairs_url)
    with open("network_edges.tsv", "w") as outfile:
        outfile.write(requests.get(pairs_url).text)


    cscs_distance_df = pyCSCS.cscs_from_files("bucket_table.tsv", "network_edges.tsv")

    # Now we wil need to output it
    cscs_distance_df.to_csv(os.path.join(args.output_folder, "cscs_distance.tsv"), sep="\t")



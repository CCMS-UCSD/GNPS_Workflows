import argparse
import math
import pandas as pd
import requests
from tqdm import tqdm
import os
import networkx as nx

def calculate_ratio(summarized_df, test_feature_1, test_feature_2, metadata_column, time_1, time_2, min_area_threshold=0):
    k = 1.0E-10

    feature1_time_1 = summarized_df.loc["{}:{}".format(test_feature_1, time_1)]["featurearea"]
    feature1_time_2 = summarized_df.loc["{}:{}".format(test_feature_1, time_2)]["featurearea"]

    feature2_time_1 = summarized_df.loc["{}:{}".format(test_feature_2, time_1)]["featurearea"]
    feature2_time_2 = summarized_df.loc["{}:{}".format(test_feature_2, time_2)]["featurearea"]
    
    feature1_time_1 = max(float(feature1_time_1), min_area_threshold)
    feature1_time_2 = max(float(feature1_time_2), min_area_threshold)
    
    feature2_time_1 = max(float(feature2_time_1), min_area_threshold)
    feature2_time_2 = max(float(feature2_time_2), min_area_threshold)

    time_1_ratio = (feature2_time_1+k)/(feature1_time_1+k)
    time_2_ratio = (feature2_time_2+k)/(feature1_time_2+k)

    chemdir = (math.log10(time_1_ratio/time_2_ratio))
    
    return chemdir

def calculate_ratio_series(summarized_df, test_feature_1, test_feature_2, metadata_column, time_series, min_area_threshold=0):
    output_list = []
    for i in range(len(time_series) - 1):
        time_1 = time_series[i]
        time_2 = time_series[i+1]
        
        chemdir = calculate_ratio(summarized_df, test_feature_1, test_feature_2, metadata_column, time_1, time_2, min_area_threshold=min_area_threshold)
        
        output_dict = {}
        output_dict["chemdir"] = abs(chemdir)
        output_dict["time_1"] = time_1
        output_dict["time_2"] = time_2
        output_dict["sign"] = math.copysign(1.0, chemdir)
        
        output_list.append(output_dict)
        
    return output_list

# Returns DF of calculated pairs
def calculate_chemdir(long_data_df, pairs_df, time_series_metadata, time_series_list, filter_metadata="None", filter_metadata_term="None", min_area_threshold=0):
    epsilon = 1.0E-10 #For Numerical Instability

    #Filtering
    print("FILTERING")
    if len(filter_metadata) > 0 and filter_metadata != "None":
        long_data_df[filter_metadata] = long_data_df[filter_metadata].astype(str)
        long_data_df = long_data_df[long_data_df[filter_metadata] == str(filter_metadata_term)]

    # Computing all the groupings necessary and median summary
    print("MEDIANS")
    computed_long_df = long_data_df[["featureid", time_series_metadata, "featurearea"]]
    computed_long_df["groupby"] = computed_long_df["featureid"].astype(str) + ":" + computed_long_df[time_series_metadata].astype(str)
    summarized_df = computed_long_df.groupby(by="groupby").median()

    # Iterating through all network edges and calculating the stats
    pairs_chemdir_list = []
    for pair in tqdm(pairs_df.to_dict(orient="records")):
        chemdir_list = calculate_ratio_series(summarized_df, int(pair["CLUSTERID1"]), int(pair["CLUSTERID2"]), time_series_metadata, time_series_list, min_area_threshold=min_area_threshold)
        chemdir_list_df = pd.DataFrame(chemdir_list)
        
        pair["max_chemdir"] = max(chemdir_list_df["chemdir"])
        
        chemdir_argmax = chemdir_list_df["chemdir"].argmax()
        pair["max_comparison"] = chemdir_list_df["time_1"][chemdir_argmax] + ":" + chemdir_list_df["time_2"][chemdir_argmax]
        pair["sign_chemdir"] = chemdir_list_df["sign"][chemdir_argmax]

        if pair["sign_chemdir"] > 0:
            pair["CLUSTERID1_chemdir"] = pair["CLUSTERID2"]
            pair["CLUSTERID2_chemdir"] = pair["CLUSTERID1"]
        else:
            pair["CLUSTERID1_chemdir"] = pair["CLUSTERID1"]
            pair["CLUSTERID2_chemdir"] = pair["CLUSTERID2"]

        pairs_chemdir_list.append(pair)
        
    pairs_chemdir_df = pd.DataFrame(pairs_chemdir_list)

    return pairs_chemdir_df

def add_edges_network(graph_object, pairs_chemdir_df):
    print("+++++++++++++++++++++++++++", graph_object)

    intermediate_edges_to_add = []
    for chemdir_edge in pairs_chemdir_df.to_dict(orient="records"):
        edge_object = {}
        edge_object["node1"] = chemdir_edge["CLUSTERID1_chemdir"]
        edge_object["node2"] = chemdir_edge["CLUSTERID2_chemdir"]
        edge_object["EdgeType"] = "CHEMDIR"
        for key in chemdir_edge:
            edge_object[key] = chemdir_edge[key]

        intermediate_edges_to_add.append((edge_object["node1"], edge_object["node2"], edge_object))

    graph_object.add_edges_from(intermediate_edges_to_add)

    return graph_object


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('task', help='GNPS FBMN Task ID')
    parser.add_argument('metadata_column', help='GNPS FBMN metadata_column')
    parser.add_argument('time_series', help='GNPS FBMN time_series, comma separated')
    parser.add_argument('output_folder', help='output folder')
    parser.add_argument('--filter_metadata', default="None", help='filter_metadata_column')
    parser.add_argument('--filter_metadata_term', default="None", help='filter_metadata_term')
    parser.add_argument('--min_area_threshold', type=int, default=0, help='min_area_threshold')

    args = parser.parse_args()

    # Acquiring Data
    task = args.task
    metadata_column = args.metadata_column
    time_series = args.time_series.split(",")
    filter_metadata_column = args.filter_metadata
    filter_metadata_term = args.filter_metadata_term
    MIN_AREA_THRESHOLD = args.min_area_threshold
    
    long_data_df = pd.read_csv("http://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&block=main&file=feature_statistics/data_long.csv".format(task))
    pairs_df = pd.DataFrame(requests.get("https://gnps.ucsd.edu/ProteoSAFe/result_json.jsp?task={}&view=network_pairs_specnets_allcomponents".format(task)).json()["blockData"])

    pairs_chemdir_df = calculate_chemdir(long_data_df, 
                                        pairs_df, 
                                        metadata_column, 
                                        time_series, 
                                        filter_metadata=filter_metadata_column, 
                                        filter_metadata_term=filter_metadata_term, 
                                        min_area_threshold=MIN_AREA_THRESHOLD)

    output_pairs_filename = os.path.join(args.output_folder, "chemdir_pairs.tsv")
    pairs_chemdir_df.to_csv(output_pairs_filename, sep="\t", index=False)

    # Formatting for GraphML
    r = requests.get("http://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&block=main&file=gnps_molecular_network_graphml/".format(task))
    G = nx.parse_graphml(r.text)
    merged_G = add_edges_network(G, pairs_chemdir_df)
    nx.write_graphml(merged_G, os.path.join(args.output_folder, "chemdir_network.graphml"), prettyprint=True)

if __name__ == "__main__":
    main()
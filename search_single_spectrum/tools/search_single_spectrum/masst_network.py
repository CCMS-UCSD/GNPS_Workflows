import requests
import pandas as pd
import networkx as nx
import argparse
import ming_gnps_library

def main():
    parser = argparse.ArgumentParser(description='Create masst network')
    parser.add_argument('input_match_results', help='input_match_results')
    parser.add_argument('output_network', help='output_network')
    parser.add_argument('--createnetwork', default="No", help='createnetwork')
    
    args = parser.parse_args()

    if args.createnetwork == "Yes":
        try:
            spectra_matches_df = pd.read_csv(args.input_match_results, sep="\t")
            create_masst_network(spectra_matches_df, args.output_network)
        except:
            with open(args.output_network, "w") as o:
                o.write("EMPTY")
    else:
        with open(args.output_network, "w") as o:
            o.write("EMPTY")



def create_masst_network(spectra_matches_df, output_graphml, output_image=None):
    # Loading all Datasets Information
    dataset_matches = list(set(spectra_matches_df["dataset_id"]))
    all_datasets = requests.get("https://massive.ucsd.edu/ProteoSAFe/datasets_json.jsp#%7B%22query%22%3A%7B%7D%2C%22table_sort_history%22%3A%22createdMillis_dsc%22%7D").json()["datasets"]

    all_node_usi_list = []

    # Source MASST USI
    output_dict = {}
    output_dict["usi"] = "mzspec:GNPS:TASK-c6b2797224f34d819d20dd7af622bc6b-spectra/:scan:1"
    output_dict["dataset"] = "QUERY"
    output_dict["scan"] = 1

    all_node_usi_list.append(output_dict)

    # Getting all the MASST data
    from tqdm import tqdm
    for dataset in tqdm(dataset_matches):
        try:
            filtered_dataset = [current_dataset for current_dataset in all_datasets if current_dataset["dataset"] == dataset]
            dataset_task = filtered_dataset[0]["task"]
            continuous_id = requests.get("http://gnps.ucsd.edu/ProteoSAFe/ContinuousIDServlet?task={}".format(dataset_task)).json()
            
            network_url = "https://gnps.ucsd.edu/ProteoSAFe/result_json.jsp?task={}&view=clusters_network_pairs".format(continuous_id["jobs"][0]["task"])
            data = requests.get(network_url).json()['blockData']
            network_df = pd.DataFrame(data)
        except:
            continue
        
        dataset_spectra_matches = spectra_matches_df[spectra_matches_df["dataset_id"] == dataset]
        clusters_matched = list(set(dataset_spectra_matches["cluster_scan"]))

        # Grabbing identification information
        try:
            dataset_identifications = ming_gnps_library.get_dataset_current_continuous_identifications(dataset_task)
            dataset_identifications_df = pd.DataFrame(dataset_identifications)
            #print(dataset_identifications_df.columns)
        except:
            pass
        
        network_df["Node1"] = network_df["Node1"].astype(int)
        filtered_edges = network_df[network_df["Node1"].isin(clusters_matched)]
        
        for edge in filtered_edges.to_dict(orient="records"):
            cluster = edge["Node2"]
            usi = "mzspec:GNPS:TASK-{}-speccontinuous/speccontinuous-00000.mgf:scan:{}".format(continuous_id["jobs"][0]["task"], cluster)
            output_dict = {}
            output_dict["usi"] = usi
            output_dict["dataset"] = filtered_dataset[0]["dataset"]
            output_dict["scan"] = cluster

            try:
                filtered_identifications_df = dataset_identifications_df[dataset_identifications_df["#Scan#"] == cluster]
                identification_dict = filtered_identifications_df.to_dict(orient="records")[0]

                output_dict["Compound_Name"] = identification_dict["Compound_Name"]
                output_dict["Smiles"] = identification_dict["Smiles"]
                output_dict["INCHI"] = identification_dict["INCHI"]
                output_dict["MQScore"] = identification_dict["MQScore"]
                output_dict["SpectrumID"] = identification_dict["SpectrumID"]
            except:
                pass

            all_node_usi_list.append(output_dict)

    # Now we will load up all the spectra and do stuff with it
    from ming_spectrum_library import Spectrum
    import spectrum_alignment
    all_spectra_list = []
    for usi_dict in tqdm(all_node_usi_list):
        usi = usi_dict["usi"]
        display_information = "{}:{}".format(usi_dict["dataset"], usi_dict["scan"])

        url = "https://metabolomics-usi.ucsd.edu/json/?usi={}".format(usi)
        spectrum_json = requests.get(url).json()

        spectrum = Spectrum("", display_information, display_information, spectrum_json["peaks"], spectrum_json["precursor_mz"], 1, 2)

        spectrum.dataset = usi_dict["dataset"]
        spectrum.usi = usi_dict["usi"]
        spectrum.Compound_Name = usi_dict.get("Compound_Name", "N/A")
        spectrum.Smiles = usi_dict.get("Smiles", "N/A")
        spectrum.INCHI = usi_dict.get("INCHI", "N/A")
        spectrum.MQScore = usi_dict.get("MQScore", "N/A")
        spectrum.SpectrumID = usi_dict.get("SpectrumID", "N/A")

        all_spectra_list.append(spectrum)

    min_score = 0.7
    min_matched_peaks = 5

    # Let's create a network now
    G = nx.Graph()
    for i, spectrum1 in tqdm(enumerate(all_spectra_list)):
        for j, spectrum2 in enumerate(all_spectra_list):
            if i <= j:
                continue

            if spectrum1.usi == spectrum2.usi:
                continue
            
            # Doing a network here
            total_score, reported_alignments = spectrum_alignment.score_alignment(spectrum1.peaks, spectrum2.peaks, spectrum1.mz, spectrum2.mz, 0.5, max_charge_consideration=1)
            if total_score < min_score:
                continue
            
            if len(reported_alignments) < min_matched_peaks:
                continue

            G.add_edge(spectrum1.scan, spectrum2.scan, cosine_score=total_score, matched_peaks=len(reported_alignments))

            # Adding Node Attributes
            G.nodes[spectrum1.scan]["mz"] = spectrum1.mz
            G.nodes[spectrum2.scan]["mz"] = spectrum2.mz
            G.nodes[spectrum1.scan]["dataset"] = spectrum1.dataset
            G.nodes[spectrum2.scan]["dataset"] = spectrum2.dataset
            G.nodes[spectrum1.scan]["Compound_Name"] = spectrum1.Compound_Name
            G.nodes[spectrum2.scan]["Compound_Name"] = spectrum2.Compound_Name
            G.nodes[spectrum1.scan]["Smiles"] = spectrum1.Smiles
            G.nodes[spectrum2.scan]["Smiles"] = spectrum2.Smiles
            G.nodes[spectrum1.scan]["INCHI"] = spectrum1.INCHI
            G.nodes[spectrum2.scan]["INCHI"] = spectrum2.INCHI
            G.nodes[spectrum1.scan]["MQScore"] = spectrum1.MQScore
            G.nodes[spectrum2.scan]["MQScore"] = spectrum2.MQScore


    import matplotlib.pyplot as plt
    import molecular_network_filtering_library

    molecular_network_filtering_library.filter_top_k(G, 10)

    nx.draw(G, with_labels=True, font_weight='bold')        
    nx.write_graphml(G, output_graphml)
    if output_image is not None:
        plt.savefig(output_image, format="PNG")


if __name__ == "__main__":
    main()

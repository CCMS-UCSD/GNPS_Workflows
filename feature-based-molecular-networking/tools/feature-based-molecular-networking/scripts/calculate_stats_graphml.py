#import_all_modules
import networkx as nx
import sys

def calculate_stats(input_graphml, output_file):
    G = nx.read_graphml(input_graphml)
    G_nodes=G.nodes()
    no_nodes = nx.number_of_nodes(G)
    G_edges=G.edges()

    no_edges_try = nx.number_of_edges(G)
    nodes_str = str(no_nodes)
    edges_str = str(no_edges_try)

    self_loops = nx.number_of_selfloops(G)
    connected_comp = no_nodes - self_loops
    connected_comp_str = str(connected_comp)

    no_ann_nodes = nx.get_node_attributes(G,'Compound_Name')
    len_no_ann_nodes = len(no_ann_nodes)
    no_ann_nodes_str = str(len_no_ann_nodes)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("number of nodes=")
        f.write(nodes_str)
        f.write("\n")
        f.write("number of edges=")
        f.write(edges_str)
        f.write("\n")
        f.write("number of connected components=")
        f.write(connected_comp_str)
        f.write("\n")
        f.write("number of annotated nodes=")
        f.write(no_ann_nodes_str)

def main():
    calculate_stats(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()

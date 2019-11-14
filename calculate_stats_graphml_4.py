#import_all_modules
import networkx as nx
import sys

#read-in_network_from_GNPS

calculate_stats_graphml_4 = sys.argv[0]

G = nx.read_graphml(sys.argv[1])
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

with open(sys.argv[2],'w',encoding = 'utf-8') as f:
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

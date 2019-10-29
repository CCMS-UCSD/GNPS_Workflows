#import_all_modules
import networkx as nx
import sys

#read-in_network_from_GNPS

calculate_stats_graphml_3 = sys.argv[0]

G = nx.read_graphml(sys.argv[1])
G_nodes=G.nodes()
no_nodes = nx.number_of_nodes(G)
G_edges=G.edges()

no_edges_try = nx.number_of_edges(G)
nodes_str = str(no_nodes)
edges_str = str(no_edges_try)

with open(sys.argv[2],'w',encoding = 'utf-8') as f:
    f.write("number of nodes =")
    f.write(nodes_str)
    f.write(" ")
    f.write("number of edges =")
    f.write(edges_str)
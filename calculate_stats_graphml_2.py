#import_all_modules
import networkx as nx
import sys

#read-in_network_from_GNPS

calculate_stats_graphml_2 = sys.argv[0]

G = nx.read_graphml(sys.argv[1])
G_nodes=G.nodes()
no_nodes = nx.number_of_nodes(G)
G_edges=G.edges()

edge_list = nx.to_pandas_edgelist(G)
no_edges = edge_list['source'].count()
nodes_str = str(no_nodes)
edges_str = str(no_edges)
with open(sys.argv[2],'w',encoding = 'utf-8') as f:
    f.write("number of nodes =")
    f.write(nodes_str)
    f.write(" ")
    f.write("number of edges =")
    f.write(edges_str)
import networkx as nx

G = nx.read_graphml('SPEC2VEC-1f01c492-download_graphml-main.graphml')

component_index = 0

for component in nx.connected_components(G):
	component_index += 1
	for node in component:
		if len(component) == 1:
			G.node[node]['componentindex'] = "-1"
		else:
            G.node[node]['componentindex'] = str(component_index)

nx.write_graphml(G, 'output_graphml.graphml')
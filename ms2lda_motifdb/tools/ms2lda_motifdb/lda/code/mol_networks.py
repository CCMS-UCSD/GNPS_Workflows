# coding=utf8
# python code to do some molecular networking

from pprint import PrettyPrinter
import numpy as np


# utility function to create an edge dictionary
def create_edge_dict(scores,min_frag_overlap = 6,min_score = 0.5):
	edge_dict = {}
	for score_row in scores:
		mol1 = score_row[0]
		mol2 = score_row[1]
		score = score_row[2]
		overlap = score_row[3]
		if overlap >= min_frag_overlap and score >= min_score:
			if not mol1 in edge_dict:
				edge_dict[mol1] = {}
			if not mol2 in edge_dict:
				edge_dict[mol2] = {}
			edge_dict[mol1][mol2] = score
			edge_dict[mol2][mol1] = score

	return edge_dict

class Network(object):
	def __init__(self,edge_dict):
		assert self._is_symmetric(edge_dict), "Edge dictionary not symmetric"
		self.edge_dict = edge_dict
		self._compute_degree()


	def _is_symmetric(self,edge_dict):
		# check each edge is in there twice
		for mol,edges in edge_dict.items():
			for target,score in edges.items():
				try:
					s2 = edge_dict[target][mol]
					if not s2 == score:
						return False
				except:
					return False
		return True



	def _compute_degree(self):
		self.n_edges = {}
		for mol in self.edge_dict:
			self.n_edges[mol] = len(self.edge_dict[mol])
	
	def top_k_filter(self,k=10):
		# create a sorted version of the dictionary
		min_scores = {}
		for mol,edges in self.edge_dict.items():
			edge_score = zip(edges.keys(),edges.values())
			edge_score = sorted(edge_score,key = lambda x: x[1],reverse = True)
			if len(edge_score) < k:
				min_scores[mol] = 0.0
			else:
				min_scores[mol] = edge_score[k-1][1]


		filtered_edge_dict = {}
		n_edges = {}
		for mol,edges in self.edge_dict.items():
			filtered_edge_dict[mol] = {}
			for target_mol,score in edges.items():
				if score >= min_scores[mol] and self.edge_dict[target_mol][mol] >= min_scores[target_mol]:
					# keep the edge
					filtered_edge_dict[mol][target_mol] = score
			n_edges[mol] = len(filtered_edge_dict[mol])
		self.edge_dict = filtered_edge_dict
		self.n_edges = n_edges


	def copy(self):
		# make a deep copy of itself and return
		new_edge_dict = {}
		for mol,edges in self.edge_dict.items():
			new_edge_dict[mol] = {}
			for target,score in edges.items():
				new_edge_dict[mol][target] = score
		return Network(new_edge_dict)
	def _extract_component(self,min_score = 0.5,start_node = None):
		if not start_node:
			start_node = self.edge_dict.keys()[0]
		component_nodes = [start_node]
		search_pos = 0
		finished = False
		while not finished:
			edges = self.edge_dict[component_nodes[search_pos]]
			for target_node,score in edges.items():
				if score >= min_score and not target_node in component_nodes:
					component_nodes.append(target_node)
			search_pos += 1
			if search_pos == len(component_nodes):
				finished = True

		# create the new edge dict
		new_edge_dict = {}
		for mol in component_nodes:
			new_edge_dict[mol] = {}
			for target,score in self.edge_dict[mol].items():
				if target in component_nodes:
					new_edge_dict[mol][target] = score

		self._remove_nodes(component_nodes)
		return Network(new_edge_dict)

	def _remove_nodes(self,nodes):
		for node in nodes:
			edges = self.edge_dict[node]
			for target,score in edges.items():
				del self.edge_dict[target][node]
			del self.edge_dict[node]

	def _find_lowest_thresh_edge(self):
		mol1 = self.edge_dict.keys()[0]
		mol2 = self.edge_dict[mol1].keys()[0]
		lowest_thresh = self.edge_dict[mol1][mol2]
		lowest_pair = (mol1,mol2)
		for mol,edges in self.edge_dict.items():
			for target,score in edges.items():
				if score <= lowest_thresh:
					lowest_thresh = score
					lowest_pair = (mol,target)
		return lowest_thresh,lowest_pair

	def _cut(self,min_score = 0.5):
		finished = False
		sub_network = None
		while not finished:
			lowest_thresh,lowest_pair = self._find_lowest_thresh_edge()
			# remove the edge
			del self.edge_dict[lowest_pair[0]][lowest_pair[1]]
			del self.edge_dict[lowest_pair[1]][lowest_pair[0]]
			sub_network = self._extract_component(min_score = min_score,start_node = lowest_pair[0])
			# check if that's the entire network and if it is, we need to remove another edge
			if len(self.edge_dict) == 0:
				self.edge_dict = sub_network.edge_dict
				self._compute_degree()
			else:
				finished = True
		return sub_network

	def n_nodes(self):
		return len(self.edge_dict)

	def convert_to_components(self,min_score=0.5,max_component_size = 100):
		components = []
		while self.n_nodes() > 0:
			components.append(self._extract_component(min_score = min_score))
			print "Found {} components".format(len(components))
		small_enough = []
		needs_cropping = []
		for component in components:
			if component.n_nodes() > max_component_size:
				needs_cropping.append(component)
			else:
				small_enough.append(component)
		while len(needs_cropping) > 0:
			print "Cropping components to have max size = {}".format(max_component_size)
			print "\t{} components ok, {} need cropping".format(len(small_enough),len(needs_cropping))
			new_crop = []
			for component in needs_cropping:
				new_comp = component._cut(min_score = 0.5)
				if new_comp.n_nodes() > max_component_size:
					new_crop.append(new_comp)
				else:
					small_enough.append(new_comp)
				if component.n_nodes() > max_component_size:
					new_crop.append(component)
				else:
					small_enough.append(component)
			needs_cropping = new_crop


		return small_enough

	def write_network(self,csv_writer,heads = False):
		if heads:
			csv_writer.writerow(['sourceNode','targetNode','Weight'])
		done = {}
		for node in self.edge_dict:
			done[node] = {}
		for node,edges in self.edge_dict.items():
			for target,score in edges.items():
				if not node in done[target]:
					csv_writer.writerow([node,target,score])
					done[node][target] = True
	def __str__(self):
		out_str = ""
		out_str += "Network has {} nodes\n".format(self.n_nodes())
		for mol,edges in self.edge_dict.items():
			out_str += str(mol) + " (degree = {})\t".format(len(edges)) + " ".join(["({},{})".format(t,s) for t,s in edges.items()]) + "\n"
		return out_str


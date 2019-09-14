#!/usr/bin/python

import ming_fileio_library
import ming_proteosafe_library

"""
Molecular Network Utilties For Use at GNPS

These classes provide utilies for loading and doing manipulation of the files

Refined Version

"""


class NetworkPair:
	def __init__(self, node1, node2, cosine, deltamz):
		self.node1 = node1
		self.node2 = node2
		self.cosine = cosine
		self.deltamz = deltamz

class OriginalSpectrum:
	def __init__(self, mz, charge, clusterindex, filename, scan):
		self.mz = mz
		self.charge = charge
		self.clusterindex = clusterindex
		self.filename = filename
		self.scan = scan

class ClusterLibraryIdentification:
	def __init__(self, spectrumID, name, smiles, inchi, score, scan):
		self.spectrumID = spectrumID
		self.name = name
		self.smiles = smiles
		self.inchi = inchi
		self.score = score
		self.scan = scan

class ClusterPeptideIdentification:
	def __init__(self, peptide, score, engine):
		self.peptide = peptide
		self.score = score
		self.engine = engine

class ClusterNode:
	def __init__(self, mz, charge, index, number_of_spectra, component_index):
		self.mz = mz
		self.charge = charge
		self.index = index
		self.component = component_index
		self.number_of_spectra = number_of_spectra
		self.constituent_spectra = []
		self.connected_pairs = []
		self.library_identifications = []
		self.all_files_string = ""

	def add_cluster_spectrum(self, filename, scan):
		self.constituent_spectra.append(filename + ":" + scan)

	def add_connected_pair(self, pair_object):
		self.connected_pairs.append(pair_object)

	def get_node_files(self):
		list_files = []
		for token in self.all_files_string.split("###"):
			if len(token.split(":")[0]) > 0:
				list_files.append(token.split(":")[0])
		return list_files

	#Returns whether the node has been identified
	def is_identified(self):
		if len(self.library_identifications) == 0:
			return False
		else:
			return True

	def does_contain_constituent_spectra(self, filename, scan):
		spectrum_key = filename + ":" + scan
		if self.constituent_spectra.count(spectrum_key) > 0:
			return True
		return False


class NetworkConnectedComponent:
	def __init__(self, component_index):
		self.component_index = component_index
		self.nodes = []

	def add_node_to_component(self, clusternode_object):
		self.nodes.append(clusternode_object)

class MolecularNetwork:
	def __init__(self):
		self.nodes = []
		self.index_to_node_map = {} #Optimization for fast access by node index
		self.index_to_neighbors = {} #Key is scan, and points to list of node objects that are neighbors
		self.pairs = []
		self.identifications = []
		self.filemapping = {} 	#Mapping from mangled name to real filename

	def load_network(self, clustersummaryfilename, pairs_filename):
		self.load_clustersummary(clustersummaryfilename)
		self.load_pairsinfo(pairs_filename)

		#Making things consistent after loading individual files

	###
	 # Must be loaded first
	###
	def load_clustersummary(self, clustersummaryfilename):
		row_count, table_data = ming_fileio_library.parse_table_with_headers(clustersummaryfilename)

		for i in range(row_count):
			cluster_index = table_data["cluster index"][i]
			mz = table_data["precursor mass"][i]
			charge = table_data["precursor charge"][i]
			parentmass = table_data["parent mass"][i]
			number_of_spectra = table_data["number of spectra"][i]
			all_files = table_data["AllFiles"][i]

			componentindex = -1
			if "componentindex" in table_data:
				componentindex = table_data["componentindex"][i]

			cluster_node = ClusterNode(mz, charge, cluster_index, number_of_spectra, componentindex)
			cluster_node.all_files_string = all_files

			self.nodes.append(cluster_node)
			self.index_to_node_map[cluster_index] = cluster_node

			#Making all the nodes not shit in terms of clustering info
			constituent_spectra = cluster_node.all_files_string.split("###")
			cluster_node.constituent_spectra = constituent_spectra


		#Make stuff consistent with components


	def load_parameters_file(self, paramsfilename):
		#Loading the file mapping
		parameters = ming_proteosafe_library.parse_xml_file(open(paramsfilename, "r"))
		mangled_mapping = ming_proteosafe_library.get_mangled_file_mapping(parameters)
		self.mangled_mapping = mangled_mapping


	###
	 # Loading the pairs info
	 # Requires clustersummary to be loaded first
	###
	def load_pairsinfo(self, pairs_filename):
		row_count, table_data = ming_fileio_library.parse_table_with_headers(pairs_filename)

		if "CLUSTERID1" in table_data:
			for i in range(row_count):
				node1 = table_data["CLUSTERID1"][i]
				node2 = table_data["CLUSTERID2"][i]
				cosine = table_data["Cosine"][i]
				deltamz = table_data["DeltaMZ"][i]
				pair = NetworkPair(node1, node2, cosine, deltamz)
				self.pairs.append(pair)
		else:
			row_count, table_data = ming_fileio_library.parse_table_without_headers(pairs_filename)
			for i in range(row_count):
				node1 = table_data[0][i]
				node2 = table_data[1][i]
				cosine = table_data[4][i]
				deltamz = table_data[2][i]
				pair = NetworkPair(node1, node2, cosine, deltamz)
				self.pairs.append(pair)



		#Make stuff consistent, specifically adding adjacency list
		for pair in self.pairs:
			node1 = pair.node1
			node2 = pair.node2

			if not(node1 in self.index_to_neighbors):
				self.index_to_neighbors[node1] = []

			if not(node2 in self.index_to_neighbors):
				self.index_to_neighbors[node2] = []

			self.index_to_neighbors[node1].append(node2)
			self.index_to_neighbors[node2].append(node1)

	#Loading the identifications of the clusters by library search
	def load_gnps_librarysearch(self, identification_filename):
		row_count, table_data = ming_fileio_library.parse_table_with_headers(identification_filename)
		for i in range(row_count):
			compound_name = table_data["Compound_Name"][i]
			smiles = table_data["Smiles"][i]
			inchi = table_data["INCHI"][i]
			SpectrumID = table_data["SpectrumID"][i]
			score = table_data["MQScore"][i]
			scan = table_data["#Scan#"][i]
			identification = ClusterLibraryIdentification(SpectrumID, compound_name, smiles, inchi, score, scan)
			self.identifications.append(identification)

			#Finding the cluster
			if scan in self.index_to_node_map:
				self.index_to_node_map[scan].library_identifications.append(identification)

	#Getter Functions
	def get_node_count(self):
		return len(self.nodes)

	#Get total number of raw spectra that was in consideration for networking
	def get_cluster_total_spectrum_counts(self):
		total_count = 0
		for node in self.nodes:
			total_count += int(node.number_of_spectra)
		return total_count

	#Returns a list of all the filenames in the network
	def get_files_list_in_clusters(self):
		file_list = []
		for node in self.nodes:
			file_list += node.get_node_files()
		return list(set(file_list))

	#Getting the Cluster Information by Index
	def get_cluster_index(self, scan):
		if scan in self.index_to_node_map:
			return self.index_to_node_map[scan]
		return None

	def get_node_neighbors(self, scan):
		if scan in self.index_to_neighbors:
			return self.index_to_neighbors[scan]
		else:
			return []

	def get_unidentified_node_neighbors(self, scan):
		if scan in self.index_to_neighbors:
			return_nodes = []
			for node_id in self.index_to_neighbors[scan]:
				if not self.get_cluster_index(node_id).is_identified():
					return_nodes.append(node_id)
		else:
			return []

		return return_nodes

	def get_identified_node_neighbors(self, scan):
		if scan in self.index_to_neighbors:
			return_nodes = []
			for node_id in self.index_to_neighbors[scan]:
				if self.get_cluster_index(node_id).is_identified():
					return_nodes.append(node_id)
		else:
			return []

		return return_nodes

	def get_node_from_raw_data(self, raw_filename, scan_number):
		for node in self.nodes:
			if node.does_contain_constituent_spectra(raw_filename, scan_number):
				return node

		return None

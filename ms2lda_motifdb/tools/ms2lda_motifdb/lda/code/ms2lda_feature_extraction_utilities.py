# A collection of useful functions and objects


# Creates a corpus in reverse: i.e. keys are features, values are a set of docs
def reverse_corpus(corpus):
	reverse_corpus = {}
	for doc,spectrum in corpus.items():
		for f,_ in spectrum.items():
			if not f in reverse_corpus:
				reverse_corpus[f] = set()
			reverse_corpus[f].add(doc)
	return reverse_corpus

# Counts how many docs each feature appears in
def count_docs(reverse_corpus,corpus,min_percent = 0.0,max_percent = 100.0):
	doc_counts = {}
	n_docs = len(corpus)
	for feature,docs in reverse_corpus.items():
		doc_counts[feature] = (len(docs),(100.0*len(docs))/n_docs)
	df = zip(doc_counts.keys(),doc_counts.values())
	to_remove = []
	if min_percent > 0.0:
		df2 = filter(lambda x: x[1][1] < min_percent,df)
		tr,_ = zip(*df2)
		to_remove += tr
	if max_percent < 100.0:
		df2 = filter(lambda x: x[1][1] > max_percent,df)
		tr,_ = zip(*df2)
		to_remove += tr
	to_remove = set(to_remove)

	return doc_counts,to_remove

# remove a particular set of features from the corpus
def remove_features(corpus,to_remove):
	for doc,spectrum in corpus.items():
		features = set(spectrum.keys())
		overlap = features.intersection(to_remove)
		for f in overlap:
			del spectrum[f]
	return corpus


def bin_diff(diff,bin_width = 0.005):
	import numpy as np
	# return the name of the bin center for the mass given the specified bin width
	offset = bin_width/2.0
	diff += offset
	bin_no = np.floor(diff / bin_width)
	bin_lower = bin_no*bin_width
	bin_upper = bin_lower + bin_width
	bin_middle = (bin_lower + bin_upper)/2.0
	bin_middle -= offset
	return "{:.4f}".format(bin_middle)

def convert_corpus_to_counts(corpus):
	n_files = len(corpus)
	counts = {}
	for file,spectra in corpus.items():
		counts[file] = {}
		for mol,spectrum in spectra.items():
			for mz,intensity in spectrum.items():
				if not mz in counts[file]:
					counts[file][mz] = 1
				else:
					counts[file][mz] += 1
	return counts

def make_count_matrix(counts):
	feature_index = {}
	sample_index = {}
	import numpy as np
	from scipy.sparse import coo_matrix
	filepos = 0
	featurepos = 0
	spdata = []
	file_list = sorted(counts.keys())
	for file in file_list:
		file_counts = counts[file]
		sample_index[file] = filepos
		filepos += 1
		for feature,count in file_counts.items():
			if not feature in feature_index:
				feature_index[feature] = featurepos
				featurepos += 1
			spdata.append((sample_index[file],feature_index[feature],count))
	i,j,k = zip(*spdata)
	co = coo_matrix((k,(j,i))) # note j,i: rows are features
	sample_list = ['' for s in sample_index]
	for s,pos in sample_index.items():
		sample_list[pos] = s
	feature_list = ['' for s in feature_index]
	for s,pos in feature_index.items():
		feature_list[pos] = s	
	return np.array(co.todense()),sample_index,feature_index,sample_list,feature_list

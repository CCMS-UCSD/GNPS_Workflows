import numpy as np
from scipy.special import psi as psi

# doesn't work ????
# def par_e_step(lda):
# 	beta = lda.e_step()
# 	return beta

def par_e_step(parameters):
 
	corpus, K, n_words, doc_index, alpha, word_index, phi_matrix, beta_matrix, gamma_matrix = parameters
	temp_beta = np.zeros((K, n_words))
	new_gamma_matrix = np.zeros_like(gamma_matrix)
	for doc in corpus:
		# print doc
		d = doc_index[doc]
		temp_gamma = np.zeros(K) + alpha
		for word in corpus[doc]:
			w = word_index[word]
			phi_matrix[doc][word] = beta_matrix[:,w]*np.exp(psi(gamma_matrix[d,:])).T
			phi_matrix[doc][word] /= phi_matrix[doc][word].sum()
			temp_gamma += phi_matrix[doc][word]*corpus[doc][word]
			temp_beta[:,w] += phi_matrix[doc][word] * corpus[doc][word]
 
		new_gamma_matrix[d,:] = temp_gamma
 
	return temp_beta, phi_matrix, new_gamma_matrix
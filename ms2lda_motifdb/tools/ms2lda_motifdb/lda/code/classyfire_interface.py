# Interface with classyfire
# Methods to return useful classyfire information from an InChIKey
import urllib2
import json
import jsonpickle

def get_taxa_path_and_substituents(inchikey):

    
    # store the taxonomy path for this inchikey here
    taxa_path = []
    substituents = []
    try:
        url = 'http://classyfire.wishartlab.com/entities/%s.json' % inchikey
        response = urllib2.urlopen(url)
        data = json.load(response)       

        # add the top-4 taxa
        keys = ['kingdom', 'superclass', 'class', 'subclass']
        for key in keys:
            if data[key] is not None:
                taxa_path.append(data[key]['name'])

        # add all the intermediate taxa >level 4 but above the direct parent
        for entry in data['intermediate_nodes']:
            taxa_path.append(entry['name'])

        # add the direct parent
        taxa_path.append(data['direct_parent']['name'])
        substituents = data.get('substituents',None)
    except:
        print "Failed on {}".format(inchikey)
    return taxa_path,substituents

def make_corpora(documents):
    # Gets the substituent and taxa corpora for documents 
    # documents is a dictionary with key doc name and value InChIKey
    taxa = {}
    substituents = {}

    for i,document in enumerate(documents):
        inchikey = documents[document]
        taxa[document],substituents[document] = get_taxa_path_and_substituents(inchikey)
        if i % 10 == 0:
            print "Done {} of {}".format(i,len(documents))

    # corpora format is a dictionary of binary lists
    taxa_corpus = {}
    substituents_corpus = {}
    taxa_list = []
    substituents_list = []


    for document in documents:
        if len(taxa[document]) > 0:
            taxa_list = list(set(taxa_list + taxa[document]))
        if len(substituents[document]) > 0:
            substituents_list = list(set(substituents_list + substituents[document]))


    n_taxa = len(taxa_list)
    n_substituents = len(substituents_list)
    for document in documents:
        if len(taxa[document]) > 0:
            taxa_corpus[document] = [0 for i in range(n_taxa)]
            for taxa_term in taxa[document]:
                taxa_corpus[document][taxa_list.index(taxa_term)] = 1
        if len(substituents[document]) > 0:        
            substituents_corpus[document] = [0 for i in range(n_substituents)]
            for substituents_term in substituents[document]:
                substituents_corpus[document][substituents_list.index(substituents_term)] = 1

    return taxa_list,taxa_corpus,substituents_list,substituents_corpus


def lda_projection(gamma,corpus,corpus_list,doc_index,n_its = 50,xi = None,hyp = (1.1,1.1)):

    n_docs,K = gamma.shape
    n_terms = len(corpus_list)

    from scipy.special import psi
    import numpy as np

    elogtheta = psi(gamma) - psi(gamma.sum(axis=1))[:,None]
    exp_elogtheta = np.exp(elogtheta)
    # delta = {}
    # for document in corpus:
    #     delta[document] = np.zeros((n_terms,K),np.float)

    # Initialise xi
    if xi == None:
        xi = np.random.rand(n_terms,K)

    for it in range(n_its):
        print "Iteration {}".format(it)
        temp_xi = np.zeros((n_terms,K),np.float)
        delta_sum = np.zeros((n_terms,K),np.float)
        for i,document in enumerate(corpus.keys()):
            if i%500 == 0:
                print "\t{}".format(i)
            try:
                doc_pos = doc_index[document]
                elt = elogtheta[doc_pos,:][None,:]
                nsc = np.array(corpus[document])
                nsc = nsc[:,None]
                temp = nsc*np.log(xi) + (1-nsc)*np.log(1-xi)
                temp += elt
                mtemp = temp.max(axis=1)
                temp = np.exp(temp - mtemp[:,None])
                delt = temp / np.sum(temp,axis=1)[:,None]
                # delta[document] = temp / np.sum(temp,axis=1)[:,None]
                
                # temp_xi += nsc*delta[document]
                temp_xi += nsc*delt

                # delta_sum += delta[document]
                delta_sum += delt
            except:
                # This means the document doesnt exist. This can happen as it may have no features
                pass
        # Update the xi
        new_xi = (temp_xi + hyp[0] - 1)/(delta_sum + hyp[0] + hyp[1] - 2)
        xi_change = (np.abs(new_xi - xi)).sum()
        print "Total xi change: {}".format(xi_change)
        xi = new_xi

    return xi





    

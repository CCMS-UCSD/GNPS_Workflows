# -*- coding: utf-8 -*-
import multiprocessing
import pickle
import time
import sys

from scipy.special import polygamma as pg
from scipy.special import psi as psi

from parallel_calls import par_e_step
import numpy as np

SMALL_NUMBER = 1e-100

# This is a Gibbs sampler LDA object. Don't use it. I'll probably delete it when I have time
class LDA(object):
    def __init__(self,corpus,K=20,alpha=1,beta=1):
        self.corpus = corpus
        self.K = K
        self.alpha = alpha
        self.beta = beta
        self.collect_words()
        self.initialise()

    def collect_words(self):
        self.words = []
        self.nwords = 0
        self.ndocs = len(self.corpus)
        docpos = 0
        self.doc_index = {}
        self.word_index = {}
        for doc in self.corpus:
            self.doc_index[doc] = docpos
            docpos += 1
            for word in self.corpus[doc]:
                if not word in self.word_index:
                    self.word_index[word] = self.nwords
                    self.nwords += 1

    def initialise(self):
        self.Z = {}
        self.doc_topic_counts = np.zeros((self.K,self.ndocs),np.int) + self.alpha
        self.topic_word_counts = np.zeros((self.K,self.nwords),np.int) + self.beta
        self.topic_totals = np.zeros((self.K),np.int) + self.beta
        self.total_words = 0
        self.word_counts = {}
        for word in self.word_index:
            self.word_counts[word] = 0

        for doc in self.corpus:
            self.Z[doc] = {}
            di = self.doc_index[doc]
            for word in self.corpus[doc]:
                wi = self.word_index[word]
                count = self.corpus[doc][word]
                self.total_words += count
                self.word_counts[word] += count
                self.Z[doc][word] = []
                for c in range(count):
                    topic = np.random.randint(self.K)
                    self.topic_totals[topic] += 1
                    self.Z[doc][word].append(topic)
                    self.doc_topic_counts[topic,di] += 1
                    self.topic_word_counts[topic,wi] += 1

        # Output things
        self.post_sample_count = 0.0
        self.post_mean_theta = np.zeros((self.K,self.ndocs),np.float)
        self.post_mean_topics = np.zeros((self.K,self.nwords),np.float)

    def gibbs_iteration(self,n_samples = 1,verbose = True,burn = True):
        # Does one gibbs step
        for sample in range(n_samples):
            if verbose:
                print "Sample {} of {} (Burn is {})".format(sample,n_samples,burn)
            for doc in self.corpus:
                di = self.doc_index[doc]
                for word in self.corpus[doc]:
                    wi = self.word_index[word]
                    for i,instance in enumerate(self.Z[doc][word]):
                        current_topic = instance
                        self.doc_topic_counts[current_topic,di] -= 1
                        self.topic_word_counts[current_topic,wi] -= 1
                        self.topic_totals[current_topic] -= 1

                        # Re-sample
                        p_topic = 1.0*self.topic_word_counts[:,wi] / self.topic_totals
                        p_topic *= self.doc_topic_counts[:,di]
                        p_topic = 1.0*p_topic / p_topic.sum()
                        new_topic = np.random.choice(self.K,p=p_topic)

                        self.Z[doc][word][i] = new_topic

                        self.doc_topic_counts[new_topic,di] += 1
                        self.topic_word_counts[new_topic,wi] += 1
                        self.topic_totals[new_topic] += 1

        if not burn:
            self.post_sample_count += 1.0
            for doc in self.corpus:
                di = self.doc_index[doc]
                tcounts = self.doc_topic_counts[:,di]
                self.post_mean_theta[:,di] += np.random.dirichlet(tcounts)
            for topic in range(self.K):
                wcounts = self.topic_word_counts[topic,:]
                self.post_mean_topics[topic,:] += np.random.dirichlet(wcounts)
            
    def get_post_mean_theta(self):
        return self.post_mean_theta / self.post_sample_count
    def get_post_mean_topics(self):
        return self.post_mean_topics / self.post_sample_count

    def get_mass_plot(self,topic_id):
        pmeantopics = self.get_post_mean_topics()
        m = []
        probs = []
        for word in self.word_index:
            m.append(float(word))
            probs.append(pmeantopics[topic_id,self.word_index[word]])

        m_probs = zip(m,probs)
        m_probs = sorted(m_probs,key=lambda x: x[0])
        m,probs = zip(*m_probs)
        return np.array(m),np.array(probs)

    def plot_topic(self,topic_id,nrows = 10,ncols = 10):

        image_array = np.zeros((nrows,ncols),np.float)
        for doc in self.corpus:
            di = self.doc_index[doc]
            if self.post_sample_count == 0:
                tcounts = self.doc_topic_counts[:,di]
                tprobs = tcounts / 1.0*tcounts.sum()
            else:
                tprobs = self.get_post_mean_theta()
            (r,c) = doc
            image_array[r,c] = tprobs[topic_id,di]

        return image_array

    def get_topic_as_dict(self,topic_id,thresh = 0.001):
        pmt = self.get_post_mean_topics()
        top = {}
        for word in self.word_index:
            pos = self.word_index[word]
            if pmt[topic_id,pos] >= thresh:
                top[word] = pmt[topic_id,pos]
        return top

    def get_topic_as_doc_dict(self,topic_id,thresh = 0.001):
        pmth = self.get_post_mean_theta()
        top = {}
        for doc in self.doc_index:
            pos = self.doc_index[doc]
            if pmth[topic_id,pos] >= thresh:
                top[doc] = pmth[topic_id,pos]
        return top
        
    def get_topic_as_tuples(self,topic_id,thresh = 0.001):
        pmth = self.get_post_mean_topics()
        top = []
        for word in self.word_index:
            pos = self.word_index[word]
            if pmth[topic_id,pos] >= thresh:
                top.append((word,pmth[topic_id,pos]))

        return sorted(top,key = lambda x: x[1], reverse=True)

# This is the LDA implementation to use
# Corpus can be passed in, or loaded from .csv files in joes style
# K = number of topics
# eta = hyperparameter for topics (i.e. pseudo word counts)
# alpha = initial Dirichlet hyperparameter
# update_alpha = boolean to determine whether or not alpha is updated at each iteration
# word_index is a dictionary storing the position of each feature in numpy arrays
 # word_index is only used in multi-file as it's important that features are always in the same order.
 # In single file it is created internally
class VariationalLDA(object):
    def __init__(self,corpus=None,K = 20,eta=0.1,
        alpha=1,update_alpha=True,word_index=None,normalise = -1,fixed_topics = None,fixed_topics_metadata = None,
        topic_index = None):
        self.corpus = corpus
        self.word_index = word_index
        self.normalise = normalise
        #  If the corpus exists, make the word index and the (unused?) word doc matrix
        if not self.corpus == None:
            self.n_docs = len(self.corpus)
            if self.word_index == None:
                self.word_index = self.find_unique_words()
            print "Object created with {} documents".format(self.n_docs)
            self.n_words = len(self.word_index)
            self.make_doc_index()
            if self.normalise > -1:
                print "Normalising intensities"
                self.normalise_intensities()
        
        self.K = K

        if fixed_topics:
            self.n_fixed_topics = len(fixed_topics)
            self.K += self.n_fixed_topics
        else:
            self.n_fixed_topics = 0


        self.alpha = alpha
        #  If alpha is a single value, make it into a vector
        if type(self.alpha) == int or type(self.alpha) == float:
            self.alpha = self.alpha*np.ones(self.K)
        self.eta = eta # Smoothing parameter for beta
        self.update_alpha = update_alpha
        self.doc_metadata = None
        

        # self.topic_index = topic_index
        # self.topic_metadata = topic_metadata
        self.topic_index = topic_index
        if not self.topic_index:
            self.topic_index = {}
            self.topic_metadata = {}
            topic_pos = 0
            if fixed_topics:
                for topic_name in fixed_topics:
                    self.topic_index[topic_name] = topic_pos
                    self.topic_metadata[topic_name] = fixed_topics_metadata[topic_name]
                    self.topic_metadata[topic_name]['type'] = 'fixed'
                    topic_pos += 1
        
            for topic_pos in range(self.n_fixed_topics,self.K):
                topic_name = 'motif_{}'.format(topic_pos)
                self.topic_index[topic_name] = topic_pos
                self.topic_metadata[topic_name] = {'name':topic_name,'type':'learnt'}

        if fixed_topics:
            self._add_exact_fixed_topics(fixed_topics)

    def _add_exact_fixed_topics(self,fixed_topics):
        # first add any missing words
        word_pos = max(self.word_index.values())+1

        for topic,spectrum in fixed_topics.items():
            for word in spectrum:
                if not word in self.word_index:
                    self.word_index[word] = word_pos
                    word_pos += 1
        self.n_words = len(self.word_index)

        # Now make the fixed rows of beta
        self.beta_matrix = np.zeros((self.K,self.n_words),np.float) + SMALL_NUMBER
        for topic,spectrum in fixed_topics.items():
            topic_pos = self.topic_index[topic]
            for word,intensity in spectrum.items():
                word_pos = self.word_index[word]
                self.beta_matrix[topic_pos,word_pos] = intensity
            self.beta_matrix[topic_pos,:] /= self.beta_matrix[topic_pos,:].sum()



    def add_fixed_topics_formulas(self,topics,prob_thresh = 0.5):
        # Adds fixed topics by matching on chemical formulas
        from formula import Formula
        print "Matching topics based on formulas"
        ti = [(topic,self.topic_index[topic]) for topic in self.topic_index]
        ti = sorted(ti,key = lambda x:x[1])
        topic_reverse,_ = zip(*ti)
        self.beta_matrix = np.zeros((self.K,len(self.word_index)),np.float)
        self.n_fixed_topics = 0

        frag_formulas = {}
        loss_formulas = {}

        for word in self.word_index:
            split_word = word.split('_')
            if len(split_word) == 3:
                formula = Formula(split_word[2])
                if word.startswith('loss'):
                    loss_formulas[str(formula)] = word
                else:
                    frag_formulas[str(formula)] = word


        for topic in topics['beta']:
            matched_probability = 0.0
            matches = {}
            for word,probability in topics['beta'][topic].items():
                split_word = word.split('_')
                if len(split_word) == 3: # it has a formula
                    formula_string = str(Formula(split_word[2]))
                    matched_word = None
                    if word.startswith('loss') and formula_string in loss_formulas:
                        matched_word = loss_formulas[formula_string]
                    elif word.startswith('fragment') and formula_string in frag_formulas:
                        matched_word = frag_formulas[formula_string]
                    if not matched_word == None:
                        matches[word] = matched_word
                        matched_probability += probability

            print "Topic: {}, {} probability matched ({})".format(topic,matched_probability,
                topics['topic_metadata'][topic].get('annotation',""))
            if matched_probability > prob_thresh:
                # We have a match
                for word in matches:
                    self.beta_matrix[self.n_fixed_topics,self.word_index[matches[word]]] = topics['beta'][topic][word]
                # Normalise
                self.beta_matrix[self.n_fixed_topics,:] /= self.beta_matrix[self.n_fixed_topics,:].sum()
                topic_here = topic_reverse[self.n_fixed_topics]
                print "Match accepted, storing as {}".format(topic_here)
                self.topic_metadata[topic_here]['type'] = 'fixed'
                for key,val in topics['topic_metadata'][topic].items():
                    self.topic_metadata[topic_here][key] = val
                self.n_fixed_topics += 1


    def add_fixed_topics(self,topics,topic_metadata = None,mass_tol = 5,prob_thresh = 0.5):
        print "Matching topics"
        ti = [(topic,self.topic_index[topic]) for topic in self.topic_index]
        ti = sorted(ti,key = lambda x:x[1])
        topic_reverse,_ = zip(*ti)
        self.beta_matrix = np.zeros((self.K,len(self.word_index)),np.float)
        self.n_fixed_topics = 0
        fragment_masses = np.array([float(f.split('_')[1]) for f in self.word_index if f.startswith('fragment')])
        fragment_names = [f for f in self.word_index if f.startswith('fragment')]
        loss_masses = np.array([float(f.split('_')[1]) for f in self.word_index if f.startswith('loss')])
        loss_names = [f for f in self.word_index if f.startswith('loss')]


        for topic in topics:
            print "Mass2Motif: {}".format(topic)
            topic_name_here = topic_reverse[self.n_fixed_topics]
            
            # self.n_fixed_topics = len(topics)

            temp_beta = np.zeros(len(self.word_index),np.float)
            probability_matched = 0.0
            
            for word in topics[topic]:
                word_mass = float(word.split('_')[1])
                if word.startswith('fragment'):
                    mass_err = 1e6*np.abs(fragment_masses - word_mass)/fragment_masses
                    min_err = mass_err.min()
                    if min_err < mass_tol:
                        matched_word = fragment_names[mass_err.argmin()]
                        temp_beta[self.word_index[matched_word]] = topics[topic][word]
                        probability_matched += topics[topic][word]
                        # print "\t Matched: {} with {}".format(word,matched_word)
                    else:
                        # print "\t Couldn't match {}".format(word)
                        pass
                else:
                    mass_err = 1e6*np.abs(loss_masses - word_mass)/loss_masses
                    min_err = mass_err.min()
                    if min_err < 2*mass_tol:
                        matched_word = loss_names[mass_err.argmin()]
                        temp_beta[self.word_index[matched_word]] = topics[topic][word]
                        probability_matched += topics[topic][word]
                        # print "\t Matched: {} with {}".format(word,matched_word)
                    else:
                        # print "\t Couldn't match {}".format(word)
                        pass
            print "\t matched {} of the probability".format(probability_matched)
            if probability_matched > prob_thresh:
                self.topic_metadata[topic_name_here]['type'] = 'fixed'
                self.beta_matrix[self.n_fixed_topics,:] = temp_beta
                # copy the metadata. If there is a name field in the incoming topic, save it as old_name
                if topic_metadata:
                    for metadata_item in topic_metadata[topic]:
                        if metadata_item == 'name':
                            self.topic_metadata[topic_name_here]['old_name'] = topic_metadata[topic][metadata_item]
                        else:
                            self.topic_metadata[topic_name_here][metadata_item] = topic_metadata[topic][metadata_item]
                self.n_fixed_topics += 1

        # Normalise
        self.beta_matrix[:self.n_fixed_topics,:] /= self.beta_matrix[:self.n_fixed_topics,:].sum(axis=1)[:,None]
        print "Matched {}/{} topics at prob_thresh={}".format(self.n_fixed_topics,len(topics),prob_thresh)

    def normalise_intensities(self):
        for doc in self.corpus:
            max_i = 0.0
            for word in self.corpus[doc]:
                if self.corpus[doc][word] > max_i:
                    max_i = self.corpus[doc][word]
            for word in self.corpus[doc]:
                self.corpus[doc][word] = int(self.normalise*self.corpus[doc][word]/max_i)

    # Load the features from a Joe .csv file. Pass the file name up until the _ms1.csv or _ms2.csv
    # these are added here
    # The scale factor is what we multiply intensities by
    def load_features_from_csv(self,prefix,scale_factor=100.0):
        # Load the MS1 peaks (MS1 object defined below)
        self.ms1peaks = []
        self.doc_metadata = {}
        ms1file = prefix + '_ms1.csv'
        with open(ms1file,'r') as f:
            heads = f.readline()
            for line in f:
                split_line = line.split(',')
                ms1_id = split_line[1]
                mz = float(split_line[5])
                rt = float(split_line[4])
                name = split_line[5] + '_' + split_line[4]
                intensity = float(split_line[6])
                new_ms1 = MS1(ms1_id,mz,rt,intensity,name)
                self.ms1peaks.append(name)
                self.doc_metadata[name] = {}
                self.doc_metadata[name]['parentmass'] = mz
                self.doc_metadata[name]['rt'] = rt
                self.doc_metadata[name]['intensity'] = intensity
                self.doc_metadata[name]['id'] = ms1_id
        print "Loaded {} MS1 peaks".format(len(self.ms1peaks))
        parent_id_list = [self.doc_metadata[name]['id'] for name in self.ms1peaks]

        # Load the ms2 objects
        frag_file = prefix + '_ms2.csv'
        features = []
        self.corpus = {}
        with open(frag_file,'r') as f:
            heads = f.readline().split(',')
            for line in f:
                split_line = line.rstrip().split(',')
                frag_name = split_line[10]
                if not frag_name == 'NA':
                    frag_name = frag_name[1:-1]
                frag_id = 'fragment_' + frag_name

                loss_name = split_line[11]
                if not loss_name == 'NA':
                    loss_name = loss_name[1:-1]
                loss_id = 'loss_' + loss_name

                if not frag_id == "fragment_NA":
                    if not frag_id in features:
                        features.append(frag_id)
                    frag_idx = features.index(frag_id)

                if not loss_id == "loss_NA":
                    if not loss_id in features:
                        features.append(loss_id)
                    loss_idx = features.index(loss_id)
                
                intensity = float(split_line[6])
                
                parent_id = split_line[2]
                # Find the parent
                parent = self.ms1peaks[parent_id_list.index(parent_id)]
                
                if parent == '156.076766819657_621.074':
                    print loss_id
                    print frag_id
                    print line
                
                # If we've not seen this parent before, create it as an empty dict
                if not parent in self.corpus:
                    self.corpus[parent] = {}
                
                # Store the ms2 features in the parent dictionary
                if not frag_id == "fragment_NA":
                    self.corpus[parent][frag_id] = intensity * scale_factor
                if not loss_id == "loss_NA":
                    self.corpus[parent][loss_id] = intensity * scale_factor

        self.n_docs = len(self.corpus)
        if self.word_index == None:
            self.word_index = self.find_unique_words()
        print "Object created with {} documents".format(self.n_docs)
        self.n_words = len(self.word_index)

        # I don't think this does anything - I will check
        self.make_doc_index()
        if self.normalise > -1:
            print "Normalising intensities"
            self.normalise_intensities()

    # Run the VB inference. Verbose = True means it gives output each iteration
    # initialise = True initialises (i.e. restarts the algorithm)
    # This means we can run the algorithm from where it got to.
    # First time its run, initialise has to be True
    def run_vb(self,n_its = 1,verbose=True,initialise=True):
        if initialise:
            print "Initialising"
            self.init_vb()
        print "Starting iterations"
        for it in range(n_its):
            start_time = time.clock()
            diff = self.vb_step()
            end_time = time.clock()
            self.its_performed += 1
            estimated_finish = ((end_time - start_time)*(n_its - it)/60.0)
            if verbose:
                print "Iteration {} (change = {}) ({} seconds, I think I'll finish in {} minutes). Alpha: ({},{})".format(it,diff,end_time - start_time,estimated_finish,self.alpha.min(),self.alpha.max())

    # D a VB step
    def vb_step(self):
        # Run an e-step
        temp_beta = self.e_step()
        temp_beta += self.eta
        # Do the normalisation in the m step
        if self.n_fixed_topics > 0:
            temp_beta[:self.n_fixed_topics,:] = self.beta_matrix[:self.n_fixed_topics,:]
        temp_beta /= temp_beta.sum(axis=1)[:,None]
        # Compute how much the word probabilities have changed
        total_difference = (np.abs(temp_beta - self.beta_matrix)).sum()
        self.beta_matrix = temp_beta
        # If we're updating alpha, run the alpha update
        if self.update_alpha:
            self.alpha = self.alpha_nr(init_alpha = self.alpha.copy())
        return total_difference
        # self.m_step()

    # Newton-Raphson procedure for updating alpha
    def alpha_nr(self,maxit=20,init_alpha=[]):
        old_alpha = self.alpha.copy()
        try:
            M,K = self.gamma_matrix.shape
            if not len(init_alpha) > 0:
                init_alpha = self.gamma_matrix.mean(axis=0)/K
            alpha = init_alpha.copy()
            alphap = init_alpha.copy()
            g_term = (psi(self.gamma_matrix) - psi(self.gamma_matrix.sum(axis=1))[:,None]).sum(axis=0)
            for it in range(maxit):
                grad = M *(psi(alpha.sum()) - psi(alpha)) + g_term
                H = -M*np.diag(pg(1,alpha)) + M*pg(1,alpha.sum())


                # playing here....
                z = M*pg(1,alpha.sum())
                h = -M*pg(1,alpha)
                c = ((grad/h).sum())/((1.0/z) + (1.0/h).sum())
                alpha_change = (grad - c)/h

                n_bad = (alpha_change > alpha).sum()
                while n_bad > 0:
                    alpha_change/=2.0
                    n_bad = (alpha_change > alpha).sum()

                
                alpha_new = alpha - alpha_change

                pos = np.where(alpha_new <= SMALL_NUMBER)[0]
                alpha_new[pos] = SMALL_NUMBER

                # if (alpha_new < 0).sum() > 0:
                #   init_alpha /= 10.0
                #   return self.alpha_nr(maxit=maxit,init_alpha = init_alpha)

                diff = np.sum(np.abs(alpha-alpha_new))
                alpha = alpha_new
                if diff < 1e-6 and it > 1:
                    return alpha
        except:
            alpha = old_alpha
        return alpha

    # TODO: tidy up and comment this function
    def e_step(self):
        temp_beta = np.zeros((self.K,self.n_words))
        for doc in self.corpus:
            d = self.doc_index[doc]
            temp_gamma = np.zeros(self.K) + self.alpha
            for word in self.corpus[doc]:
                w = self.word_index[word]
                log_phi_matrix = np.log(self.beta_matrix[:,w]) + psi(self.gamma_matrix[d,:]).T
                # self.phi_matrix[doc][word] = self.beta_matrix[:,w]*np.exp(psi(self.gamma_matrix[d,:])).T
                # for k in range(self.K):
                #   self.phi_matrix[doc][word][k] = self.beta_matrix[k,w]*np.exp(scipy.special.psi(self.gamma_matrix[d,k]))
                log_phi_matrix = np.exp(log_phi_matrix - log_phi_matrix.max())
                self.phi_matrix[doc][word] = log_phi_matrix/log_phi_matrix.sum()
                # self.phi_matrix[doc][word] /= self.phi_matrix[doc][word].sum()
                temp_gamma += self.phi_matrix[doc][word]*self.corpus[doc][word]
                temp_beta[:,w] += self.phi_matrix[doc][word] * self.corpus[doc][word]
            # self.phi_matrix[d,:,:] = (self.beta_matrix * self.word_matrix[d,:][None,:] * (np.exp(scipy.special.psi(self.gamma_matrix[d,:]))[:,None])).T
            # self.phi_matrix[d,:,:] /= self.phi_matrix[d,:,:].sum(axis=1)[:,None]
            # self.gamma_matrix[d,:] = self.alpha + self.phi_matrix[d,:,:].sum(axis=0)
            self.gamma_matrix[d,:] = temp_gamma
            pos = np.where(self.gamma_matrix[d,:]<SMALL_NUMBER)[0]
            self.gamma_matrix[d,pos] = SMALL_NUMBER
        return temp_beta

    # Function to find the unique words in the corpus and assign them to indices
    def find_unique_words(self):
        word_index = {}
        pos = 0
        for doc in self.corpus:
            for word in self.corpus[doc]:
                if not word in word_index:
                    word_index[word] = pos
                    pos += 1
        print "Found {} unique words".format(len(word_index))
        return word_index

    # Pretty sure this matrix is never used
    def make_doc_index(self):
        self.doc_index = {}
        doc_pos = 0
        for doc in self.corpus:
            self.doc_index[doc] = doc_pos
            doc_pos += 1

    # Initialise the VB algorithm
    # TODO: tidy this up
    def init_vb(self):
        # self.gamma_matrix = np.zeros((self.n_docs,self.K),np.float) + 1.0
        # self.phi_matrix = np.zeros((self.n_docs,self.n_words,self.K))
        self.its_performed = 0
        self.phi_matrix = {}
        self.gamma_matrix = np.zeros((self.n_docs,self.K))
        for doc in self.corpus:
            self.phi_matrix[doc] = {}
            for word in self.corpus[doc]:
                self.phi_matrix[doc][word] = np.zeros(self.K)
            d = self.doc_index[doc]
            doc_total = 0.0
            for word in self.corpus[doc]:
                doc_total += self.corpus[doc][word]
            self.gamma_matrix[d,:] = self.alpha + 1.0*doc_total/self.K
        # # Normalise this to sum to 1
        # self.phi_matrix /= self.phi_matrix.sum(axis=2)[:,:,None]

        # Initialise the betas
        if self.n_fixed_topics == 0:
            # self.beta_matrix = np.random.rand(self.K,self.n_words)
            self.beta_matrix = np.zeros((self.K,self.n_words),np.double)
            for k in range(self.K):
                self.beta_matrix[k,:] = np.random.dirichlet(self.eta*np.ones(self.n_words)) 
        else:
            for k in range(self.n_fixed_topics,self.K):
                self.beta_matrix[k,:] = np.random.dirichlet(self.eta*np.ones(self.n_words))
        self.beta_matrix /= self.beta_matrix.sum(axis=1)[:,None]

    # Function to return a dictionary with keys equal to documents and values equal to the probability
    # of the requested document (used for visusaling in DESI imaging)
    def get_topic_as_doc_dict(self,topic_id,thresh = 0.001,normalise=False):
        top = {}
        mat = self.gamma_matrix
        if normalise:
            mat = self.get_expect_theta()

        for doc in self.doc_index:
            pos = self.doc_index[doc]
            if mat[pos,topic_id] >= thresh:
                top[doc] = mat[pos,topic_id]
        return top

    # Return a topic as a dictionary over words
    def get_topic_as_dict(self,topic_id):
        top = {}
        for word in self.word_index:
            top[word] = self.beta_matrix[topic_id,self.word_index[word]]
        return top

    # Return the topic probabilities for all documents 
    # Note that self.doc_index maps the document names to their
    # position in this matrix
    def get_expect_theta(self):
        e_theta = self.gamma_matrix.copy()
        e_theta /= e_theta.sum(axis=1)[:,None]
        return e_theta

    def get_beta(self):
        return self.beta_matrix.copy()

    def make_dictionary(self,metadata=None,min_prob_to_keep_beta = 1e-3,
        min_prob_to_keep_phi = 1e-2,min_prob_to_keep_theta = 1e-2,
        filename = None,features = None,compute_overlaps = True):

        if metadata == None:
            if self.doc_metadata == None:
                metadata = {}
                for doc in self.corpus:
                    metadata[doc] = {'name': doc,'parentmass': float(doc.split('_')[0])}
            else:
                metadata = self.doc_metadata

        lda_dict = {}
        lda_dict['corpus'] = self.corpus
        lda_dict['word_index'] = self.word_index
        lda_dict['doc_index'] = self.doc_index
        lda_dict['K'] = self.K
        lda_dict['alpha'] = list(self.alpha)
        lda_dict['beta'] = {}
        lda_dict['doc_metadata'] = metadata
        lda_dict['topic_index'] = self.topic_index
        lda_dict['topic_metadata'] = self.topic_metadata
        
        pure_gamma = []
        for gamma in self.gamma_matrix:
            pure_gamma.append(list(gamma))

        lda_dict['gamma'] = gamma

        if features:
            lda_dict['features'] = features

        # Create the inverse indexes
        wi = []
        for i in self.word_index:
            wi.append((i,self.word_index[i]))
        wi = sorted(wi,key = lambda x: x[1])

        di = []
        for i in self.doc_index:
            di.append((i,self.doc_index[i]))
        di = sorted(di,key=lambda x: x[1])

        ri,i = zip(*wi)
        ri = list(ri)
        di,i = zip(*di)
        di = list(di)

        # make a reverse index for topics
        tp = [(topic,self.topic_index[topic]) for topic in self.topic_index]
        tp = sorted(tp,key = lambda x: x[1])
        reverse,_ = zip(*tp)

        for k in range(self.K):
            pos = np.where(self.beta_matrix[k,:]>min_prob_to_keep_beta)[0]
            motif_name = reverse[k]
            # motif_name = 'motif_{}'.format(k)
            lda_dict['beta'][motif_name] = {}
            for p in pos:
                word_name = ri[p]
                lda_dict['beta'][motif_name][word_name] = self.beta_matrix[k,p]

        eth = self.get_expect_theta()
        lda_dict['theta'] = {}
        for i,t in enumerate(eth):
            doc = di[i]
            lda_dict['theta'][doc] = {}
            pos = np.where(t > min_prob_to_keep_theta)[0]
            for p in pos:
                motif_name = reverse[p]
                # motif_name = 'motif_{}'.format(p)
                lda_dict['theta'][doc][motif_name] = t[p]

        lda_dict['phi'] = {}
        ndocs = 0
        for doc in self.corpus:
            ndocs += 1
            lda_dict['phi'][doc] = {}
            for word in self.corpus[doc]:
                lda_dict['phi'][doc][word] = {}
                pos = np.where(self.phi_matrix[doc][word] >= min_prob_to_keep_phi)[0]
                for p in pos:
                    motif_name = reverse[p]
                    lda_dict['phi'][doc][word][motif_name] = self.phi_matrix[doc][word][p]
            if ndocs % 500 == 0:
                print "Done {}".format(ndocs)

        if compute_overlaps:
            os = compute_overlap_scores(lda_dict)
            lda_dict['overlap_scores'] = os

        if not filename == None:
            with open(filename,'w') as f:
                pickle.dump(lda_dict,f)

        return lda_dict

# MS1 object used by Variational Bayes LDA
class MS1(object):
    def __init__(self,ms1_id,mz,rt,intensity,name):
        self.ms1_id = ms1_id
        self.mz = mz
        self.rt = rt
        self.intensity = intensity
        self.name = name
    def __str__(self):
        return self.name

# TODO: comment this class!
class MultiFileVariationalLDA(object):
    def __init__(self,corpus_dictionary,word_index,topic_index = None,topic_metadata = None,K = 20,alpha=1,eta = 0.1,update_alpha=True,normalise = 1000.0):
        self.word_index = word_index # this needs to be consistent across the instances
        self.corpus_dictionary = corpus_dictionary
        self.K = K
        self.alpha = alpha
        self.n_words = len(self.word_index)
        if type(self.alpha) == int:
            self.alpha = self.alpha*np.ones(self.K)
        self.eta = eta # Smoothing parameter for beta
        self.individual_lda = {}
        self.update_alpha = update_alpha        

        self.topic_index = topic_index
        if topic_index == None:
            self.topic_index = {}
            for topic_pos in range(self.K):
                self.topic_index['mass2motif_{}'.format(topic_pos)] = topic_pos
        self.topic_metadata = topic_metadata
        if self.topic_metadata == None:
            self.topic_metadata = {}
            for topic in self.topic_index:
                self.topic_metadata[topic] = {'name':topic,'type':'learnt'}

        for corpus_name in self.corpus_dictionary:
            new_lda = VariationalLDA(corpus=self.corpus_dictionary[corpus_name],K=K,
                alpha=alpha,eta=eta,word_index=word_index,
                topic_index = self.topic_index,
                topic_metadata = self.topic_metadata,
                update_alpha=self.update_alpha,
                normalise = normalise)
            self.individual_lda[corpus_name] = new_lda


    def run_vb(self,n_its = 10,initialise=True,parallel=False):
        if initialise:
            for lda_name in self.individual_lda:
                self.individual_lda[lda_name].init_vb()

        if parallel:
            num_cores = multiprocessing.cpu_count()
            print 'parallel=%s num_cores=%d' % (parallel, num_cores)
            pool = multiprocessing.Pool(num_cores)
        else:
            print 'serial processing'
        
        for it in range(n_its):

            print "Iteration: {}".format(it)
            temp_beta = np.zeros((self.K,self.n_words),np.float)
            total_difference = []
            
            if parallel:            

                # map each param_set for an individual lda to a worker that performs par_e_step()
                ldas = [self.individual_lda[lda_name] for lda_name in self.individual_lda]  
                params = []
                for l in ldas:
                    param_set = (l.corpus, l.K, l.n_words, l.doc_index, l.alpha, l.word_index, l.phi_matrix, l.beta_matrix, l.gamma_matrix)
                    params.append(param_set)
                par_results = pool.map(par_e_step, params)

                # process the results
                assert len(par_results) == len(ldas)
                for i in range(len(par_results)):
                    
                    beta_res, phi_res, gamma_res = par_results[i]
                    temp_beta += beta_res
                    ldas[i].phi_matrix = phi_res
                    ldas[i].gamma_matrix = gamma_res
                    
            else: # serial
                
                for lda_name in self.individual_lda:
                    temp_beta += self.individual_lda[lda_name].e_step()

            # cannot run this in parallel due to recursion .. ??
            # see http://stackoverflow.com/questions/7222570/parallel-recursive-function-in-python
            for lda_name in self.individual_lda:
                if self.individual_lda[lda_name].update_alpha:
                    self.individual_lda[lda_name].alpha = self.individual_lda[lda_name].alpha_nr()

            temp_beta += self.eta
            temp_beta /= temp_beta.sum(axis=1)[:,None]
            first_lda = self.individual_lda[self.individual_lda.keys()[0]]          
            total_difference = (np.abs(temp_beta - first_lda.beta_matrix)).sum()
            for lda_name in self.individual_lda:
                self.individual_lda[lda_name].beta_matrix = temp_beta
            print total_difference

    def make_dictionary(self,min_prob_to_keep_beta = 1e-3,
                        min_prob_to_keep_phi = 1e-2,min_prob_to_keep_theta = 1e-2,
                        filename = None):
        multifile_dict = {}
        multifile_dict['individual_lda'] = {}
        for lda_name in self.individual_lda:
            multifile_dict['individual_lda'][lda_name] = self.individual_lda[lda_name].make_dictionary(
                                                                    min_prob_to_keep_theta = min_prob_to_keep_theta,
                                                                    min_prob_to_keep_phi = min_prob_to_keep_phi,
                                                                    min_prob_to_keep_beta = min_prob_to_keep_beta)
        multifile_dict['word_index'] = self.word_index
        multifile_dict['K'] = self.K

        if filename:
            with open(filename,'w') as f:
                pickle.dump(multifile_dict,f)

        return multifile_dict

def make_split_dictionary(mflda,filename,postfix,features = None):
    # Makes a multifile LDA into several individual dictionary files
    multifile_dict = {}
    multifile_dict['individual_lda'] = []
    for lda_name in mflda.individual_lda:
        outname = lda_name + postfix
        multifile_dict['individual_lda'].append(outname)
        mflda.individual_lda[lda_name].make_dictionary(filename = outname + '.dict',features = features)
    multifile_dict['word_index'] = mflda.word_index
    multifile_dict['K'] = mflda.K
    with open(filename,'w') as f:
        pickle.dump(multifile_dict,f)


class SpectraSampler(object):
    def __init__(self,variational_lda):
        self.vlda = variational_lda
        self.compute_avg_word_count()
        print "Average {} words per document".format(self.mean_word_count)
        self.vocab_size = len(self.vlda.word_index)
        self.K = self.vlda.K
        self.compute_MS1_dist()

    def compute_MS1_dist(self):
        self.ms1_masses = []
        for doc in self.vlda.corpus:
            mass = float(doc.split('_')[0])
            self.ms1_masses.append(mass)
        
        self.ms1_mass_mean  = np.array(self.ms1_masses).mean()
        self.ms1_mass_var = np.array(self.ms1_masses).var()

    def compute_avg_word_count(self):
        self.wcounts = []
        for doc in self.vlda.corpus:
            new_count = 0
            for word in self.vlda.corpus[doc]:
                new_count += int(self.vlda.corpus[doc][word])
            self.wcounts.append(new_count)
        self.mean_word_count = int(np.array(self.wcounts).mean())

        temp = zip(self.vlda.word_index.keys(),self.vlda.word_index.values())
        temp = sorted(temp,key = lambda x: x[1])
        self.reverse_word_index,_ = zip(*temp)

    def generate_spectrum(self,n_words = None,include_losses = False):
        new_spectrum = {}
        beta_copy = self.vlda.beta_matrix.copy()
        if not include_losses:
            for word in self.vlda.word_index:
                if word.startswith('loss'):
                    pos = self.vlda.word_index[word]
                    beta_copy[:,pos] = 0
            beta_copy /= beta_copy.sum(axis=1)[:,None]
        if not n_words:
            # n_words = np.random.poisson(self.mean_word_count)
            n_words = self.wcounts[np.random.choice(len(self.vlda.corpus))]
            print "Generating {} words".format(n_words)
            theta = np.random.dirichlet(self.vlda.alpha)
            s_theta = zip(theta,['topic_{}'.format(i) for i in range(len(theta))])
            s_theta = sorted(s_theta,key = lambda x: x[0],reverse = True)
            print s_theta[:10]
            for word in range(n_words):
                # Select a topic
                topic = np.random.choice(self.K,p=theta)
                # Select a word
                word_pos = np.random.choice(self.vocab_size,p = self.vlda.beta_matrix[topic,:])
                word = self.reverse_word_index[word_pos]
                if not word in new_spectrum:
                    new_spectrum[word] = 1
                else:
                    new_spectrum[word] += 1
        return new_spectrum



def compute_overlap_scores(lda_dictionary):
    # Compute the overlap scores for the lda model in dictionary format
    
   
    overlap_scores = {}
    for doc,phi in lda_dictionary['phi'].items():
        motifs = lda_dictionary['theta'][doc].keys()
        doc_overlaps = {m : 0.0 for m in motifs}
        for word,probs in phi.items():
            for m in motifs:
                if word in lda_dictionary['beta'][m] and m in probs:
                    doc_overlaps[m] += lda_dictionary['beta'][m][word]*probs[m]
        overlap_scores[doc] = {}
        for m in doc_overlaps:
            overlap_scores[doc][m] = doc_overlaps[m]
    return overlap_scores
                 
def write_summary_file(lda_dictionary,filename):
    import csv
    with open(filename,'w') as f:
        writer = csv.writer(f)
        heads = ['clusterID','motif','probability','overlap']
        writer.writerow(heads)
        for doc,motifs in lda_dictionary['theta'].items():
            for motif,probability in motifs.items():
                row = [doc,motif,probability,lda_dictionary['overlap_scores'][doc].get(motif,0.0)]
                writer.writerow(row)
            
def write_topic_report(lda_dictionary,filename,backend = 'agg'):
    # import pylab as plt
    import matplotlib
    matplotlib.use(backend)
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    with PdfPages(filename) as pdf:

        topic_list = lda_dictionary['beta'].keys()
        # TODO fix motif order in report
        # topic_list = zip(topic_list,[int(t.split('_')[1]) for t in topic_list])
        # topic_list.sort(key = lambda x: x[1])
        # topic_list,_ = zip(*topic_list)
        for topic in topic_list:
            sys.stdout.write(topic + ' ')
            sys.stdout.flush()

            word_probs = lda_dictionary['beta'][topic]
            plt.figure(figsize=(20,10))
            for word,prob in word_probs.items():
                word_type,word_mz = word.split('_')
                word_mz = float(word_mz)
                if word_type == 'fragment':
                    plt.plot([word_mz,word_mz],[0,prob],'r')
                    if prob >= 0.025:
                        plt.text(word_mz,prob,'{:.0f}'.format(word_mz))
                if word_type == 'loss':
                    plt.plot([word_mz,word_mz],[0,-prob],'g')
                    if prob >= 0.025:
                        plt.text(word_mz,-prob-0.005,'{:.0f}'.format(word_mz))

            plt.plot(plt.xlim(),[0,0],'k--')
            plt.xlabel('m/z')
            plt.ylabel('probability')
            plt.title('{}'.format(topic))
            pdf.savefig()
            plt.close()

            # add some text
            textPage = plt.figure(figsize=(20,10))
            textPage.clf()
            topic_probs = zip(lda_dictionary['beta'][topic].keys(),lda_dictionary['beta'][topic].values())
            topic_probs.sort(key = lambda x: x[1],reverse = True)
            col = 0
            n_rows = 20
            textPage.text(0.3,0.9,"{}".format(topic),size = 24)
            for i,(word,prob) in enumerate(topic_probs):
                if prob < 0.005:
                    break
                rowpos = i%n_rows
                textPage.text(0.15+(col)*0.2,0.8-rowpos/40.0,"{:30s}: {:.2f}".format(word,prob),transform=textPage.transFigure, size=12)
                if rowpos == n_rows-1:
                    col += 1

            pdf.savefig()
            plt.close()

            
            

from Queue import PriorityQueue
import numpy as np
import pandas as pd
import scipy.sparse as ss
import math

class FeatureExtractor(object):

    def __init__(self, input_set, fragment_grouping_tol, loss_grouping_tol,
                 loss_threshold_min_val, loss_threshold_max_val):

        self.all_ms1 = []
        self.all_ms2 = []
        self.all_counts = []
        self.all_doc_labels = []
        self.vocab = []
        self.vocab_pos = {}
        self.fragment_grouping_tol = fragment_grouping_tol
        self.loss_grouping_tol = loss_grouping_tol
        self.loss_threshold_min_val = loss_threshold_min_val
        self.loss_threshold_max_val = loss_threshold_max_val

        # load all the ms1 and ms2 files
        self.F = len(input_set)
        for ms1_df, ms2_df in input_set:
            print "Loading MS1 dataframe %d X %d" % (ms1_df.shape)
            self.all_ms1.append(ms1_df)
            print "Loading MS2 dataframe %d X %d" % (ms2_df.shape)
            self.all_ms2.append(ms2_df)
        for ms1_df in self.all_ms1:
            ms1_df['peakID'] = ms1_df['peakID'].astype(int)
        for ms2_df in self.all_ms2:
            ms2_df['peakID'] = ms2_df['peakID'].astype(int)

        # build a position index of each ms1 and ms2 row's peakID and file
        self.ms1_pos = {}
        for f in range(self.F):
            ms1 = self.all_ms1[f]
            temp = self._position_index(ms1, f)
            self.ms1_pos.update(temp)

        # build a position index of each ms1 row's peakID and file
        self.ms2_pos = {}
        for f in range(self.F):
            ms2 = self.all_ms2[f]
            temp = self._position_index(ms2, f)
            self.ms2_pos.update(temp)

    def make_fragment_queue(self):
        q = PriorityQueue()
        for f in range(self.F):
            print "Processing fragments for file %d" % f
            ms2 = self.all_ms2[f]
            for _, row in ms2.iterrows():
                fragment_mz = row['mz']
                fragment_id = row['peakID']
                item = (fragment_mz, fragment_id, f, row)
                q.put(item)
        return q

    def make_loss_queue(self, mode='POS'):
        q = PriorityQueue()
        for f in range(self.F):
            print "Processing losses for file %d" % f
            ms1 = self.all_ms1[f]
            ms2 = self.all_ms2[f]
            for _, row in ms2.iterrows():

                key = (row['MSnParentPeakID'], f)
                pos = self.ms1_pos[key]
                parent_row = ms1.iloc[pos]
                row_mz = row['mz']
                row_id = row['peakID']
                parent_mz = parent_row['mz']
                loss_mz = np.abs(parent_mz - row_mz)

                item = (loss_mz, row_id, f, row)
                q.put(item)

        return q

    def _is_valid(self, current_mass, group):
        valid = True
        if current_mass < self.loss_threshold_min_val:
            valid = False
        if current_mass > self.loss_threshold_max_val:
            valid = False
        return valid

    def group_features(self, q, grouping_tol, check_threshold=False):

        groups = {}
        k = 0
        group = []
        while not q.empty():

            current_item = q.get()
            current_mass = current_item[0]
            current_file = current_item[2]
            current_row = current_item[3]
            item = (current_row, current_file, current_mass)
            group.append(item)

            # check if the next mass is outside tolerance
            if len(q.queue) > 0:
                head = q.queue[0]
                head_mass = head[0]
                _, upper = self._mass_range(current_mass, grouping_tol)
                if head_mass > upper:

                    if check_threshold:
                        if self._is_valid(current_mass, group):
                            groups[k] = group
                            k += 1
                    else: # nothing to check
                        groups[k] = group
                        k += 1
                    group = [] # whether valid or not, discard this group

            else: # no more item

                if check_threshold:
                    if self._is_valid(current_mass, group):
                        groups[k] = group
                else: # nothing to check
                    groups[k] = group

        K = len(groups)
        print "Total groups=%d" % K
        return groups

    def create_counts(self, fragment_groups, loss_groups):

        # initialise fragment vocab
        fragment_group_words = self._generate_words(fragment_groups, 'fragment')
        loss_group_words = self._generate_words(loss_groups, 'loss')
        self.vocab.extend(fragment_group_words.values())
        self.vocab.extend(loss_group_words.values())
        for n in range(len(self.vocab)):
            w = self.vocab[n]
            self.vocab_pos[w] = n

        # initialise the count dataframes for each file
        for f in range(self.F):
            df, doc_label = self._init_counts(f, self.vocab)
            self.all_counts.append(df)
            self.all_doc_labels.append(doc_label)

        # populate the dataframes
        print "Populating the counts"
        self._populate_counts(fragment_groups, fragment_group_words)
        self._populate_counts(loss_groups, loss_group_words)

    def get_entry(self, f):
        df = self.all_counts[f]
        vocab = self.vocab
        ms1 = self.all_ms1[f]
        ms2 = self.all_ms2[f]
        return df, vocab, ms1, ms2

    def _mass_range(self, mass_centre, mass_tol):
        interval = mass_centre * mass_tol * 1e-6
        mass_start = mass_centre - interval
        mass_end = mass_centre + interval
        return (mass_start, mass_end)

    def _position_index(self, df, f):
        peakid_pos = {}
        pos = 0
        for _, row in df.iterrows():
            key = (int(row['peakID']), f)
            peakid_pos[key] = pos
            pos += 1
        return peakid_pos

    def _get_doc_label(self, mz_val, rt_val):
        doc_label = '%s_%s' % (mz_val, rt_val)
        return doc_label

    def _print_group(self, group):
        print "%d members in the group" % len(group)
        for row, f, _ in group:
            this_parent_id = row['MSnParentPeakID']
            this_file_id = f
            this_peak_id = row['peakID']
            key = (this_file_id, this_parent_id, this_peak_id)
            print "- %d %d %d" % key

    def _generate_words(self, groups, prefix):
        group_words = {}
        for k in groups:
            group = groups[k]
            group_vals = []
            for _, _, val in group:
                group_vals.append(val)
            mean_mz = np.mean(np.array(group_vals))
            rounded_mz = np.round(mean_mz, 5)
            w = '%s_%s' % (prefix, rounded_mz)
            group_words[k] = w
        return group_words

    def _init_counts(self, f, vocab):

        # generate column labels
        doc_labels = []
        ms1 = self.all_ms1[f]
        mzs = ms1['mz'].values
        rts = ms1['rt'].values
        n_docs = len(ms1)
        for n in range(n_docs):
            doc_label = self._get_doc_label(mzs[n], rts[n])
            doc_labels.append(doc_label)

        # generate index
        row_labels = vocab

        # create the dictionary to hold the results
        lda_dict = {}
        for doc_name in doc_labels:
            lda_dict[doc_name] = {}

        return lda_dict, doc_labels

    def _populate_counts(self, groups, group_words):

        i = 0
        for k in groups:

            w = group_words[k]
            group = groups[k]
            for row, f, _ in group:

                lda_dict = self.all_counts[f]

                key = (row['MSnParentPeakID'], f)
                col_pos = self.ms1_pos[key]
                doc_id = self.all_doc_labels[f][col_pos]
                intensity = row['intensity']

                if w in lda_dict[doc_id]:
                    lda_dict[doc_id][w] += intensity
                else:
                    lda_dict[doc_id].update({w : intensity})
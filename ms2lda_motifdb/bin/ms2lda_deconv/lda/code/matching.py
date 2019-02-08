import math
import itertools
import copy
import csv
from collections import defaultdict

from Queue import PriorityQueue
from scipy.sparse import lil_matrix

class MatchFeature(object):

    def __init__(self, mz, rt, intensity, metadata):

        self.mz = mz
        self.intensity = intensity
        self.rt = rt
        self.matched = False
        self.metadata = metadata

    def __repr__(self):

        if self.rt is None:
            return "mz=%f, intensity=%f metadata=%s" % (self.mz, self.intensity, self.metadata)
        else:
            return "mz=%f, rt=%f, intensity=%f metadata=%s" % (self.mz, self.rt, self.intensity, self.metadata)

class SimpleMatching:

    def run(self, feature_list_1, feature_list_2, mz_tol, rt_tol):

        feature_list_1 = copy.deepcopy(feature_list_1)
        feature_list_2 = copy.deepcopy(feature_list_2)

        dist_mat = self.compute_scores(feature_list_1, feature_list_2, mz_tol, rt_tol)
        matches = self.approximate_match(feature_list_1, feature_list_2, dist_mat)

        # process matched features
        results = []
        for match in matches:
            for feature in match:
                feature.matched = True
        results.extend(matches)

        # process unmatched features
        unmatched_1 = filter(lambda x: not x.matched, feature_list_1)
        unmatched_2 = filter(lambda x: not x.matched, feature_list_2)
        for item in unmatched_1 + unmatched_2:
            results.append(set([item]))

        print '%d matched feature pairs' % len(matches)
        print '%d unmatched features from feature_list_1' % len(unmatched_1)
        print '%d unmatched features from feature_list_2' % len(unmatched_2)

        return results

    def compute_scores(self, feature_list_1, feature_list_2, mz_tol, rt_tol):

        print 'Computing scores'

        n_row = len(feature_list_1)
        n_col = len(feature_list_2)
        dist_mat = lil_matrix((n_row, n_col))

        # slow
        for i in range(len(feature_list_1)):
            f1 = feature_list_1[i]
            for j in range(len(feature_list_2)):
                f2 = feature_list_2[j]
                if self.is_within_tolerance(f1, f2, mz_tol, rt_tol):
                    dist_mat[i, j] = self.compute_dist(f1, f2, mz_tol, rt_tol)

        return dist_mat

    def is_within_tolerance(self, f1, f2, mz_tol, rt_tol):

        mz_lower, mz_upper = self.get_mass_range(f1.mz, mz_tol)
        rt_lower, rt_upper = self.get_rt_range(f1.rt, rt_tol)
        mz_ok = (mz_lower < f2.mz) and (f2.mz < mz_upper)
        rt_ok = (rt_lower < f2.rt) and (f2.rt < rt_upper)
        return mz_ok and rt_ok

    def get_mass_range(self, mz, mz_tol):

        interval = mz * mz_tol * 1e-6
        lower = mz - interval
        upper = mz + interval
        return lower, upper

    def get_rt_range(self, rt, rt_tol):

        lower = rt - rt_tol
        upper = rt + rt_tol
        return lower, upper

    def compute_dist(self, f1, f2, mz_tol, rt_tol):

        mz = f1.mz - f2.mz
        rt = f1.rt - f2.rt
        dist = math.sqrt((rt*rt)/(rt_tol*rt_tol) + (mz*mz)/(mz_tol*mz_tol))
        return dist

    def approximate_match(self, feature_list_1, feature_list_2, dist_mat):

        print 'Matching'
        dist_mat = dist_mat.tolil()
        matches = []

        q = self.make_queue(dist_mat)
        while not q.empty(): # while there are candidates to match

            # get the next candidate match with smallest distance
            pq_entry = q.get()
            priority = pq_entry[0]
            item = pq_entry[1]
            i = item[0]
            j = item[1]

            if dist_mat[i, j] != 0: # if they have not been matched

                # match the candidates together
                f1 = feature_list_1[i]
                f2 = feature_list_2[j]
                match = set([f1, f2])
                matches.append(match)

                # f1 and f2 cannot be matched anymore, so set row i and col j to 0
                dist_mat[i, :] = 0
                dist_mat[:, j] = 0

        return matches

    def make_queue(self, dist_arr):

        # make a queue of candidate matches ordered by distance (ascending)
        q = PriorityQueue()
        dist_arr = dist_arr.tocoo()
        for i, j, v in itertools.izip(dist_arr.row, dist_arr.col, dist_arr.data):
            dist = v
            item = (i, j)
            q.put((dist, item))
        return q

class MassOnlyMatching(SimpleMatching):

    def process(self, input_set, mz_tol):

        # first file is the reference
        ref_filename = input_set[0]
        ref_features = self.to_features(ref_filename)
        print 'Reference is %s (%d features)' % (ref_filename, len(ref_features))
        print

        # match all to the reference
        results = []
        for i in range(1, len(input_set)):
            filename = input_set[i]
            other_features = self.to_features(filename)
            print 'Processing %s (%d features)' % (filename, len(other_features))
            res = self.run(ref_features, other_features, mz_tol, None)
            results.append(res)
            print

        # collect aligned peaksets across individual results by the reference m/z value
        combined = defaultdict(set)
        for res in results:
            for row in res:
                if len(row) > 1:
                    f = self.get_ref_feature(row, ref_filename)
                    combined[f.mz].update(row)

        # turn aligned peaksets into a list of tuples
        final = []
        for ref_mz in combined:
            row = combined[ref_mz]
            new_row = set()
            for f in row:
                new_row.add((f.mz, f.intensity, f.metadata['filename']))
            final.append(list(new_row))

        return final

    def to_features(self, filename):

        feature_list = []
        with open(filename, 'rb') as f:

            reader = csv.reader(f)
            peak_list = list(reader)

            for mz, intensity in peak_list:
                mz = float(mz)
                intensity = float(intensity)
                metadata = {'filename': filename}
                f = MatchFeature(mz, None, intensity, metadata)
                feature_list.append(f)

        return feature_list

    def get_ref_feature(self, aligned, ref_filename):
        for f in aligned:
            if f.metadata['filename'] == ref_filename:
                return f

    def is_within_tolerance(self, f1, f2, mz_tol, rt_tol):

        mz_lower, mz_upper = self.get_mass_range(f1.mz, mz_tol)
        mz_ok = (mz_lower < f2.mz) and (f2.mz < mz_upper)
        return mz_ok

    def compute_dist(self, f1, f2, mz_tol, rt_tol):

        mz = f1.mz - f2.mz
        dist = math.sqrt((mz*mz)/(mz_tol*mz_tol))
        return dist
import numpy as np
import sys
import os
import csv
import argparse
import json
import pandas as pd
import requests
import redis

# try:
#     redis_connection = redis.Redis(host='dorresteinappshub.ucsd.edu', port=6378, db=0)
# except:
#     redis_connection = None
redis_connection = None


def acquire_motifdb(db_list):
    db_list_key = json.dumps(db_list)
    if redis_connection is not None:
        if redis_connection.exists(db_list_key):
            cached_data = json.loads(redis_connection.get(db_list_key))
            return cached_data["motifdb_spectra"], cached_data["motifdb_metadata"], set(cached_data["motifdb_features"])

    # no longer needed as CSRF protection has been disabled for get_motifset()
    # client = requests.session()
    # token_output = client.get(server_url + 'initialise_api/').json()
    # token = token_output['token']
    # data = {'csrfmiddlewaretoken':token}

    data = {}
    data['motifset_id_list'] = db_list
    data['filter'] = 'True'

    try:
        output = requests.post(server_url + 'get_motifset/',data = data, verify=False).json()
        motifdb_spectra = output['motifs']
        motifdb_metadata = output['metadata']
        motifdb_features = set()
        for m,spec in motifdb_spectra.items():
            for f in spec:
                motifdb_features.add(f)
    except:
        motifdb_spectra = {}
        motifdb_metadata = {}
        motifdb_features = set()

    #Trying to cache
    if redis_connection is not None:
        data_cache = {}
        data_cache["motifdb_spectra"] = motifdb_spectra
        data_cache["motifdb_metadata"] = motifdb_metadata
        data_cache["motifdb_features"] = list(motifdb_features)

        redis_connection.set(db_list_key, json.dumps(data_cache))

    return motifdb_spectra, motifdb_metadata, motifdb_features

# Put this here as its now the only thing you need from the motifdb codebase
class FeatureMatcher(object):
    def __init__(self,db_features,other_features,bin_width=0.005):
        self.db_features = db_features
        self.other_features = other_features
        self.fmap = {}
        self.bin_width = bin_width
        self.augmented_features = {f:v for f,v in other_features.items()}

        self.match()
        self.match(ftype='loss')



    def match(self,ftype='fragment'):
        import bisect
        other_names = [f for f in self.other_features if f.startswith(ftype)]
        other_min_mz = [self.other_features[f][0] for f in self.other_features if f.startswith(ftype)]
        other_max_mz = [self.other_features[f][1] for f in self.other_features if f.startswith(ftype)]

        temp = zip(other_names,other_min_mz,other_max_mz)
        temp.sort(key = lambda x: x[1])
        other_names,other_min_mz,other_max_mz = zip(*temp)
        other_names = list(other_names)
        other_min_mz = list(other_min_mz)
        other_max_mz = list(other_max_mz)

        exact_match = 0
        new_ones = 0
        overlap_match = 0
        for f in [f for f in self.db_features if f.startswith(ftype)]:
            if f in other_names:
                self.fmap[f] = f;
                exact_match += 1
            else:
                fmz = float(f.split('_')[1])
                if fmz < other_min_mz[0] or fmz > other_max_mz[-1]:
                    self.fmap[f] = f
                    self.augmented_features[f] = (fmz-self.bin_width/2,fmz+self.bin_width/2)
                    new_ones += 1
                    continue
                fpos = bisect.bisect_right(other_min_mz,fmz)
                fpos -= 1
                if fmz <= other_max_mz[fpos]:
                    self.fmap[f] = other_names[fpos]
                    overlap_match += 1
                else:
                    self.fmap[f] = f
                    self.augmented_features[f] = (fmz-self.bin_width/2,fmz+self.bin_width/2)
                    new_ones += 1
        print "Finished matching ({}). {} exact matches, {} overlap matches, {} new features".format(ftype,exact_match,overlap_match,new_ones)

    def convert(self,dbspectra):
        for doc,spec in dbspectra.items():
            newspec = {}
            for f,i in spec.items():
                newspec[self.fmap[f]] = i
            dbspectra[doc] = newspec
        return dbspectra


#Outputting datastructures for GNPS to write out
def get_motifs_in_scans(lda_dictionary,metadata,overlap_thresh=0.3,p_thresh=0.1,X=5,motif_metadata = {}):
    # write a nodes file
    all_motifs = lda_dictionary['beta'].keys()
    all_docs = lda_dictionary['theta'].keys()

    doc_to_motif = {}
    for d in lda_dictionary['theta']:
        for m,p in lda_dictionary['theta'][d].items():
            if p >= p_thresh and lda_dictionary['overlap_scores'][d].get(m,0.0) >= overlap_thresh:
                if not d in doc_to_motif:
                    doc_to_motif[d] = set()
                doc_to_motif[d].add(m)

    #This list includes a list of motifs found in all scans and metadata associated with each motif
    motifs_in_scans = []

    for doc in all_docs:
        try:
            motifs = list(doc_to_motif[doc])
        except:
            motifs = []

        for m in motifs:
            motif_dict = {}
            motif_dict["scan"] = doc
            motif_dict["precursor.mass"] = metadata[doc]['precursormass']
            try:
                motif_dict["retention.time"] = metadata[doc]['parentrt']
            except:
                motif_dict["retention.time"] = "0.0"
            motif_dict["motif"] = m
            motif_dict["probability"] = lda_dictionary['theta'][doc][m]
            motif_dict["overlap"] = lda_dictionary['overlap_scores'][doc][m]

            try:
                md = motif_metadata.get(m,None)
                link_url = md.get('motifdb_url',None)
                annotation = md.get('annotation',None)

                motif_dict["motifdb_url"] = link_url.encode('utf8')
                motif_dict["motifdb_annotation"] = annotation.encode('utf8')
            except:
                motif_dict["motifdb_url"] = ""
                motif_dict["motifdb_annotation"] = ""

            motifs_in_scans.append(motif_dict)

    return motifs_in_scans


"""Parsing Args"""

parser = argparse.ArgumentParser(description='Creates MS2LDA')
parser.add_argument('input_format', help='input_format')
parser.add_argument('input_iterations', type=int, help='input_iterations')
parser.add_argument('input_minimum_ms2_intensity', type=float, help='input_minimum_ms2_intensity')
parser.add_argument('input_free_motifs', type=int, help='input_free_motifs')
parser.add_argument('input_bin_width', type=float, help='input_bin_width')
parser.add_argument('input_network_overlap', type=float, help='input_network_overlap')
parser.add_argument('input_network_pvalue', type=float, help='input_network_pvalue')
parser.add_argument('input_network_topx', type=int, help='input_network_topx')

parser.add_argument('gnps_motif_include', help='gnps_motif_include')
parser.add_argument('massbank_motif_include', help='massbank_motif_include')
parser.add_argument('urine_motif_include', help='urine_motif_include')
parser.add_argument('euphorbia_motif_include', help='euphorbia_motif_include')
parser.add_argument('rhamnaceae_motif_include', help='rhamnaceae_motif_include')
parser.add_argument('strep_salin_motif_include', help='strep_salin_motif_include')
parser.add_argument('photorhabdus_motif_include', help='photorhabdus_motif_include')
parser.add_argument('user_motif_sets', help='user_motif_sets')

parser.add_argument('input_mgf_file', help='input_mgf_file')
parser.add_argument('input_pairs_file', help='input_pairs_file')
parser.add_argument('input_mzmine2_folder', help='input_mzmine2_folder')
parser.add_argument('output_prefix', help='output_prefix')

args = parser.parse_args()


"""Grabbing the latest Motifs from MS2LDA"""
import requests
server_url = 'https://ms2lda.org/motifdb/'
# motifset_dict = requests.get(server_url+'list_motifsets/', verify=False).json()
# db_list = ['gnps_binned_005']  # Can update this later with multiple motif sets
db_list = []

if args.gnps_motif_include == "yes":
    db_list.append(2)
if args.massbank_motif_include == "yes":
    db_list.append(4)
if args.urine_motif_include == "yes":
    db_list.append(1)
if args.euphorbia_motif_include == "yes":
    db_list.append(3)
if args.rhamnaceae_motif_include == "yes":
    db_list.append(5)
if args.strep_salin_motif_include == "yes":
    db_list.append(6)
if args.photorhabdus_motif_include == "yes":
    db_list.append(16)

if not ("None" in args.user_motif_sets):
    try:
        db_list += [int(motif_db_id) for motif_db_id in args.user_motif_sets.split(",")]
    except:
        print("User motif set improperly formatted. Please have numbers separated by commas or enter None")
        exit(1)

db_list = list(set(db_list))

# Acquire motifset from MS2LDA.org
motifdb_spectra, motifdb_metadata, motifdb_features = acquire_motifdb(db_list)


"""Parsing the input files"""

# following should be mscluster or mzmine
input_format = args.input_format
input_iterations = args.input_iterations
input_minimum_ms2_intensity = args.input_minimum_ms2_intensity
input_free_motifs = args.input_free_motifs
input_bin_width = args.input_bin_width

# mgf file name
input_mgf_file = args.input_mgf_file

# pairs file name
pairs_file = args.input_pairs_file

# output prefix
output_prefix = args.output_prefix

if os.path.isdir(output_prefix):
    output_prefix = os.path.join(output_prefix, "output")

print(input_format, input_mgf_file)

ldacodepath = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'lda/code')

sys.path.append(ldacodepath)

from ms2lda_feature_extraction import LoadMGF, MakeBinnedFeatures

# Assuming only one mgf file...
name_field = "scans"

if input_format == 'mscluster':
    csv_id_field = None
    mgf_id_field = None
    input_csv_file = None

    l = LoadMGF(name_field=name_field,min_ms2_intensity=input_minimum_ms2_intensity)
elif input_format == 'mzmine':
    mzmine_path = args.input_mzmine2_folder
    if os.path.isdir(mzmine_path):
        all_files = [f for f in os.listdir(mzmine_path) if os.path.isfile(os.path.join(mzmine_path, f))]
        if len(all_files) != 1:
            print("Requires exactly one quantification file")
            exit(1)
        input_csv_file = os.path.join(mzmine_path, all_files[0])
    else:
        input_csv_file = mzmine_path


    csv_id_col = 'row ID'
    mgf_id_field = 'scans'
    l = LoadMGF(name_field=name_field, \
                peaklist=input_csv_file, \
                csv_id_col=csv_id_col, \
                id_field=mgf_id_field, \
                min_ms2_intensity=input_minimum_ms2_intensity, \
                mz_col_name='row m/z', \
                rt_col_name='row retention time')

ms1, ms2, metadata = l.load_spectra([input_mgf_file])
print "Loaded {} spectra".format(len(ms1))

m = MakeBinnedFeatures(bin_width=input_bin_width)  #What value do you want here?? TODO: Parameterize
corpus, features = m.make_features(ms2)
corpus = corpus[corpus.keys()[0]]

# from motifdb_loader import FeatureMatcher
fm = FeatureMatcher(motifdb_features, features)
motifdb_spectra = fm.convert(motifdb_spectra)


# Add the motifdb features to avoid problems when loading the dict into vlda later
bin_width = m.bin_width
added = 0
for f in motifdb_features:
    if not f in features:
        word_mz = float(f.split('_')[1])
        word_mz_min = word_mz - bin_width / 2
        word_mz_max = word_mz + bin_width / 2
        features[f] = (word_mz_min, word_mz_max)
        added += 1

print "Added {} features".format(added)

from lda import VariationalLDA

#K = 300  # number of *new* topics
K = input_free_motifs  # number of *new* topics

vlda = VariationalLDA(corpus, K=K, normalise=1000.0,
                      fixed_topics=motifdb_spectra,
                      fixed_topics_metadata=motifdb_metadata)

# note that for real runs the number of iterations is recommended to be 1000 or higher
vlda.run_vb(initialise=True, n_its=input_iterations)

vd = vlda.make_dictionary(
    features=features, metadata=metadata, filename=output_prefix + '.dict')

from ms2lda_molnet_integration import write_output_files
write_output_files(vd, pairs_file, output_prefix, metadata,
                   overlap_thresh=args.input_network_overlap, p_thresh=args.input_network_pvalue,
                   X=args.input_network_topx, motif_metadata = motifdb_metadata)

# Writing the report - ntoe that you might need to set the 'backend' argument
# for this method to work (see the method in lda.py) as it depends what on
# your system will render the pdf...
from lda import write_topic_report
try:
    write_topic_report(vd,output_prefix+'_topic_report.pdf')
except:
    print("PDF Generation Failed")


### Writing additional output, creates a list of all motifs found in data, one motif per row and MS/MS Scan
all_motifs_in_scans = get_motifs_in_scans(vd, metadata,
                                            overlap_thresh=args.input_network_overlap, p_thresh=args.input_network_pvalue,
                                            X=args.input_network_topx, motif_metadata = motifdb_metadata)


# Outputting motif list, one by line
fieldnames = ['scan', 'precursor.mass',
                  'retention.time',
                  "motif",
                  "probability",
                  "overlap",
                  "motifdb_url",
                  "motifdb_annotation"]
output_motifs_scans_filename = output_prefix + "_motifs_in_scans.tsv"
motif_list_df = pd.DataFrame(all_motifs_in_scans)
motif_list_df = motif_list_df[fieldnames]
motif_list_df.to_csv(output_motifs_scans_filename, sep="\t", index=False)

# Reformatting the list of cluster summary
# TODO


sys.exit(0)


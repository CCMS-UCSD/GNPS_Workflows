from chemClass2Network import *
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('GNPS', help='enter your GNPS job ID')
parser.add_argument('--nap', default="None", help='enter your nap ID')
parser.add_argument('--dereplicator', default="None", help='enter your dereplicator ID')
parser.add_argument('--varquest', default="None", help='enter your varquest ID')
parser.add_argument('--ms2lda_job', default="None", help='enter your MS2LDA.org ID')
parser.add_argument('--gnps_ms2lda_job', default="None", help='enter your MS2LDA at GNPS job ID')

parser.add_argument('output_directory', help='enter your directory for generated output files')

args = parser.parse_args()
nap_ID = args.nap
GNPS_job_ID = args.GNPS
directory = args.output_directory

'''
nap_ID = 'c4bb6b8be9e14bdebe87c6ef3abe11f6'
GNPS_job_ID = 'b817262cb6114e7295fee4f73b22a3ad'
Varquest_job_ID = '4d971b8162644e869a68faa35f01b915'
Derep_job_ID = 'c62d3283752f4f98b1720d0a6d1ee65b'
MS2LDA_job_ID = '907'
'''
create_Folder(directory=directory)
GNPS_file = request_GNPS_file(GNPS_job_ID, directory) + '/'

gnpslibfile, netfile = process_GNPS_file(GNPS_file)
SMILES_csv, out_dict = add_Chemical_Info(gnpslibfile, directory, nap_ID=args.nap, Derep_job_ID=args.dereplicator, Varquest_job_ID=args.varquest)

print("Calculating InCHI Keys")
InchiKeys_lst, InchiKeys, inchi_dic, SMILES_failed = convert_SMILES_InchiKeys(SMILES_csv, out_dict, directory)
print("Getting classifiations")
get_Classy(InchiKeys, directory)

#Creating a network with classyfire information
final, ClassyFireResults_file = create_ClassyFireResults(netfile, inchi_dic, directory)
create_GraphML(GNPS_file, final, directory)

#Creating a network from the molecular networking along with mass2motif
mass_2_Motifs(GNPS_file, ClassyFireResults_file, directory, MS2LDA_job_ID=args.ms2lda_job, GNPS_MS2LDA_job_ID=args.gnps_ms2lda_job)

print('operations completed')
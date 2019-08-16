from chemClass2Network import *
import argparse
import os

parser = argparse.ArgumentParser()

parser.add_argument('GNPS', help='enter your GNPS job ID')
parser.add_argument('directory', help='enter your directory for generated output files')
parser.add_argument('--nap', help='enter your nap ID')
parser.add_argument('--varquest', help='enter your Varquest job ID', action='store')
parser.add_argument('--derep', help='enter your Dereplicator job ID', action='store')
parser.add_argument('--ms2lda', help='enter your MS2LDA job ID', action='store', type=str)
parser.add_argument('--prob', 
                    help='minimal probability score for a Mass2Motif to be included. Default is 0.01', 
                    action='store', 
                    type=float)
parser.add_argument('--overlap', 
                    help='minimal overlap score for a Mass2Motif to be included. Default is 0.3.', 
                    action='store', 
                    type=float)
parser.add_argument('--top', 
                    help='specifies how many most shared motifs per molecular family should be shown. Default is 5.', 
                    action='store', 
                    type=int)
args = parser.parse_args()
nap_ID = args.nap
GNPS_job_ID = args.GNPS
directory = args.directory

create_Folder(directory=directory)
GNPS_file = request_GNPS_file(GNPS_job_ID, directory) + '/'

#optional varquest and dereplicator jobs for classical 
if args.varquest:
    Varquest_file = request_Varquest_file(args.varquest, directory) + '/'
if args.derep:
    Derep_file = request_Derep_file(args.derep, directory) + '/'

gnpslibfile, netfile = process_GNPS_file(GNPS_file)
if args.varquest and args.derep:
    SMILES_csv, out_dict = add_Chemical_Info(gnpslibfile, nap_ID, directory, 
                                            Derep_job_ID=args.derep, 
                                            Varquest_job_ID=args.varquest, 
                                            derepfile=Derep_file, 
                                            varquestfile=Varquest_file)
else:
    SMILES_csv, out_dict = add_Chemical_Info(gnpslibfile, nap_ID, directory)
InchiKeys_lst, InchiKeys, inchi_dic, SMILES_failed = convert_SMILES_InchiKeys(SMILES_csv, out_dict, directory)
get_Classy(InchiKeys, directory)
final, ClassyFireResults_file = create_ClassyFireResults(netfile, inchi_dic, directory)
create_GraphML(GNPS_file, final, directory)

#optional MS2LDA job Mass 2 Motifs
if args.prob or args.overlap or args.top:
    user_Params = pack_User_Params(args.prob, args.overlap, args.top)
if args.ms2lda and user_Params:
    MS2LDA_job_ID = args.ms2lda
    mass_2_Motifs(GNPS_file, MS2LDA_job_ID, ClassyFireResults_file, directory, user_Params)
else:
    MS2LDA_job_ID = args.ms2lda
    mass_2_Motifs(GNPS_file, MS2LDA_job_ID, ClassyFireResults_file, directory)
    
print('operations completed')
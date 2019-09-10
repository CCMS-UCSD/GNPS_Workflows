from chemClass2Network import *
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('GNPS', help='enter your GNPS job ID')
parser.add_argument('--nap', default='None', help='enter your nap ID')
parser.add_argument('--varquest', default='None', help='enter your Varquest job ID')
parser.add_argument('--derep', default='None', help='enter your Dereplicator job ID')
parser.add_argument('--ms2lda', default='None', help='enter your MS2LDA job ID')
parser.add_argument('--gnps_ms2lda_job', default='None', help='enter your MS2LDA at GNPS job ID')
parser.add_argument('--prob', 
                    default=0.01,
                    help='minimal probability score for a Mass2Motif to be included. Default is 0.01', 
                    action='store', 
                    type=float)
parser.add_argument('--overlap', 
                    default=0.3,
                    help='minimal overlap score for a Mass2Motif to be included. Default is 0.3.', 
                    action='store', 
                    type=float)
parser.add_argument('--top', 
                    default=5,
                    help='specifies how many most shared motifs per molecular family should be shown. Default is 5.', 
                    action='store', 
                    type=int)

parser.add_argument('output_directory', help='enter your directory for generated output files')

args = parser.parse_args()
GNPS_job_ID = args.GNPS
directory = args.output_directory

create_Folder(directory=directory)
GNPS_file = request_GNPS_file(GNPS_job_ID, directory) + '/'

#request Varquest and Derep files if specified
if args.varquest!='None' and args.varquest!=None:
    Varquest_file = request_Varquest_file(args.varquest, directory) + '/'
elif args.varquest=='None' or args.varquest==None:
    Varquest_file = None

if args.derep!='None' and args.derep!=None:
    Derep_file = request_Derep_file(args.derep, directory) + '/'
elif args.derep=='None' or args.derep==None:
    Derep_file = None

gnpslibfile, netfile = process_GNPS_file(GNPS_file)
SMILES_csv, out_dict = add_Chemical_Info(gnpslibfile, directory, nap_ID=args.nap, Derep_job_ID=args.derep, Varquest_job_ID=args.varquest, derepfile=Derep_file, varquestfile=Varquest_file)

print('Calculating InCHI Keys')
InchiKeys_lst, InchiKeys, inchi_dic, SMILES_failed = convert_SMILES_InchiKeys(SMILES_csv, out_dict, directory)
print('Getting classifications')
get_Classy(InchiKeys, directory)

#Creating a network with classyfire information
final, ClassyFireResults_file = create_ClassyFireResults(netfile, inchi_dic, directory)
create_GraphML(GNPS_file, final, directory)

#optional MS2LDA job Mass 2 Motifs
if args.ms2lda!='None' and args.ms2lda!=None:
    user_Params = pack_User_Params(prob=args.prob, overlap=args.overlap, top=args.top)
    MS2LDA_job_ID = args.ms2lda
    mass_2_Motifs(GNPS_file, MS2LDA_job_ID, ClassyFireResults_file, directory, user_Params)
elif args.gnps_ms2lda_job!='None' and args.gnps_ms2lda_job!=None:
    print('Load from GNPS')
else:
    print('No Op')
    
print('operations completed')
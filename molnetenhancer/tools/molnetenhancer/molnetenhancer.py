from chemClass2Network import *
import argparse
import os

def main():
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

    process(args.GNPS, args.output_directory, varquest_job_id=args.varquest, \
        dereplicator_job_id=args.derep, ms2lda_job_id=args.ms2lda, \
        ms2lda_gnps_job_id=args.gnps_ms2lda_job, nap_job_id=args.nap)

def process(GNPS_job_ID, output_directory, varquest_job_id=None, dereplicator_job_id=None, ms2lda_job_id=None, ms2lda_gnps_job_id=None, nap_job_id=None, ms2lda_prob=0.01, ms2lda_overlap=0.3, ms2lda_top=5):
    '''
    nap_ID = 'c4bb6b8be9e14bdebe87c6ef3abe11f6'
    GNPS_job_ID = 'b817262cb6114e7295fee4f73b22a3ad'
    Varquest_job_ID = '4d971b8162644e869a68faa35f01b915'
    Derep_job_ID = 'c62d3283752f4f98b1720d0a6d1ee65b'
    MS2LDA_job_ID = '907'
    '''
    create_Folder(directory=output_directory)
    GNPS_file = request_GNPS_file(GNPS_job_ID, output_directory) + '/'

    gnpslibfile, netfile = process_GNPS_file(GNPS_file)
    SMILES_csv, out_dict = add_Chemical_Info(gnpslibfile, output_directory, nap_ID=nap_job_id, Derep_job_ID=dereplicator_job_id, Varquest_job_ID=varquest_job_id)

    print('Calculating InCHI Keys')
    InchiKeys_lst, InchiKeys, inchi_dic, SMILES_failed = convert_SMILES_InchiKeys(SMILES_csv, out_dict, output_directory)
    print('Getting classifications')
    get_Classy(InchiKeys, output_directory)

    #Creating a network with classyfire information
    final, ClassyFireResults_file = create_ClassyFireResults(netfile, inchi_dic, output_directory)
    create_GraphML(GNPS_file, final, output_directory)


    #optional MS2LDA job Mass 2 Motifs
    if ms2lda_job_id!='None' and ms2lda_job_id!=None and len(ms2lda_job_id) > 2 and len(ms2lda_job_id) < 20:
        user_Params = pack_User_Params(prob=ms2lda_prob, overlap=ms2lda_overlap, top=ms2lda_top)
        MS2LDA_job_ID = ms2lda_job_id
        mass_2_Motifs(GNPS_file, MS2LDA_job_ID, ClassyFireResults_file, output_directory, user_Params)
    elif ms2lda_gnps_job_id!='None' and ms2lda_gnps_job_id!=None:
        print("MS2LDA from GNPS is currently not supported but is coming soon!")
        exit(1)
    else:
        print('No MS2LDA Op')
        
    print('operations completed')

if __name__=="__main__":
    main()

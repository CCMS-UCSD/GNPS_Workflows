from pyMolNetEnhancer import *
import pandas as pd
import os
import csv 
import json
import networkx as nx
from pathlib import Path

infer_numeric_types = True

def create_Folder(directory='Output Files'):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)
    #return directory

#cURL requested GNPS file based on the user-defined GNPS job ID
def request_GNPS_file(GNPS_job_ID, directory):
    import requests
    from io import BytesIO
    from zipfile import ZipFile

    GNPS_job_ID = GNPS_job_ID
    result = requests.post("https://gnps.ucsd.edu/ProteoSAFe/DownloadResult?task=%s&view=download_cytoscape_data" % GNPS_job_ID) 
    print('GNPS request success: ' + str(result.ok))
    zf = ZipFile(BytesIO(result.content))
    folder_name = directory + '/GNPS_output_graphML'
    zf.extractall(folder_name)
    zf.close()
    return folder_name; #returns the folder name of the GNPS_output_graphML folder (str)

#cURL requested Varquest file based on the user-defined Varquest job ID
def request_Varquest_file(Varquest_job_ID, directory):
    import requests
    from io import BytesIO
    from zipfile import ZipFile

    Varquest_job_ID = Varquest_job_ID
    result = requests.post("https://gnps.ucsd.edu/ProteoSAFe/DownloadResult?task=%s&view=view_significant" % Varquest_job_ID) 
    print('Varquest request success: ' + str(result.ok))
    zf = ZipFile(BytesIO(result.content))
    folder_name = directory + '/Varquest_output'
    zf.extractall(folder_name)
    zf.close()
    return folder_name; #returns the folder name of the Varquest_output folder (str)

#cURL requested Dereplicator file based on the user-defined Dereplicator job ID
def request_Derep_file(Derep_job_ID, directory):
    import requests
    from io import BytesIO
    from zipfile import ZipFile

    Derep_job_ID = Derep_job_ID
    result = requests.post("https://gnps.ucsd.edu/ProteoSAFe/DownloadResult?task=%s&view=view_significant" % Derep_job_ID) 
    print('Dereplicator request success: ' + str(result.ok))
    zf = ZipFile(BytesIO(result.content))
    folder_name = directory + '/Derep_output'
    zf.extractall(folder_name)
    zf.close()
    return folder_name; #returns the folder name of the Derep_output folder (str)

#proces GNPS file
def process_GNPS_file(GNPS_file):
    if 'clusterinfo_summary' in os.listdir(GNPS_file) and 'DB_result' in os.listdir(GNPS_file):
        netfile = GNPS_file + 'clusterinfo_summary/' + str(os.listdir(GNPS_file + 'clusterinfo_summary/')[0]) 
        gnpslibfile = GNPS_file + 'DB_result/'+ str(os.listdir(GNPS_file + 'DB_result/')[0]) 

    elif 'clusterinfosummarygroup_attributes_withIDs_withcomponentID' in os.listdir(GNPS_file):
        netfile = GNPS_file + 'clusterinfosummarygroup_attributes_withIDs_withcomponentID/' + str(os.listdir(GNPS_file + 'clusterinfosummarygroup_attributes_withIDs_withcomponentID/')[0])
        gnpslibfile = GNPS_file + 'result_specnets_DB/'+ str(os.listdir(GNPS_file + 'result_specnets_DB/')[0])

    else:
        netfile = GNPS_file + 'clusterinfosummary/' + str(os.listdir(GNPS_file + 'clusterinfosummary/')[0])
        gnpslibfile = GNPS_file + 'result_specnets_DB/'+ str(os.listdir(GNPS_file + 'result_specnets_DB/')[0])
    return gnpslibfile, netfile

#add all chemical structural information output as dataframe items in list
def add_Chemical_Info(gnpslibfile, directory, nap_ID=None, Derep_job_ID=None, Varquest_job_ID=None, derepfile=None, varquestfile=None):

    gnpslib = pd.read_csv(gnpslibfile, sep='\t')
    matches = [gnpslib]

    if nap_ID != None and nap_ID != 'None':
        nap = pd.read_csv("http://proteomics2.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=final_out/node_attributes_table.tsv" % nap_ID, sep = "\t")
        matches.append(nap)
    elif nap_ID == None or nap_ID == 'None':
        nap = None    

    if Derep_job_ID != None and Derep_job_ID != 'None':
        derep = pd.read_csv(derepfile + [s for s in os.listdir(derepfile) if "DEREPLICATOR" in s][0], sep = '\t')
        matches.append(derep)
    elif Derep_job_ID == None or Derep_job_ID == 'None':
        derep = None

    if Varquest_job_ID != None and Varquest_job_ID != 'None':
        varquest = pd.read_csv(varquestfile +[s for s in os.listdir(varquestfile) if "DEREPLICATOR" in s][0], sep = '\t')
        matches.append(varquest)
    elif Varquest_job_ID == None or Varquest_job_ID == 'None':
        varquest = None

    file_name = directory + '/SMILES.csv'
    out = unique_smiles(matches)
    out['df'].to_csv(file_name, quoting=csv.QUOTE_NONE, escapechar='&')
    print('SMILES have been written to "'+file_name+'"')
    return file_name, out; #returns the file name of the SMILES.csv (str)

#convert SMILES to InchiKeys
def convert_SMILES_InchiKeys(SMILES_csv, out, directory):
    import requests
    from bs4 import BeautifulSoup
    from lxml import html
    import urllib.parse

    smiles_df = pd.read_csv(SMILES_csv)

    InchiKeys_lst = []
    SMILES_failed = []
    fail_count = 0

    for i in range(len(smiles_df)):
        smile_str = smiles_df.loc[i]['SMILES']
        link = 'https://gnps-structure.ucsd.edu/inchikey?smiles={}'.format(urllib.parse.quote(smile_str))

        try:
            result = requests.get(link)
            result.raise_for_status()
            InchiKeys_lst.append('InChIKey=' + result)
        except:
            SMILES_failed.append(smile_str)
            fail_count += 1
            InchiKeys_lst.append('InChIKey=XXXXXXXXXXXXXX-XXXXXXXXXX-X')#place holder for unidentified
            
    print('Number of failed conversions is ' + str(fail_count))

    ikeys = pd.DataFrame(data=InchiKeys_lst)
    ikeys.columns = ['InChIKey']
    file_name = directory + '/InciKeys.txt'
    ikeys.to_csv(file_name, quoting=csv.QUOTE_NONE, escapechar='&')

    out['df']['inchikey'] = ikeys
    inchi_dic = make_inchidic(out)

    print('conversions have been written to "'+file_name+'"')
    return out, file_name, inchi_dic, SMILES_failed #returns dictionary, inchi_dic and list of failed

def get_Classy(InchiKeys, directory):
    get_classifications(InchiKeys)
    new_path = directory + '/all_json.json'
    os.rename('all_json.json', new_path)
    print('classifications have been written to all_json.json')

def create_ClassyFireResults(netfile, inchi_dic, directory):
    with open(directory + "/all_json.json") as tweetfile:
        jsondic = json.loads(tweetfile.read())

    df = make_classy_table(jsondic)
    df = df.rename(columns = {'class':'CF_class','smiles':'SMILES'})
    net = pd.read_csv(netfile,  sep='\t')
    final = molfam_classes(net,df,inchi_dic)

    #Renaming no matches in score columns to 0
    for key in final:
        if "_score" in key:
            final[key][final[key] == ''] = 0.0

    file_name = directory + "/ClassyFireResults_Network.txt"
    final.to_csv(file_name, sep = '\t', index = False)
    print('created "'+file_name+'"')
    return final, file_name

def create_GraphML(GNPS_file, final, directory):
    if any("FEATURE" in s for s in os.listdir(GNPS_file)):
        graphMLfile = GNPS_file + [x for x in os.listdir(GNPS_file) if 'FEATURE' in x][0]
        graphML = nx.read_graphml(graphMLfile)
        graphML_classy = make_classyfire_graphml(graphML,final)
        nx.write_graphml(graphML_classy, directory+"/ClassyFireResults_Network.graphml", infer_numeric_types = infer_numeric_types)
    elif any("METABOLOMICS" in s for s in os.listdir(GNPS_file)):
        graphMLfile = GNPS_file + [x for x in os.listdir(GNPS_file) if 'METABOLOMICS' in x][0]
        graphML = nx.read_graphml(graphMLfile)
        graphML_classy = make_classyfire_graphml(graphML,final)
        nx.write_graphml(graphML_classy, directory+"/ClassyFireResults_Network.graphml", infer_numeric_types = infer_numeric_types)
    else:
        print('There is no graphML file for this GNPS molecular network job')
    print('graphML has been written to ClassyFireResults_Network.graphml')

def pack_User_Params(prob, overlap, top):
    user_Params = [prob, overlap, top]
    return user_Params

def unpack_User_Params(user_Params):
    prob = user_Params[0]
    overlap = user_Params[1]
    top = user_Params[2]
    return prob, overlap, top

def mass_2_Motifs(GNPS_file, MS2LDA_job_ID, ClassyFireResults_file, directory, user_Params):
    #import MS2LDA data
    motifs = pd.read_csv('http://ms2lda.org/basicviz/get_gnps_summary/%s' % MS2LDA_job_ID)
    edges = pd.read_csv(GNPS_file + 'networkedges_selfloop/' + str(os.listdir(GNPS_file +'networkedges_selfloop/')[0]), sep = '\t')
    #unpack user parameters
    prob, overlap, top = unpack_User_Params(user_Params)
    #create network data with mapped motifs
    motif_network = Mass2Motif_2_Network(edges, motifs, prob, overlap, top)
    motif_network['edges'].to_csv('Mass2Motifs_Edges.tsv', sep='\t',index=False)
    motif_network['nodes'].to_csv('Mass2Motifs_Nodes.tsv', sep='\t',index=True)
    #create graphML file
    MG = make_motif_graphml(motif_network['nodes'],motif_network['edges'])
    #write graphML file
    nx.write_graphml(MG, os.path.join(directory, "Motif_Network.graphml"), infer_numeric_types = infer_numeric_types)
    final = pd.read_csv(ClassyFireResults_file, sep = "\t")
    graphML_classy = make_classyfire_graphml(MG, final)
    nx.write_graphml(graphML_classy, os.path.join(directory, "Motif_ChemicalClass_Network.graphml"), infer_numeric_types = infer_numeric_types)
    print('Mass 2 Motifs graphML has been written to Motif_ChemicalClass_Network.graphml')
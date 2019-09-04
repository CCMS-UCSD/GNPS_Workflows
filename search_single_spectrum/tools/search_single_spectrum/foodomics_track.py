# this module takes in searches for one clustered scan and runs searches against the current version of the foodomics library. A tsv containing the predicted types of the clustered scan spectrum, confidence and product scores and number of hits would be returned. 

# current version of the search maximizes sensitvity by lowering the product score threshold to 1 and the confidence to 0.3 so that it's most likely to reveal the top one to top three candidate types of the molecule at different detail level on the food tree. 

import sys
import pandas as pd
from collections import Counter
import urllib.request, json 
import os

# ignore this unless molecule name is desired. Molecule names refer to those hits from foodomic library to known compounds in the massIVE database. 
def load_mol_name(massive_url):
    data = 0
    with urllib.request.urlopen(massive_url) as url:
        data = json.loads(url.read().decode())
    massive_hits = data['blockData']
    #create a dictionary for query to molecule names
    massive_query = []
    massive_mol_attb = []
    for mhit in massive_hits:
        massive_query.append(int(mhit['#Scan#']))
        massive_mol_attb.append((mhit['Compound_Name'],mhit['MQScore'],mhit['']))
    query_mol_name_dict = dict(zip(massive_query,massive_mol_attb))
    return query_mol_name_dict


#call markers: 
#returns a tsv containing columns: cluster_scan, marker_type, confidence, number_of_hits, and product_score. 
#parameters:
#threshold: product score cutoff
#level: input 1-5 to be meaningful
#metadata: metadata sheet following the foodomics metadata protocol
#hit_table: the query results
#query_mol_name_dict: refer to comments for method load_mol_name, don't use this if you don't care about known molecules in your search query. 
#Complex: default to False, if searching complex sample, use True
#search_known: refer to method load_mol_name. if you don't care about the names, set it to False. 
def call_marker(threshold,level,metadata,hit_table,query_mol_name_dict,Complex=False,search_known=False):
    #read metadata
    metadata = pd.read_csv(metadata,delimiter='\t',index_col='filename')
    group = 'sample_type_group' + str(level)
    files = metadata.index.tolist()
    types = metadata[group].tolist()
    files_to_types = dict(zip(files,types))
    #group count
    group_count = Counter(types)
    
    hits_all = pd.read_csv(hit_table,sep='\t')
    hits_by_query = hits_all.groupby(['cluster_scan'])
    #hits_by_query
    qids = list(set(hits_all['cluster_scan'].tolist()))
    file = open('hit_marker_high_confidence_heuristic_'+str(level)+'.tsv','w+')
    if search_known==True:
        file.write('cluster_scan\tmarker_type\tconfidence\tnumber_of_hits\tmolecule_name\tmolecule_identity\tproduct_score\n')
    else:
        file.write('cluster_scan\tmarker_type\tconfidence\tnumber_of_hits\tproduct_score\n')
    for qid in qids:
        hits = hits_by_query.get_group(qid)
        hits_names = list(set(hits['filename'].tolist()))
        hits_search_name = [i.split('/')[-1].split('.')[0]+'.mzXML' for i in hits_names]
        hits_types = [files_to_types[j] for j in hits_search_name]
        norm = len(hits_types)
        hits_lib = Counter(hits_types)
        if Complex== False:
            norm = norm - hits_lib['complex']
            del hits_lib['complex']
        normalized_hits_lib = {}
        for key,val in hits_lib.items():
            normalized_hits_lib[key] = val/norm
            if normalized_hits_lib[key]*hits_lib[key] >= threshold and normalized_hits_lib[key]>=0:
                if Complex==True and (qid in query_mol_name_dict):
                    file.write(str(qid) + '\t' + key + '\t' + str(normalized_hits_lib[key]) + '\t' + str(hits_lib[key])+ '\t' + query_mol_name_dict[int(qid)][0] + '\t' + query_mol_name_dict[int(qid)][1] + '\t' + str(normalized_hits_lib[key]*hits_lib[key]) + '\n' )
                if Complex==False:
                    file.write(str(qid) + '\t' + key + '\t' + str(normalized_hits_lib[key]) + '\t' + str(hits_lib[key])+ '\t' + str(normalized_hits_lib[key]*hits_lib[key]) + '\n' )
                
    file.close()    
#find hit at all depth level on the food tree. 
def all_depth(threshold,metadata,hit_table,query_mol_name_dict,Complex=False,search_known=False):
    for level in range(1,6):
        call_marker(threshold,level,metadata,hit_table,query_mol_name_dict,Complex,search_known)

# merge the dataframes for each level together and delete intermidiates
def merge_markers():
    files = ['hit_marker_high_confidence_heuristic_1.tsv','hit_marker_high_confidence_heuristic_2.tsv','hit_marker_high_confidence_heuristic_3.tsv','hit_marker_high_confidence_heuristic_4.tsv','hit_marker_high_confidence_heuristic_5.tsv']
    df = pd.DataFrame()
    depth = 1
    for f in files:
        tmp = pd.read_csv(f,sep='\t',index_col=0)
        tmp['depth'] = pd.Series([depth]*len(tmp.index),index=tmp.index)
        if df.empty:
            df = tmp
        else:
            df = pd.concat([df,tmp])
        depth = depth + 1
    for f in files:
        os.remove(f)
    return df
    
metadata = sys.argv[1]
query = sys.argv[2]
output_filename = sys.argv[3]

try:
    #run main
    print('loading hit names')
    known_hit = {}
    print('done\nsearching for results')
    all_depth(1,metadata,query,known_hit)
    df = merge_markers()
    df.to_csv(output_filename,sep='\t')
    print('done,please see file ')
    #spectrum identifier: 
except:
    open(output_filename, "w")
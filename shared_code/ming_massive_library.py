#!/usr/bin/python

import requests
import json

def massivesearch_get_peptides_list(offset, page_size, total_rows=0):
    url = "http://massive.ucsd.edu/ProteoSAFe/QueryPROXI"
    payload = {'pageSize': page_size, "offset": offset, "query" : '#{"searched_button":"peptides"}', "query_type" : "peptide", "totalRows" : total_rows}
    r = requests.get(url, params=payload)
    return json.loads(r.text)

def massivesearch_get_psms_per_peptide(offset, page_size, peptide):
    url = "http://massive.ucsd.edu/ProteoSAFe/QueryPROXI"
    payload = {'pageSize': page_size, "offset": offset, "query" : '#{"searched_button":"psms","peptide":"%s"}' % (peptide), "query_type" : "psm"}
    r = requests.get(url, params=payload)
    return json.loads(r.text)

def massivesearch_get_variants_per_peptide(offset, page_size, peptide):
    url = "http://massive.ucsd.edu/ProteoSAFe/QueryPROXI"
    payload = {'pageSize': page_size, "offset": offset, "query" : '#{"searched_button":"psms","peptide":"%s"}' % (peptide), "query_type" : "variant"}
    r = requests.get(url, params=payload)
    return json.loads(r.text)

def massivesearch_get_proteins_per_peptide(offset, page_size, peptide):
    url = "http://massive.ucsd.edu/ProteoSAFe/QueryPROXI"
    payload = {'pageSize': page_size, "offset": offset, "query" : '#{"searched_button":"psms","peptide":"%s"}' % (peptide), "query_type" : "protein"}
    r = requests.get(url, params=payload)
    return json.loads(r.text)

def massivesearch_get_datasets_per_peptide(offset, page_size, peptide):
    url = "http://massive.ucsd.edu/ProteoSAFe/QueryPROXI"
    payload = {'pageSize': page_size, "offset": offset, "query" : '#{"searched_button":"psms","peptide":"%s"}' % (peptide), "query_type" : "dataset"}
    r = requests.get(url, params=payload)
    return json.loads(r.text)

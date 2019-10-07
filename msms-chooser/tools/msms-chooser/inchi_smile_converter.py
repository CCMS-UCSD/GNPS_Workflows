import os
import csv
import requests

# this is used to query inchi, smiles using Ming's web api
def inchi2smiles (inchi):
    url = "https://gnps-structure.ucsd.edu/smiles?inchi=%s"%inchi
    response = requests.get(url)
    if response.status_code !=200 :
        #print(response.text)
        print(url)
        print("no results for %s"%inchi)
        return ""
    return response.text

def smiles2inchi (smiles):
    url = "https://dorresteinappshub.ucsd.edu:5065/inchi?smiles=%s"%smiles
    response = requests.get(url)
    if response.status_code !=200 :
        #print(response.text)
        print("no results for %s"%smiles)
        return ""
    return response.text

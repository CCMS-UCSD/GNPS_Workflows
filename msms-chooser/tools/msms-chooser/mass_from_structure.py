import os
import csv
import requests

# this is used to query inchi, smiles using Ming's web api
def mass_from_inchi (inchi):
    print(inchi)
    url = "https://gnps-structure.ucsd.edu/structuremass?inchi=%s&filtersalts"%inchi
    response = requests.get(url)
    if response.status_code !=200 :
        print("no results")
        #print (response.text)
        print(url)
        return 0
    return float(response.text)

def mass_from_smiles (smiles):
    print(smiles)
    url = "https://gnps-structure.ucsd.edu/structuremass?smiles=%s&filtersalts"%smiles
    response = requests.get(url)
    if response.status_code !=200 :
        print("no results")
        #print (response.text)
        print(url)
        return 0
    return float(response.text)

#!/usr/bin/python

import requests
import json

#Returns the library spectra as a list
def pulldown_library(library_name):
    SERVER_URL = "http://gnps.ucsd.edu/ProteoSAFe/LibraryServlet?library="
    target_url = SERVER_URL + library_name
    r = requests.get(target_url)
    json_text = r.text
    spectra_object = json.loads(json_text)

    return spectra_object["spectra"]

def pulldown_all_continuous_libraries():
    library_names = ["all", "NIST14", "MASSBANK", "MONA", "MASSBANKEU", "HMDB", "RESPECT"]

    library_spectra = []
    for library_name in library_names:
        print "Pulling " + library_name
        library_spectra += pulldown_library(library_name)

    return library_spectra

#returns specturm
def get_library_spectrum(spectrum_id):
    SERVER_URL = "http://gnps.ucsd.edu/ProteoSAFe/SpectrumCommentServlet?SpectrumID="
    url = SERVER_URL + spectrum_id
    r = requests.get(url)
    spectrum_object = json.loads(r.text)

    return spectrum_object


#Returns all datasets as a list of dataset objects
def get_all_datasets():
    SERVER_URL = "http://gnps.ucsd.edu/ProteoSAFe/datasets_json.jsp"

    url = SERVER_URL
    r = requests.get(url)
    json_object = json.loads(r.text)

    return json_object["datasets"];

#Getting all the jobs for a particular dataset in a list
def get_continuous_id_jobs(dataset_task):
    SERVER_URL = "http://gnps.ucsd.edu/ProteoSAFe/ContinuousIDServlet?task="

    url = SERVER_URL + dataset_task
    r = requests.get(url)
    json_object = json.loads(r.text)

    return json_object["jobs"];

#Get the most recent networking job for this dataset
def get_most_recent_continuous_networking_of_dataset(dataset_task):
    all_jobs = get_continuous_id_jobs(dataset_task)
    #Assume sorted in reverse chronological ordering
    for job in all_jobs:
        if job["workflowname"] == "METABOLOMICS-SNETS":
            return job

    return None

#Valid defined as the continuous identification jobs since most recent networking
def get_valid_continous_id_jobs(dataset_task):
    all_jobs = get_continuous_id_jobs(dataset_task)
    return_jobs = []
    #Assume sorted in reverse chronological ordering
    for job in all_jobs:
        if job["workflowname"] == "METABOLOMICS-SNETS":
            return return_jobs
        return_jobs.append(job)

    return return_jobs

#Get dataset information with credentials
def get_dataset_information(dataset_task, username, password):

    s = requests.Session()

    payload = {
        'user' : username,
        'password' : password,
        'login' : 'Sign in'
    }

    r = s.post('https://' + "gnps.ucsd.edu" + '/ProteoSAFe/user/login.jsp', data=payload)

    ENDPOINT_URL = "https://gnps.ucsd.edu/ProteoSAFe/MassiveServlet?task=" + dataset_task + "&function=massiveinformation"

    r = s.get(ENDPOINT_URL)
    return json.loads(r.text)

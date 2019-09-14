#!/usr/bin/python

import os
import requests
import time
import json
import shutil
import xmltodict
import ming_fileio_library
from collections import defaultdict

PROTEOSAFE_USER_UPLOADS_DIR = "/data/ccms-data/uploads"
PROTEOSAFE_USER_FRONTEND_TASKS_DIR = "/data/ccms-data/tasks"

def parse_xml_file(input_file):
    key_value_pairs = defaultdict(list)
    xml_obj = xmltodict.parse(input_file.read())

    #print(json.dumps(xml_obj["parameters"]))
    for parameter in xml_obj["parameters"]["parameter"]:
        name = parameter["@name"]
        value = parameter["#text"]
        key_value_pairs[name].append(value)

    return key_value_pairs

def get_mangled_file_mapping(params):
    all_mappings = params["upload_file_mapping"]
    mangled_mapping = {}
    for mapping in all_mappings:
        splits = mapping.split("|")
        mangled_name = splits[0]
        original_name = splits[1]
        mangled_mapping[mangled_name] = original_name

    return mangled_mapping

def get_reverse_mangled_file_mapping(params):
    all_mappings = params["upload_file_mapping"]
    mangled_mapping = {}
    for mapping in all_mappings:
        splits = mapping.split("|")
        mangled_name = splits[0]
        original_name = splits[1]
        mangled_mapping[os.path.basename(original_name)] = mangled_name

    return mangled_mapping


def parse_specnets_param(input_filename):
    key_value_pairs = {}
    for line in open(input_filename, "r"):
        if len(line) < 1:
            continue
        key = line.split("=")[0]
        value = line.split("=")[1]
        key_value_pairs[key] = value

    return key_value_pairs


#Base url is just somethign like massive.ucsd.edu
#parameters is a map
def invoke_workflow(base_url, parameters, login, password):
    username = login
    password = password

    s = requests.Session()

    payload = {
        'user' : username,
        'password' : password,
        'login' : 'Sign in'
    }

    r = s.post('https://' + base_url + '/ProteoSAFe/user/login.jsp', data=payload)
    r = s.post('https://' + base_url + '/ProteoSAFe/InvokeTools', data=parameters)
    task_id = r.text

    if len(task_id) > 4 and len(task_id) < 60:
        print("Launched Task: : " + r.text)
        return task_id
    else:
        print(task_id)
        return None

def delete_task(base_url, task_id, login, password):
    username = login
    password = password

    s = requests.Session()

    payload = {
        'user' : username,
        'password' : password,
        'login' : 'Sign in'
    }

    delete_url = 'https://' + base_url + '/ProteoSAFe/Delete?task=' + task_id

    r = s.post('https://' + base_url + '/ProteoSAFe/user/login.jsp', data=payload)
    r = s.get(delete_url)

def restart_task(base_url, task_id, login, password):
    task_information = get_task_information(base_url, task_id)

    dont_restart_states = ["DONE", "RUNNING", "LAUNCHING"]
    if(task_information["status"] in dont_restart_states):
        return

    username = login
    password = password

    s = requests.Session()

    payload = {
        'user' : username,
        'password' : password,
        'login' : 'Sign in'
    }

    restart_url = 'https://' + base_url + '/ProteoSAFe/Restart?task=' + task_id

    r = s.post('https://' + base_url + '/ProteoSAFe/user/login.jsp', data=payload)
    r = s.get(restart_url)

def get_task_information(base_url, task_id):
    url = 'https://' + base_url + '/ProteoSAFe/status_json.jsp?task=' + task_id
    return json.loads(requests.get(url).text)

def get_my_running_jobs(base_url, login, password):
    all_jobs = get_all_my_jobs(base_url, login, password)
    running_jobs = []
    for job in all_jobs:
        if job["status"] == "RUNNING":
            running_jobs.append(job)
    return running_jobs


def get_all_my_jobs(base_url, login, password):
    username = login
    password = password

    s = requests.Session()

    payload = {
        'user' : username,
        'password' : password,
        'login' : 'Sign in'
    }

    jobs_url = 'https://' + base_url + '/ProteoSAFe/jobs_json.jsp'

    r = s.post('https://' + base_url + '/ProteoSAFe/user/login.jsp', data=payload)
    r = s.get(jobs_url)

    return json.loads(r.text)["jobs"]

def get_all_jobs(base_url, login, password):
    username = login
    password = password

    s = requests.Session()

    payload = {
        'user' : username,
        'password' : password,
        'login' : 'Sign in'
    }

    jobs_url = 'https://' + base_url + '/ProteoSAFe/jobs_json.jsp?user=all'

    r = s.post('https://' + base_url + '/ProteoSAFe/user/login.jsp', data=payload)
    r = s.get(jobs_url)

    return json.loads(r.text)["jobs"]

#Waits for not running, then returns status
def wait_for_workflow_finish(base_url, task_id):
    url = 'https://' + base_url + '/ProteoSAFe/status_json.jsp?task=' + task_id
    json_obj = json.loads(requests.get(url).text)
    while (json_obj["status"] != "FAILED" and json_obj["status"] != "DONE"):
        print("Waiting for task: " + task_id)
        time.sleep(10)
        try:
            json_obj = json.loads(requests.get(url).text)
        except KeyboardInterrupt:
            raise
        except:
            print("Exception In Wait")
            time.sleep(1)

    return json_obj["status"]


#Copies a result file from a task folder and saves it where I want
def retreive_proteosafe_result_file(task_id, username, source_folder_name, target_file):
    proteosafe_data_path = "/data/ccms-data/tasks/"
    source_folder_path = os.path.join(proteosafe_data_path, username, task_id, source_folder_name)
    source_files = ming_fileio_library.list_files_in_dir(source_folder_path)

    if len(source_files) == 1:
        #Can Copy
        source_file = os.path.join(source_files, source_files[0])
        print("Copying from " + source_file + " to " + target_file)
        shutil.copyfile(source_file, target_file)

#Returns a list of absolute paths, this goes to front end task directory
def get_proteosafe_result_file_path(task_id, username, source_folder_name):
    proteosafe_data_path = "/data/ccms-data/tasks/"
    source_folder_path = os.path.join(proteosafe_data_path, username, task_id, source_folder_name)

    if not ming_fileio_library.is_path_present(source_folder_path):
        return []

    source_files = ming_fileio_library.list_files_in_dir(source_folder_path)

    return source_files

#Returns a list of absolute paths, this goes to back end task directory
def get_proteosafe_backend_result_file_path(task_id, source_folder_name, site):
    proteosafe_data_path = "/data/"
    if site == "proteomics2":
        proteosafe_data_path += "beta-proteomics2"
    source_folder_path = os.path.join(proteosafe_data_path, "tasks", task_id, source_folder_name)
    if not ming_fileio_library.is_path_present(source_folder_path):
        return []

    source_files = ming_fileio_library.list_files_in_dir(source_folder_path)

    return source_files

def retreive_proteosafe_backend_task_directory_file_proteomics2(task_id, source_folder_name, target_file):
    retreive_proteosafe_backend_task_directory_file(task_id, "beta-proteomics2", source_folder_name, target_file)

def retreive_proteosafe_backend_task_directory_file(task_id, servername, source_folder_name, target_file):
    proteosafe_data_path = "/data/" + servername + "/tasks/"
    source_folder_path = os.path.join(proteosafe_data_path, task_id, source_folder_name)
    source_files = ming_fileio_library.list_files_in_dir(source_folder_path)

    if len(source_files) == 1:
        #Can Copy
        source_file = os.path.join(source_files, source_files[0])
        print("Copying from " + source_file + " to " + target_file)
        shutil.copyfile(source_file, target_file)

#Programmatically Make a Dataset Public
def make_dataset_public(dataset_task, username, password):
    base_url = "massive.ucsd.edu"

    s = requests.Session()

    payload = {
        'user' : username,
        'password' : password,
        'login' : 'Sign in'
    }

    r = s.post('https://' + base_url + '/ProteoSAFe/user/login.jsp', data=payload)
    r = s.get('https://' + base_url + '/ProteoSAFe/PublishDataset?' + "task=" + dataset_task)
    print("Making Datset Public")

#Adding dataset annotation, dataset_id must have MSV
def add_dataset_annotation(annotation_name, annotation_value, dataset_id, username, password):
    #Adding Accession
    base_url = "massive.ucsd.edu"

    s = requests.Session()

    payload = {
        'user' : username,
        'password' : password,
        'login' : 'Sign in'
    }

    r = s.post('https://' + base_url + '/ProteoSAFe/user/login.jsp', data=payload)
    add_url = 'https://' + base_url + '/ProteoSAFe/DatasetAnnotation?' + "function=addannotation" + "&annotation_name=" + annotation_name + "&annotation_value=" + annotation_value + "&dataset=" + dataset_id
    r = s.post(add_url)
    return r

#Adding a publication to a dataset
def add_dataset_publication(pmid, pmcid, authors, title, citation, abstract, dataset_id, username, password):
    #Adding Accession
    base_url = "massive.ucsd.edu"

    s = requests.Session()

    payload = {
        'user' : username,
        'password' : password,
        'login' : 'Sign in'
    }

    r = s.post('https://' + base_url + '/ProteoSAFe/user/login.jsp', data=payload)

    publication_payload = {
        'publication.pmid' : pmid,
        'publication.pmcid' : pmcid,
        'publication.authors' : authors,
        'publication.title' : title,
        'publication.citation' : citation,
        'publication.abstract' : abstract,
        'dataset' : dataset_id
    }

    r = s.post('https://' + base_url + '/ProteoSAFe/ManagePublications', data=publication_payload)

    print("Posted Publication")

#Get a list of all datasets
def get_all_datasets():
    base_url = "gnps.ucsd.edu"
    datasets_url = 'https://' + base_url + '/ProteoSAFe/datasets_json.jsp'
    json_obj = json.loads(requests.get(datasets_url).text)
    return json_obj["datasets"]

#Returns a dict keyed by dataset id
def get_all_dataset_dict():
    all_datasets = get_all_datasets()
    dataset_map = {}
    for dataset in all_datasets:
        dataset_map[dataset["dataset"]] = dataset
    return dataset_map

def get_dataset_information(dataset_task, username=None, password=None):
    datasets_url = "https://massive.ucsd.edu/ProteoSAFe/MassiveServlet?task=" + dataset_task + "&function=massiveinformation"
    if username != None:
        s = requests.Session()

        payload = {
            'user' : username,
            'password' : password,
            'login' : 'Sign in'
        }
        r = s.post('https://massive.ucsd.edu/ProteoSAFe/user/login.jsp', data=payload)

        return json.loads(s.get(datasets_url).text)

    else:
        json_obj = json.loads(requests.get(datasets_url).text)
        return json_obj

def get_dataset_mzTab_list(dataset_task):
    url = "http://massive.ucsd.edu/ProteoSAFe/result_json.jsp?task=%s&view=view_result_list" % (dataset_task)
    json_obj = json.loads(requests.get(url).text)["blockData"]
    return json_obj

def get_dataset_comments(dataset_task):
    url = "http://massive.ucsd.edu/ProteoSAFe/MassiveServlet?task=%s&function=comment" % (dataset_task)
    json_obj = json.loads(requests.get(url).text)
    return json_obj

def get_dataset_reanalysis(dataset_task):
    url = "http://massive.ucsd.edu/ProteoSAFe/MassiveServlet?task=%s&function=reanalysis" % (dataset_task)
    json_obj = json.loads(requests.get(url).text)
    return json_obj

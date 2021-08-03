#!/usr/bin/python

import os
import requests
import time
import json
import shutil
import xmltodict
import ming_fileio_library
from collections import defaultdict

try:
    from requests.packages.urllib3.response import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except ImportError:
    import requests.packages.urllib3
    requests.packages.urllib3.disable_warnings()


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

def get_stripped_extenstion_file_mapping(params):
    all_mappings = get_mangled_file_mapping(params)
    output_mapping = {}
    for mangled_name in all_mappings:
        output_mapping[ming_fileio_library.get_filename_without_extension(mangled_name)] = all_mappings[mangled_name]

    return output_mapping

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

    r = s.post('https://' + base_url + '/ProteoSAFe/user/login.jsp', data=payload, verify=False)
    r = s.post('https://' + base_url + '/ProteoSAFe/InvokeTools', data=parameters, verify=False)
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

    r = s.post('https://' + base_url + '/ProteoSAFe/user/login.jsp', data=payload, verify=False)
    r = s.get(delete_url, verify=False)

def restart_task(base_url, task_id, login, password, force=False):
    task_information = get_task_information(base_url, task_id)

    dont_restart_states = ["DONE", "RUNNING", "LAUNCHING"]
    if(task_information["status"] in dont_restart_states) and force == False:
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

    r = s.post('https://' + base_url + '/ProteoSAFe/user/login.jsp', data=payload, verify=False)
    r = s.get(restart_url, verify=False)

def suspend_task(base_url, task_id, login, password):
    task_information = get_task_information(base_url, task_id)

    if(task_information["status"] != "RUNNING"):
        print("Not Running")
        return

    username = login
    password = password

    s = requests.Session()

    payload = {
        'user' : username,
        'password' : password,
        'login' : 'Sign in'
    }

    suspend_url = 'https://' + base_url + '/ProteoSAFe/Suspend?task=' + task_id

    r = s.post('https://' + base_url + '/ProteoSAFe/user/login.jsp', data=payload, verify=False)
    r = s.get(suspend_url, verify=False)

def get_task_information(base_url, task_id):
    url = 'https://' + base_url + '/ProteoSAFe/status_json.jsp?task=' + task_id
    return json.loads(requests.get(url, verify=False).text)

def get_task_parameters(base_url, task_id, parameter_blacklist = ['task', 'upload_file_mapping', 'uuid', 'user']):
    params = {}
    full_url = "https://" + base_url + "/ProteoSAFe/ManageParameters"
    response = requests.get(full_url, params={"task" : task_id})

    response_text = response.text
    params = xmltodict.parse(response_text)

    parameters = params['parameters']['parameter']

    new_parameters = defaultdict(list)
    for parameter in parameters:
        param_name = parameter["@name"]
        param_value = parameter["#text"]

        if param_name not in parameter_blacklist:
            new_parameters[param_name].append(param_value)

    return new_parameters

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

    r = s.post('https://' + base_url + '/ProteoSAFe/user/login.jsp', data=payload, verify=False)
    r = s.get(jobs_url, verify=False)

    return json.loads(r.text)["jobs"]

def get_all_jobs(base_url, login, password, count=1000, offset=0):
    username = login
    password = password

    s = requests.Session()

    payload = {
        'user' : username,
        'password' : password,
        'login' : 'Sign in'
    }

    jobs_url = 'https://' + base_url + '/ProteoSAFe/jobs_json.jsp?user=all&filtertype=entries&entries=%d&offset=%d' % (count, offset)

    r = s.post('https://' + base_url + '/ProteoSAFe/user/login.jsp', data=payload)
    r = s.get(jobs_url)

    return json.loads(r.text)["jobs"]

def update_user_quota(base_url, login, password, user, quota_name, quota_value):
    username = login
    password = password

    s = requests.Session()

    payload = {
        'user' : username,
        'password' : password,
        'login' : 'Sign in'
    }

    r = s.post('https://' + base_url + '/ProteoSAFe/user/login.jsp', data=payload)

    url_for_quota = "https://" + base_url + "/ProteoSAFe/APIQuoteServlet?api=%s&user=%s&quota_limit=%d" % (quota_name, user, quota_value)

    r = s.post(url_for_quota)

    return


#Waits for not running, then returns status
def wait_for_workflow_finish(base_url, task_id):
    url = 'https://' + base_url + '/ProteoSAFe/status_json.jsp?task=' + task_id
    json_obj = json.loads(requests.get(url, verify=False).text)
    while (json_obj["status"] != "FAILED" and json_obj["status"] != "DONE" and json_obj["status"] != "SUSPENDED"):
        print("Waiting for task: " + task_id)
        time.sleep(10)
        try:
            json_obj = json.loads(requests.get(url, verify=False).text)
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

def detach_reanalysis(reanalysis_task_id, username, password):
    base_url = "massive.ucsd.edu"

    s = requests.Session()

    payload = {
        'user' : username,
        'password' : password,
        'login' : 'Sign in'
    }

    r = s.post('https://' + base_url + '/ProteoSAFe/user/login.jsp', data=payload)
    detach_url = 'https://' + base_url + '/ProteoSAFe/DetachReanalysis?task=%s' % (reanalysis_task_id)
    print(detach_url)
    r = s.get(detach_url)
    return r

#Get a list of all datasets
def get_all_datasets():
    base_url = "massive.ucsd.edu"
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

def get_dataset_file_category_folders(dataset_accession, username, password):
    s = requests.Session()

    payload = {
        'user' : username,
        'password' : password,
        'login' : 'Sign in'
    }
    r = s.post('https://massive.ucsd.edu/ProteoSAFe/user/login.jsp', data=payload)

    #Importing Dataset
    payload = {
        'importUser' : dataset_accession
    }
    r = s.post('https://massive.ucsd.edu/ProteoSAFe/ManageSharing', data=payload)

    url = 'https://massive.ucsd.edu/ProteoSAFe/ManageFiles?query={"parentDir":"%s"}' % (dataset_accession)
    json_obj = json.loads(s.get(url).text)["items"]

    return json_obj

def get_all_files_in_dataset_folder(dataset_accession, folder_prefix, username, password, includefilemetadata=False):
    s = requests.Session()

    payload = {
        'user' : username,
        'password' : password,
        'login' : 'Sign in'
    }
    r = s.post('https://massive.ucsd.edu/ProteoSAFe/user/login.jsp', data=payload)

    #Importing Dataset
    payload = {
        'importUser' : dataset_accession
    }
    r = s.post('https://massive.ucsd.edu/ProteoSAFe/ManageSharing', data=payload)

    directories_to_list = []
    directories_to_list.append(os.path.join(dataset_accession, folder_prefix))

    all_files = []
    while len(directories_to_list) > 0:
        directory_to_list = directories_to_list.pop(0)
        url = 'https://massive.ucsd.edu/ProteoSAFe/ManageFiles?query='
        try:
            #Python 2
            import urllib
            url += urllib.quote('{"parentDir":"%s"}' % (directory_to_list))
        except:
            #Python 3
            import urllib
            url += urllib.parse.quote('{"parentDir":"%s"}' % (directory_to_list))

        json_obj = json.loads(s.get(url).text)["items"]
        for item in json_obj:
            if item["directory"] == True:
                #dir_name = ming_fileio_library.get_root_folder(item["path"])
                if item["path"].find(directory_to_list) == -1:
                    print("Error Listing", directory_to_list, " Listed This, not subdir: ", item["path"], url)
                else:
                    directories_to_list.append(item["path"])
            else:
                if item["size"] > 0:
                    if includefilemetadata:
                        all_files.append({"path": item["path"], "timestamp" : int(item["modified"])})
                    else:
                        all_files.append(item["path"])
                else:
                    x = 1
                    #print("File not included, 0 size", item["path"])

    return all_files

def get_all_files_in_dataset_folder_ftp(dataset_accession, folder_prefix, includefilemetadata=False, massive_host=None):
    import ftputil

    if massive_host == None:
        massive_host = ftputil.FTPHost("massive.ucsd.edu", "anonymous", "")

    directory = os.path.join(dataset_accession, folder_prefix)

    all_files = []

    for root, dirs, files in massive_host.walk(directory, topdown=True, onerror=None):
        for filename in files:
            file_full_path = os.path.join(root, filename)
            if includefilemetadata:
                print(file_full_path)
                file_stats = massive_host.lstat(file_full_path)
                all_files.append({"path": file_full_path, "timestamp" : int(file_stats.st_mtime)})
            else:
                all_files.append(file_full_path)


    return all_files


def get_all_results_from_serverside_results_view(server, task_id, view_name):
    url = "http://%s/ProteoSAFe/result_json.jsp?task=%s&view=%s" % (server, task_id, view_name)
    r = requests.get(url)
    sqlite_filename = r.json()["blockData"]["file"]
    total_rows = int(r.json()["blockData"]["total_rows"])
    page_size = 100

    number_of_pages = int(total_rows / page_size) + 1

    all_results = []
    for i in range(number_of_pages):
        url = "http://%s/ProteoSAFe/QueryResult?task=%s&file=%s&pageSize=%d&offset=%d&query=&totalRows=%d" % (server, task_id, sqlite_filename, page_size, page_size * i, total_rows)
        print(url)
        r = requests.get(url)
        all_results += r.json()["row_data"]

    return all_results

def get_all_result_clientside_result_view(server, task_id, view_name):
    url = "http://%s/ProteoSAFe/result_json.jsp?task=%s&view=%s" % (server, task_id, view_name)
    r = requests.get(url)
    return r.json()["blockData"]



def get_all_results_from_serverside_results_view_groupbycolumn(server, task_id, view_name, column):
    url = "http://%s/ProteoSAFe/result_json.jsp?task=%s&view=%s" % (server, task_id, view_name)
    r = requests.get(url)
    sqlite_filename = r.json()["blockData"]["file"]
    total_rows = int(r.json()["blockData"]["total_rows"])

    url = "http://%s/ProteoSAFe/QueryResult?task=%s&file=%s&groupByColumn=%s" % (server, task_id, sqlite_filename, column)
    r = requests.get(url)
    return r.json()["row_data"]

# def dataset_accession_to_task(dataset_accession):
#     url = "http://massive.ucsd.edu/ProteoSAFe/QueryMSV?id=%s" % (dataset_accession)
#     r = requests.get(url)
#     print(r.text)

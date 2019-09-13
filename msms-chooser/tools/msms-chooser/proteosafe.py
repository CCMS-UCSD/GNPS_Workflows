#!/usr/bin/python

import os
import requests
import time
import json
import shutil
import xmltodict
from collections import defaultdict


def parse_xml_file(input_filename):
    key_value_pairs = defaultdict(list)
    xml_obj = xmltodict.parse(open(input_filename).read())

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

"""Admin only action"""
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

"""Admin only action"""
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

def get_my_running_jobs(base_url, login, password):
    all_jobs = get_all_my_jobs(base_url, login, password)
    running_jobs = []
    for job in all_jobs:
        if job["status"] == "RUNNING":
            running_jobs.append(job)
    return running_jobs

"""Admin only action"""
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

"""Admin only action"""
"""Updates quota values for a given username"""
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

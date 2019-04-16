from fabric.api import *
import os

env.hosts=['gnps.ucsd.edu']
#env.hosts=['proteomics2.ucsd.edu']
env.user='miw023'

def update_workflow():
    put(os.path.join(os.getcwd(), 'metabolomics-snets-v2'), "/ccms/workflows/")
    put(os.path.join(os.getcwd(), 'tools/metabolomicsnetsv2'), "/data/cluster/tools/", mirror_local_mode=True)

def update_workflow_gnps():
    local_path = os.path.join(os.getcwd(), 'tools/metabolomicsnetsv2')
    temp_path_copy = '/Users/{}/temp_tools'.format(env.user)
    temp_path = '/Users/{}/temp_tools/metabolomicsnetsv2'.format(env.user)
    final_path = '/data/cluster/tools/'
    update_folder(local_path, temp_path_copy, temp_path, final_path, user="gamma")

    local_path = os.path.join(os.getcwd(), 'metabolomics-snets-v2')
    temp_path_copy = '/Users/{}/temp'.format(env.user)
    temp_path = '/Users/{}/temp/metabolomics-snets-v2'.format(env.user)
    final_path = '/ccms/workflows/'
    update_folder(local_path, temp_path_copy, temp_path, final_path, user="ccms")

def update_folder(local_path, temp_path_copy, temp_path, final_path, user="ccms"):
    put(local_path,temp_path_copy)
    sudo('cp -r {} {}'.format(temp_path, final_path), user=user)

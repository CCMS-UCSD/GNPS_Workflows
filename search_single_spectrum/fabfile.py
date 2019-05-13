from fabric.api import *
import os

#env.hosts=['proteomics2.ucsd.edu']
env.hosts=['gnps.ucsd.edu']
env.user='miw023'
#env.gateway="mingxun@mingwangbeta.ucsd.edu"

def update_workflow():
    put(os.path.join(os.getcwd(), 'tools/search_single_spectrum'), "/data/cluster/tools/", mirror_local_mode=True)

    local_path = os.path.join(os.getcwd(), 'search_single_spectrum')
    temp_path_copy = '/Users/{}/temp'.format(env.user)
    temp_path = '/Users/{}/temp/search_single_spectrum'.format(env.user)
    final_path = '/ccms/workflows/'
    update_folder(local_path, temp_path_copy, temp_path, final_path)

def update_folder(local_path, temp_path_copy, temp_path, final_path):
    put(local_path,temp_path_copy)
    sudo('cp -r {} {}'.format(temp_path, final_path), user= 'ccms')

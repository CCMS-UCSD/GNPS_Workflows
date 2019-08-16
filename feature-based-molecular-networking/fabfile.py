from fabric.api import *
import os

env.hosts=['proteomics2.ucsd.edu']
#env.hosts=['gnps.ucsd.edu']
env.user='miw023'

#VERSION="1.2.3"

def update_workflow():
    #Making workflow the default version
    put(os.path.join(os.getcwd(), 'feature-based-molecular-networking'), "/ccms/workflows/")

    local_path = os.path.join(os.getcwd(), 'tools/feature-based-molecular-networking')
    temp_path_copy = '/Users/{}/temp_tools'.format(env.user)
    temp_path = '/Users/{}/temp_tools/feature-based-molecular-networking'.format(env.user)
    final_path = '/data/cluster/tools/'
    update_folder(local_path, temp_path_copy, temp_path, final_path, user=env.user)

def update_workflow_gnps():
    local_path = os.path.join(os.getcwd(), 'tools/feature-based-molecular-networking')
    temp_path_copy = '/Users/{}/temp_tools'.format(env.user)
    temp_path = '/Users/{}/temp_tools/feature-based-molecular-networking'.format(env.user)
    final_path = '/data/cluster/tools/'
    update_folder(local_path, temp_path_copy, temp_path, final_path, user="gamma")

    local_path = os.path.join(os.getcwd(), 'feature-based-molecular-networking')
    temp_path_copy = '/Users/{}/temp'.format(env.user)
    temp_path = '/Users/{}/temp/feature-based-molecular-networking'.format(env.user)
    final_path = '/ccms/workflows/'
    update_folder(local_path, temp_path_copy, temp_path, final_path, user="ccms")

def update_folder(local_path, temp_path_copy, temp_path, final_path, user="ccms"):
    put(local_path,temp_path_copy)
    sudo('cp -r {} {}'.format(temp_path, final_path), user=user)

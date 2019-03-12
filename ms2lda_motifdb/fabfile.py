from fabric.api import *
import os

#env.hosts=['proteomics2.ucsd.edu']
env.hosts=['gnps.ucsd.edu']
env.user='miw023'
env.gateway="mingxun@mingwangbeta.ucsd.edu"

def update_workflow():
    put(os.path.join(os.getcwd(), 'tools/ms2lda_motifdb'), "/data/cluster/tools/", mirror_local_mode=True)

    local_path = os.path.join(os.getcwd(), 'ms2lda_motifdb')
    temp_path_copy = '/Users/{}/temp'.format(env.user)
    temp_path = '/Users/{}/temp/ms2lda_motifdb'.format(env.user)
    final_path = '/ccms/workflows/'
    update_folder(local_path, temp_path_copy, temp_path, final_path)
    #put(os.path.join(os.getcwd(), 'ms2lda_motifdb'), "/ccms/workflows/")

def update_folder(local_path, temp_path_copy, temp_path, final_path):
    put(local_path,temp_path_copy)
    sudo('cp -r {} {}'.format(temp_path, final_path), user= 'ccms')

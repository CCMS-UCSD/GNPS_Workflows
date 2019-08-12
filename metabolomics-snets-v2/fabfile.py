from fabric.api import *
import os

#env.hosts=['gnps.ucsd.edu']
env.hosts=['proteomics2.ucsd.edu']
env.user='miw023'
#env.gateway="mingxun@mingwangbeta.ucsd.edu"

VERSION="1.2.5"

def update_workflow():
    #Making workflow the default version
    put(os.path.join(os.getcwd(), 'metabolomics-snets-v2'), "/ccms/workflows/")

    #Uploading workflow to a specific version
    run("mkdir /ccms/workflows/metabolomics-snets-v2/versions", warn_only=True)
    run("mkdir /ccms/workflows/metabolomics-snets-v2/versions/%s" % (VERSION) , warn_only=True)
    run("cp /ccms/workflows/metabolomics-snets-v2/*.xml /ccms/workflows/metabolomics-snets-v2/versions/%s/" % (VERSION) )
    
    #Uploading tools to a specific version area
    run("mkdir /data/cluster/tools/metabolomicsnetsv2/%s" % (VERSION) , warn_only=True)
    local_path = os.path.join(os.getcwd(), 'tools/metabolomicsnetsv2')
    temp_path_copy = '/Users/{}/temp_tools'.format(env.user)
    temp_path = '/Users/{}/temp_tools/metabolomicsnetsv2'.format(env.user)
    final_path = '/data/cluster/tools/metabolomicsnetsv2/%s/' % ()
    update_folder(local_path, temp_path_copy, temp_path, final_path, user=env.user)

    #put(os.path.join(os.getcwd(), 'tools/metabolomicsnetsv2'), "/data/cluster/tools/", mirror_local_mode=True)

def update_workflow_gnps():
    #TODO: Update actual deployment to GNPS to be correct
    print("REDO")

    # local_path = os.path.join(os.getcwd(), 'tools/metabolomicsnetsv2')
    # temp_path_copy = '/Users/{}/temp_tools'.format(env.user)
    # temp_path = '/Users/{}/temp_tools/metabolomicsnetsv2'.format(env.user)
    # final_path = '/data/cluster/tools/'
    # update_folder(local_path, temp_path_copy, temp_path, final_path, user="gamma")

    # local_path = os.path.join(os.getcwd(), 'metabolomics-snets-v2')
    # temp_path_copy = '/Users/{}/temp'.format(env.user)
    # temp_path = '/Users/{}/temp/metabolomics-snets-v2'.format(env.user)
    # final_path = '/ccms/workflows/'
    # update_folder(local_path, temp_path_copy, temp_path, final_path, user="ccms")

#The final path is not the parent, it will be equivalent to the local path
def update_folder(local_path, temp_path_copy, temp_path, final_path, user="ccms"):
    put(local_path,temp_path_copy)
    sudo('cp -r {} {}'.format(os.path.join(temp_path, "*"), final_path), user=user)

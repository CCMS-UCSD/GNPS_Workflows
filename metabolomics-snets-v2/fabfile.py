from fabric.api import *
import os

#env.hosts=['gnps.ucsd.edu']
env.hosts=['proteomics2.ucsd.edu']
env.user='miw023'
#env.gateway="mingxun@mingwangbeta.ucsd.edu"

VERSION="release_1.2.5"

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
    final_path = '/data/cluster/tools/metabolomicsnetsv2/%s/' % (VERSION)
    update_folder(local_path, temp_path_copy, temp_path, final_path, user=env.user)

def update_workflow_gnps():
    #TODO: Update actual deployment to GNPS to be correct
    print("TEST THIS WORKS")

    # Deploying the workflow
    sudo("mkdir /ccms/workflows/metabolomics-snets-v2/versions", warn_only=True, user="ccms")
    sudo("mkdir /ccms/workflows/metabolomics-snets-v2/versions/%s" % (VERSION) , warn_only=True, user="ccms")

    local_path = os.path.join(os.getcwd(), 'metabolomics-snets-v2')
    temp_path_copy = '/Users/{}/temp'.format(env.user)
    temp_path = '/Users/{}/temp/metabolomics-snets-v2'.format(env.user)
    final_path = '/ccms/workflows/metabolomics-snets-v2'
    update_folder(local_path, temp_path_copy, temp_path, final_path, user="ccms")

    #Copying to correct version
    sudo("cp /ccms/workflows/metabolomics-snets-v2/*.xml /ccms/workflows/metabolomics-snets-v2/versions/%s/" % (VERSION), user="ccms")
    
    # Deploying the tool
    sudo("mkdir /data/cluster/tools/metabolomicsnetsv2/%s" % (VERSION) , warn_only=True, user="gamma")
    local_path = os.path.join(os.getcwd(), 'tools/metabolomicsnetsv2')
    temp_path_copy = '/Users/{}/temp_tools'.format(env.user)
    temp_path = '/Users/{}/temp_tools/metabolomicsnetsv2'.format(env.user)
    final_path = '/data/cluster/tools/metabolomicsnetsv2/%s/' % (VERSION)
    update_folder(local_path, temp_path_copy, temp_path, final_path, user="gamma")
    

#The final path is not the parent, it will be equivalent to the local path
def update_folder(local_path, temp_path_copy, temp_path, final_path, user="ccms"):
    put(local_path,temp_path_copy, mirror_local_mode=True)
    sudo('cp -pr {} {}'.format(os.path.join(temp_path, "*"), final_path), user=user)

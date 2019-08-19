from fabric.api import *
import os
from xml.etree import ElementTree as ET
import uuid
import glob

#env.hosts=['gnps.ucsd.edu']
env.hosts=['proteomics2.ucsd.edu']
env.user='miw023'
env.production_user = "ccms"
env.workflow_components = ['input.xml', 'binding.xml', 'flow.xml', 'result.xml', 'tool.xml']
#env.gateway="mingxun@mingwangbeta.ucsd.edu"

VERSION="release_9"

def verify_workflow_component(workflow_filename, component):
    local = '{}/{}'.format(workflow_filename,component)
    xml = ET.parse(local)

#TODO: Validate that the xml is also a valid workflow
def update_workflow_component(workflow_filename, component, workflow_version=None, production=False):
    local = '{}/{}'.format(workflow_filename,component)
    if workflow_version:
        server = '/ccms/workflows/{}/versions/{}/{}'.format(workflow_filename, workflow_version, component)
    else:
        server = '/ccms/workflows/{}/{}'.format(workflow_filename, component)
    update_file(local, server, production=production)

def update_workflow_xml(workflow_name, workflow_version, production_str=""):
    production = production_str=="production"

    for component in env.workflow_components:
        verify_workflow_component(os.path.join(workflow_name), component)

    if production:
        sudo("mkdir /ccms/workflows/{}/versions".format(workflow_name), warn_only=True, user=env.production_user)
        sudo("mkdir /ccms/workflows/{}/versions/{}".format(workflow_name, workflow_version), warn_only=True, user=env.production_user)
    else:
        run("mkdir /ccms/workflows/{}/versions".format(workflow_name), warn_only=True)
        run("mkdir /ccms/workflows/{}/versions/{}".format(workflow_name, workflow_version), warn_only=True)

    for component in env.workflow_components:
        update_workflow_component(workflow_name, component, workflow_version=workflow_version, production=production) #Explicitly adding versioned
        update_workflow_component(workflow_name, component, production=production) #Adding to active default version

#Update File
def update_file(local_path, final_path, production=False):
    if production:
        remote_temp_path = os.path.join("/tmp/{}_{}".format(local_path.replace("/", "_"), str(uuid.uuid4())))
        put(local_path, remote_temp_path, mirror_local_mode=True)
        sudo('cp {} {}'.format(remote_temp_path, final_path), user=env.production_user)
    else:
        put(local_path, final_path, mirror_local_mode=True)

def update_folder(local_path, final_path, production=False):
    if production:
        remote_temp_path = os.path.join("/tmp/{}_{}".format(local_path.replace("/", "_"), str(uuid.uuid4())))
        put(local_path, remote_temp_path, mirror_local_mode=True)
        sudo('cp -r {} {}'.format(remote_temp_path, final_path), user=env.production_user)
    else:
        put(local_path, final_path, mirror_local_mode=True)

#Uploading the actual tools to the server
def update_tools(workflow_name, workflow_version, production_str=""):
    production = production_str=="production"

    if production:
        sudo("mkdir -p /data/cluster/tools/{}/{}".format(workflow_name, workflow_version), warn_only=True, user=env.production_user)
    else:
        run("mkdir -p /data/cluster/tools/{}/{}".format(workflow_name, workflow_version), warn_only=True)

    local_path = 'tools/{}'.format(workflow_name)
    final_path = '/data/cluster/tools/{}/{}/'.format(workflow_name, workflow_version)
    update_folder(local_path, final_path, production=production)


# def update_workflow_xml(workflow_name, workflow_version):
#     #Making workflow the default version
#     put(os.path.join(os.getcwd(), workflow_name), "/ccms/workflows/")

#     #Uploading workflow to a specific version
#     run("mkdir /ccms/workflows/metabolomics-snets-v2/versions", warn_only=True)
#     run("mkdir /ccms/workflows/metabolomics-snets-v2/versions/%s" % (VERSION) , warn_only=True)
#     run("cp /ccms/workflows/metabolomics-snets-v2/*.xml /ccms/workflows/metabolomics-snets-v2/versions/%s/" % (VERSION) )


# def update_tools(tool_folder, workflow_version):
#     #Uploading tools to a specific version area
#     run("mkdir /data/cluster/tools/metabolomicsnetsv2/%s" % (VERSION) , warn_only=True)
#     local_path = os.path.join(os.getcwd(), 'tools/metabolomicsnetsv2')
#     temp_path_copy = '/Users/{}/temp_tools'.format(env.user)
#     temp_path = '/Users/{}/temp_tools/metabolomicsnetsv2'.format(env.user)
#     final_path = '/data/cluster/tools/metabolomicsnetsv2/%s/' % (VERSION)
#     update_folder(local_path, temp_path_copy, temp_path, final_path, user=env.user)



# def update_workflow():
#     #Making workflow the default version
#     put(os.path.join(os.getcwd(), 'metabolomics-snets-v2'), "/ccms/workflows/")

#     #Uploading workflow to a specific version
#     run("mkdir /ccms/workflows/metabolomics-snets-v2/versions", warn_only=True)
#     run("mkdir /ccms/workflows/metabolomics-snets-v2/versions/%s" % (VERSION) , warn_only=True)
#     run("cp /ccms/workflows/metabolomics-snets-v2/*.xml /ccms/workflows/metabolomics-snets-v2/versions/%s/" % (VERSION) )
    
#     #Uploading tools to a specific version area
#     run("mkdir /data/cluster/tools/metabolomicsnetsv2/%s" % (VERSION) , warn_only=True)
#     local_path = os.path.join(os.getcwd(), 'tools/metabolomicsnetsv2')
#     temp_path_copy = '/Users/{}/temp_tools'.format(env.user)
#     temp_path = '/Users/{}/temp_tools/metabolomicsnetsv2'.format(env.user)
#     final_path = '/data/cluster/tools/metabolomicsnetsv2/%s/' % (VERSION)
#     update_folder(local_path, temp_path_copy, temp_path, final_path, user=env.user)

# def update_workflow_gnps():
#     # Deploying the workflow
#     sudo("mkdir /ccms/workflows/metabolomics-snets-v2/versions", warn_only=True, user="ccms")
#     sudo("mkdir /ccms/workflows/metabolomics-snets-v2/versions/%s" % (VERSION) , warn_only=True, user="ccms")

#     local_path = os.path.join(os.getcwd(), 'metabolomics-snets-v2')
#     temp_path_copy = '/Users/{}/temp'.format(env.user)
#     temp_path = '/Users/{}/temp/metabolomics-snets-v2'.format(env.user)
#     final_path = '/ccms/workflows/metabolomics-snets-v2'
#     update_folder(local_path, temp_path_copy, temp_path, final_path, user="ccms")

#     #Copying to correct version
#     sudo("cp /ccms/workflows/metabolomics-snets-v2/*.xml /ccms/workflows/metabolomics-snets-v2/versions/%s/" % (VERSION), user="ccms")
    
#     # Deploying the tool
#     sudo("mkdir /data/cluster/tools/metabolomicsnetsv2/%s" % (VERSION) , warn_only=True, user="gamma")
#     local_path = os.path.join(os.getcwd(), 'tools/metabolomicsnetsv2')
#     temp_path_copy = '/Users/{}/temp_tools'.format(env.user)
#     temp_path = '/Users/{}/temp_tools/metabolomicsnetsv2'.format(env.user)
#     final_path = '/data/cluster/tools/metabolomicsnetsv2/%s/' % (VERSION)
#     update_folder(local_path, temp_path_copy, temp_path, final_path, user="gamma")
    

# #The final path is not the parent, it will be equivalent to the local path
# def update_folder(local_path, temp_path_copy, temp_path, final_path, production=False):
#     if production:
#         put(local_path,temp_path_copy, mirror_local_mode=True)
#         sudo('cp -pr {} {}'.format(os.path.join(temp_path, "*"), final_path), user="ccms")
#     else:
#         put(local_path,final_path, mirror_local_mode=True)


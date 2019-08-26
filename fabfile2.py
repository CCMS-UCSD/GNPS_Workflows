from fabric import Connection
from fabric import task
import os
from xml.etree import ElementTree as ET
import uuid
import glob

#env.hosts=['gnps.ucsd.edu']
# env.hosts=['proteomics2.ucsd.edu']
# env.user='miw023'
# env.production_user = "ccms"
# env.workflow_components = ['input.xml', 'binding.xml', 'flow.xml', 'result.xml', 'tool.xml']
# env.gateway="mingxun@mingwangbeta.ucsd.edu"

workflow_components = ['input.xml', 'binding.xml', 'flow.xml', 'result.xml', 'tool.xml']

# fab_connection = Connection(
#     host="proteomics2.ucsd.edu",
#     user="miw023"
# )

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
    fab_connection.update_file(local, server, production=production)

@task
def update_workflow_xml(fab_connection, workflow_name, workflow_version, production_str=""):
    production = production_str=="production"

    for component in workflow_components:
        verify_workflow_component(os.path.join(workflow_name), component)

    if production:
        fab_connection.sudo("mkdir /ccms/workflows/{}/versions".format(workflow_name), warn_only=True, user=env.production_user)
        fab_connection.sudo("mkdir /ccms/workflows/{}/versions/{}".format(workflow_name, workflow_version), warn_only=True, user=env.production_user)
    else:
        fab_connection.run("mkdir /ccms/workflows/{}/versions".format(workflow_name), warn_only=True)
        fab_connection.run("mkdir /ccms/workflows/{}/versions/{}".format(workflow_name, workflow_version), warn_only=True)

    for component in workflow_components:
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
        print("Uploading folder", local_path, final_path)
        #put(local_path, final_path, mirror_local_mode=True)

#Uploading the actual tools to the server
@task
def update_tools(workflow_name, workflow_version, production_str=""):
    production = production_str=="production"

    if production:
        sudo("mkdir -p /data/cluster/tools/{}/{}".format(workflow_name, workflow_version), warn_only=True, user=env.production_user)
    else:
        run("mkdir -p /data/cluster/tools/{}/{}".format(workflow_name, workflow_version), warn_only=True)

    local_path = 'tools/{}'.format(workflow_name)
    final_path = '/data/cluster/tools/{}/{}/'.format(workflow_name, workflow_version)

    print(local_path, final_path)

    update_folder(local_path, final_path, production=production)
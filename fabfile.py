from fabric import Connection
from fabric import task
from fabric import config
import os
from xml.etree import ElementTree as ET
import uuid
import glob

# env.hosts=['gnps.ucsd.edu']
# env.hosts=['proteomics2.ucsd.edu']
# env.user='miw023'
# env.production_user = "ccms"
# env.workflow_components = ['input.xml', 'binding.xml', 'flow.xml', 'result.xml', 'tool.xml']

workflow_components = ['input.xml', 'binding.xml', 'flow.xml', 'result.xml', 'tool.xml']

VERSION="release_9"

def verify_workflow_component(workflow_filename, component):
    local = '{}/{}'.format(workflow_filename,component)
    xml = ET.parse(local)

#TODO: Validate that the xml is also a valid workflow
def update_workflow_component(fab_connection, workflow_filename, component, workflow_version=None, production=False):
    local = '{}/{}'.format(workflow_filename,component)
    if workflow_version:
        server = '/ccms/workflows/{}/versions/{}/{}'.format(workflow_filename, workflow_version, component)
    else:
        server = '/ccms/workflows/{}/{}'.format(workflow_filename, component)
    update_file(fab_connection, local, server, production=production)

@task
def update_workflow_xml(fab_connection, workflow_name, workflow_version, production_str=""):
    production = production_str=="production"

    for component in workflow_components:
        verify_workflow_component(os.path.join(workflow_name), component)

    if production:
        fab_connection.sudo("mkdir /ccms/workflows/{}/versions".format(workflow_name), user=env.production_user)
        fab_connection.sudo("mkdir /ccms/workflows/{}/versions/{}".format(workflow_name, workflow_version), user=env.production_user)
    else:
        fab_connection.run("mkdir /ccms/workflows/{}/versions".format(workflow_name))
        fab_connection.run("mkdir /ccms/workflows/{}/versions/{}".format(workflow_name, workflow_version))

    for component in workflow_components:
        update_workflow_component(fab_connection, workflow_name, component, workflow_version=workflow_version, production=production) #Explicitly adding versioned
        update_workflow_component(fab_connection, workflow_name, component, production=production) #Adding to active default version

#Update File
def update_file(fab_connection, local_path, final_path, production=False):
    if production:
        remote_temp_path = os.path.join("/tmp/{}_{}".format(local_path.replace("/", "_"), str(uuid.uuid4())))
        fab_connection.put(local_path, remote_temp_path, preserve_mode=True)
        fab_connection.sudo('cp {} {}'.format(remote_temp_path, final_path), user=fab_connection["env"]["production_user"])
    else:
        fab_connection.put(local_path, final_path, preserve_mode=True)

#TODO: update this to work with rsync
def update_folder(fab_connection, local_path, final_path, production=False):
    #Tar up local folder and upload to temporary space on server and untar
    local_temp_path = os.path.join("/tmp/{}_{}.tar".format(local_path.replace("/", "_"), str(uuid.uuid4())))
    cmd = "tar -C {} -chvf {} .".format(local_path, local_temp_path)
    print(cmd)
    os.system(cmd)

    remote_temp_tar_path = os.path.join("/tmp/{}_{}.tar".format(local_path.replace("/", "_"), str(uuid.uuid4())))
    fab_connection.put(local_temp_path, remote_temp_tar_path, preserve_mode=True)

    remote_temp_path = os.path.join("/tmp/{}_{}".format(local_path.replace("/", "_"), str(uuid.uuid4())))
    fab_connection.run("mkdir {}".format(remote_temp_path))
    fab_connection.run("tar -C {} -xvf {}".format(remote_temp_path, remote_temp_tar_path))

    if production:
        #fab_connection.sudo('rsync -rlptDv {}/ {}'.format(remote_temp_path, final_path), user=fab_connection["env"]["production_user"], password=fab_connection["sudo"]["password"])
        #fab_connection.sudo('rsync -rlptDv {}/ {}'.format(remote_temp_path, final_path))
        fab_connection.run('sudo su ccms && whoami')
        fab_connection.run('sudo su ccms && whoami')
        fab_connection.run('whoami')
    else:
        fab_connection.run('rsync -rlptDv {}/ {}'.format(remote_temp_path, final_path))

#Uploading the actual tools to the server
@task
def update_tools(fab_connection, workflow_name, workflow_version, production_str=""):
    production = production_str=="production"

    if production:
        fab_connection.sudo("mkdir -p /data/cluster/tools/{}/{}".format(workflow_name, workflow_version), user=fab_connection["env"]["production_user"])
    else:
        fab_connection.run("mkdir -p /data/cluster/tools/{}/{}".format(workflow_name, workflow_version))

    local_path = 'tools/{}/'.format(workflow_name)
    final_path = '/data/cluster/tools/{}/{}/'.format(workflow_name, workflow_version)

    update_folder(fab_connection, local_path, final_path, production=production)
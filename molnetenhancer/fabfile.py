from fabric.api import *
import os

env.hosts=['proteomics2.ucsd.edu']
#env.hosts=['gnps.ucsd.edu']
env.user='miw023'

def update_workflow():
    put(os.path.join(os.getcwd(), 'molnetenhancer'), "/ccms/workflows/")
    put(os.path.join(os.getcwd(), 'tools/molnetenhancer'), "/data/cluster/tools/", mirror_local_mode=True)

from fabric.api import *
import os

env.hosts=['proteomics2.ucsd.edu']
env.user='miw023'

def update_workflow():
    put(os.path.join(os.getcwd(), 'feature-based-molecular-networking'), "/ccms/workflows/")
    put(os.path.join(os.getcwd(), 'tools/feature-based-molecular-networking'), "/data/cluster/tools/")

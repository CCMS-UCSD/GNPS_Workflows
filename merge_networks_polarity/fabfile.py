from fabric.api import *
import os

env.hosts=['proteomics2.ucsd.edu']
#env.hosts=['gnps.ucsd.edu']
env.user='miw023'

def update_workflow():
    put(os.path.join(os.getcwd(), 'merge_networks_polarity'), "/ccms/workflows/")
    put(os.path.join(os.getcwd(), 'tools/MergePolarity'), "/data/cluster/tools/", mirror_local_mode=True)

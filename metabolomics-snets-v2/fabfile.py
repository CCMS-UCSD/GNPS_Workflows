from fabric.api import *
import os

#env.hosts=['gnps.ucsd.edu']
env.hosts=['proteomics2.ucsd.edu']
env.user='miw023'

def update_workflow():
    put(os.path.join(os.getcwd(), 'metabolomics-snets-v2'), "/ccms/workflows/")
    put(os.path.join(os.getcwd(), 'tools/metabolomicsnetsv2'), "/data/cluster/tools/", mirror_local_mode=True)

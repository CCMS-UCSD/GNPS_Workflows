from fabric.api import *
import os

env.hosts=['proteomics2.ucsd.edu']
#env.hosts=['gnps.ucsd.edu']
env.user='miw023'

def update_workflow():
    put(os.path.join(os.getcwd(), 'ms2lda_motifdb'), "/ccms/workflows/")
    put(os.path.join(os.getcwd(), 'tools/ms2lda_motifdb'), "/data/cluster/tools/")

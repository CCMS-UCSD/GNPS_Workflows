from fabric.api import *
import os

env.hosts=['proteomics2.ucsd.edu']
env.user='miw023'

# def update_binaries():
#    binaries = [
#        ('/Users/ben/Developer/sps/bin','main_execmodule'),
#        ('/Users/ben/Developer/sps/bin','convert')
#    ]
#    for (path,binary) in binaries:
#        put(os.path.join(path,binary),os.path.join('/data/cluster/tools/dis_cluster_fast',binary))

def update_workflow():
    myfiles = [
        ('./feature-based-molecular-networking/flow.xml','/ccms/workflows/feature-based-molecular-networking/flow.xml'),
        ('./feature-based-molecular-networking/binding.xml','/ccms/workflows/feature-based-molecular-networking/binding.xml'),
        ('./feature-based-molecular-networking/result.xml','/ccms/workflows/feature-based-molecular-networking/result.xml'),
        ('./feature-based-molecular-networking/tool.xml','/ccms/workflows/feature-based-molecular-networking/tool.xml')
    ]

    for (local,remote) in myfiles:
        put(local,remote)

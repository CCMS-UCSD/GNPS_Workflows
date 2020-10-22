## conda installation

1. wget https://data.qiime2.org/distro/core/qiime2-2019.10-py36-linux-conda.yml
1. conda env create -n qiime2-2019.10-mmvec --file qiime2-2019.10-py36-linux-conda.yml
1. conda install -n qiime2-2019.10-mmvec mmvec=1.0.4 -c conda-forge
1. qiime dev refresh-cache


## conda installation

wget https://data.qiime2.org/distro/core/qiime2-2019.10-py36-linux-conda.yml
conda env create -n qiime2-2019.10-mmvec --file qiime2-2019.10-py36-linux-conda.yml
conda install -n qiime2-2019.10-mmvec mmvec=1.0.4 -c conda-forge
qiime dev refresh-cache


## conda installation

wget https://data.qiime2.org/distro/core/qiime2-2019.4-py36-linux-conda.yml
conda env create -n qiime2-2019.4-mmvec --file qiime2-2019.4-py36-linux-conda.yml
conda install -n qiime2-2019.4-mmvec mmvec -c conda-forge
qiime dev refresh-cache


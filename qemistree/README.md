To install environment, make qiime2-2020.11-qemistree using yml for conda. Then

```
/data/ccms-gnps/tools/miniconda3_gamma/bin/conda env create -n qiime2-2020.11-qemistree --file qiime2-2020.11-py36-linux-conda.yml
```

### Updating q2-qemistree

```
pip uninstall q2-qemistree
pip install https://github.com/biocore/q2-qemistree/archive/2020.1.4.tar.gz
export LC_ALL=en_US.UTF-8 && qiime dev refresh-cache
LC_ALL=en_US.UTF-8 && ./pip install empress
qiime dev refresh-cache
```

### Installing Sirius

```
cd tools/qemistree
wget https://bio.informatik.uni-jena.de/repository/dist-release-local/de/unijena/bioinf/ms/sirius/4.9.3/sirius-4.9.3-linux64-headless.zip
unzip sirius-4.9.3-linux64-headless.zip
```

NOTE: Sirius will not work in a branch because it does not tolerate a : in the path

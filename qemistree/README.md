To install environment, make qiime2-2020.11-qemistree using yml for conda. Then

```
/data/ccms-gnps/tools/miniconda3_gamma/bin/conda env create -n qiime2-2020.11-qemistree --file qiime2-2020.11-py36-linux-conda.yml
```

### Updating q2-qemistree
1. pip uninstall q2-qemistree
1. pip install https://github.com/biocore/q2-qemistree/archive/2020.1.4.tar.gz
1. export LC_ALL=en_US.UTF-8 && qiime dev refresh-cache
1. LC_ALL=en_US.UTF-8 && ./pip install empress
1. qiime dev refresh-cache

NOTE: Sirius will not work in a branch because it does not tolerate a : in the path

To install environment, make qiime2-2019.10-qemistree using yml for conda. Then

### Updating q2-qemistree
1. pip uninstall q2-qemistree
1. pip install https://github.com/biocore/q2-qemistree/archive/2020.1.3.tar.gz
1. export LC_ALL=en_US.UTF-8 && qiime dev refresh-cache
1. LC_ALL=en_US.UTF-8 && ./pip install empress
1. qiime dev refresh-cache

NOTE: Sirius will not work in a branch because it does not tolerate a : in the path

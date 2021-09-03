## Environment Setup

On the GNPS side, to get everything set up for this template workflow, need a few steps:

Installing Conda Enviornment

```
conda create -n msql2 python=3.9
```

Installing dependencies

```
conda install -n msql2 -c bioconda nextflow
conda activate msq2 
pip install -r requirements.txt
```
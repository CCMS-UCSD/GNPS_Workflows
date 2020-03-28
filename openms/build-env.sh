#!/bin/bash

print_usage() {
  echo "Usage: $0 <openms-release/binaries/conda path> <conda-env.yaml path>"
}

if [ $# -ne 3 ]; then
  print_usage
  exit 1
else
  CONDA_ROOT=$1
  CONDA_YML=$2
fi




###
# Install + Build Miniconda Environment
###
# Download Mininconda install script
CONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
CONDA_SCRIPT_FILE="./Miniconda3.sh"
curl -o ${CONDA_SCRIPT_FILE} ${CONDA_URL}

# Install Miniconda
bash ${CONDA_SCRIPT_FILE}

# Clean Miniconda installer from dir
rm ${CONDA_SCRIPT_FILE}


###
# Update Conda Environment with Dependencies
###
conda env update --file ${CONDA_YML}


###
# Correct default conda lib links
###
cd ${CONDA_ROOT}/bin
ln -s x86_64-conda_cos6-linux-gnu-cc cc
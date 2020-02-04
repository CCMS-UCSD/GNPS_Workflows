# Environment Variables
```bash
unset PATH
unset LD_LIBRARY_PATH

CONDA_ROOT=<path to conda root>
OPENMS_CONTRIB_LIBS=<path to openms contrib-build lib>
OPENMS_BUILD=<path to openms build dir>

###
# conda
###
export PATH=${CONDA_ROOT}/bin
export LD_LIBRARY_PATH=${CONDA_ROOT}/lib

###
# openms contrib-build
###
export PATH=${PATH}:${OPENMS_CONTRIB_LIBS}/bin
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${OPENMS_CONTRIB_LIBS}/lib

###
# openms-build
###
export PATH=${PATH}:${OPENMS_BUILD}/bin
export LD_LIBRARY_PATH=${PATH}:${OPENMS_BUILD}/lib

###
# set CXX compiler include flag
###
export CXXFLAGS="-isystem ${OPENMS_CONTRIB_LIBS}/include"

###
# inlcude system binaries
###
export PATH=${PATH}:/bin:/usr/bin
```

# Builiding OpenMS
## Conda Environment
Use conda environment as specified by exported environment dependencies: [conda-env.yaml](./conda-env.yaml)

### Library Dependencies Checks:
1. Ensure that `cc` library is properly simlinked <br>
`conda install -c conda-forge cxx-compiler`
    - **Check**: Determine which cc is linked
      ```bash
      $ which cc
      {CONDA_ROOT}/bin/cc
      ``` 
    - **Solution**: Create symlink
      ```bash
      $ cd ${CONDA_ROOT}/bin
      $ ln -s x86_64-conda_cos6-linux-gnu-cc cc
      $ export PATH=${CONDA_ROOT}/bin:${PATH}     # ensure that conda binaries are pathed
      ```
      
## Building OpenMS Contrib Libraries
1. Install openms contrib libraries
    ```bash
    $ export OPENMS_CONTRIB_SRC=<path to contrib clone>
    $ git clone https://github.com/openms/contrib.git ${OPENMS_CONTRIB_SRC}
    $ cmake -DBUILD_TYPE=<library> -DNUMBER_OF_JOBS=<num compile jobs> ${OPENMS_CONTRIB_SRC}
    ```
    - **Required Libraries**: These are the libraries that are not included in the clean conda env
    ```bash
    $ cmake -DBUILD_TYPE=LIBSVM -DNUMBER_OF_JOBS=8 ${OPENMS_CONTRIB_SRC}
    $ cmake -DBUILD_TYPE=COINOR .
    $ cmake -DBUILD_TYPE=GLPK .
    $ cmake -DBUILD_TYPE=WILDMAGIC .
    $ cmake -DBUILD_TYPE=HDF5 .
    ```

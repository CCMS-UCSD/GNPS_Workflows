# Building Runtime Environment
1. Download the [conda-env.yaml](./conda-env.yaml) file
    ```bash
    curl -o conda-env.yaml <conda-env.yaml url>
    ```

2. Download the [build-env.sh](./build-env.sh) shell script
    ```bash
    curl -o build.env.sh <build-env.sh url>
    ```

3. Run the build script to install the library environment
    - Conda must be installed at `<openms-release>/binaries/conda`
    ```bash
    $ bash build-env.sh     
    # accept license agreement
    >>> yes
    # location for conda install should be in release/binaries/conda dir
    >>> <openms_release>/binaries/conda
    # DO NOT RUN conda init
    >>> no
    ```

    ## Debugging `build-env.sh` script
    The [build-env.sh]() shell program executes the following:
    1. Download and install the latest version of Miniconda3
        ```bash
        ###
        # Install + Build Miniconda Environment
        ###
        # Download Mininconda install script
        curl -o "./Miniconda3.sh" "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"

        # Install Miniconda
        bash "./Miniconda3.sh"
        ```

    2. Update conda environment with OpenMS dependencies
        ```bash
        conda env update --file <conda-env.yaml>
        ```

    3. Ensure that `cc` library is properly symlinked <br>
        `conda install -c conda-forge cxx-compiler`
        - **Check**: Determine which cc is linked
          ```bash
          $ which cc
          {CONDA_ROOT}/bin/cc
          ```
        - **Solution**: Create symlink
          ```bash
          $ cd <openms-release>/binaries/conda/bin
          $ ln -s x86_64-conda_cos6-linux-gnu-cc cc
          # ensure that conda binaries are pathed
          $ export PATH=${CONDA_ROOT}/bin:${PATH}
          ```          

# Building OpenMS
> :warning: Ensure that system libaries are up-to-date with OpenMS-2.4 prerequisites
## Environment Parameters
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
###å
export PATH=${PATH}:/bin:/usr/bin
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

## Building OpenMS Binaries
```bash
$ cd ${OPENMS_BUILD_DIR}
$ cmake -DOPENMS_CONTRIB_LIBS="${OPENMS_CONTRIB_LIBS}" -DCMAKE_PREFIX_PATH="${CONDA_ROOT}" "${OPENMS_ROOT}"
```
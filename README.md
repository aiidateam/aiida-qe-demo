# aiida-qe-demo

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/chrisjsewell/aiida-qe-demo/main?labpath=tutorial)

A demonstration tutorial of using aiida-quantumespresso

## Building the documentation

To build the documentation, first install the dependencies in a conda environment (using mamba to resolve dependencies):

    mamba env create -f environment.yml
    conda activate aiida-qe-demo

Then, build the documentation:

    sphinx-build -nW --keep-going -b html tutorial tutorial/_build/html

Note that the first time you build the documentation, it will take a while to execute all the notebooks.
But subsequent builds will be much faster, as the notebooks will be cached.

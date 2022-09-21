# AiiDA Quantum Espresso Demonstration

This tutorial is a demonstration of the AiiDA workflow manager.

It is intended to give a quick overview of the main features of AiiDA, and to show how they can be used to set up and run quantum calculations, using [Quantum ESPRESSO](https://www.quantum-espresso.org/) as an example.

The tutorial is divided into a number of sections, each of which is a Jupyter notebook.

## Running the tutorial

The tutorial can be run in two ways:

### Using Binder

The easiest way to run the tutorial is to click on the Binder badge below, which will launch a Binder instance with the tutorial pre-installed.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/chrisjsewell/aiida-qe-demo/main?labpath=tutorial%2Fintro.ipynb)

### Locally

Alternatively, you can run the tutorial locally, by following the instructions below.

#### Install the tutorial

First, clone the tutorial repository:

    git clone

Then, install the tutorial environment using [mamba](https://mamba.readthedocs.io):

    mamba env create -f environment.yml

Finally, activate the environment:

    mamba activate aiida-qe-demo

Then, start the Jupyter notebook server:

    jupyter lab

```{toctree}
:hidden:

intro
next
```

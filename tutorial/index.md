---
sd_hide_title: true
---

# AiiDA Demonstration

![aiida graph](_static/aiida/common_workflow_calculator_plus_sponsors.png)

This tutorial is a demonstration of the AiiDA workflow manager.
It is intended to:

1. Give a brief overview of the main features of AiiDA
2. Show how it can be used to set up and run quantum calculations, using [Quantum ESPRESSO](https://www.quantum-espresso.org/) as an example.
3. Show how the results of these calculations can be explored.
4. Show how calculation can be combined into complex workflow and run in high-throughput.

```{toctree}
:hidden:
:numbered:

1_what_is_aiida
2_bands_workflow
3_qe_to_aiida
4_generating_inputs
5_error_handling
6_write_your_own_workflow
7_next_steps
glossary
```

## Interacting with the tutorial

The tutorial is divided into a number of sections, most of which are written Jupyter notebook, that can be run within the [Conda environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) provided in {download}`environment.yaml <../environment.yml>`.

### Using Binder

The easiest way to run the notebooks is to click on the Binder badge below, which will launch a Binder instance with the environment pre-installed.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/chrisjsewell/aiida-qe-demo/main?labpath=tutorial)

Alternatively, any page with a 🚀 icon can be launched in Binder by clicking on it.

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

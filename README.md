February 2025
## Contents

- [Overview](#overview)
- [Repo Contents](#repo-contents)
- [System Requirements](#system-requirements)
- [Installation Guide](#installation-guide)
- [Demo](#demo)
- [Citation](#citation)

# Overview
This Repo includes scripts for data processing and analysis for the Antarctic Ecosystem Value (AEV) Index.
The AEV Index is created by merging ecosystem information across food web trophic levels to identify valuable
regions around Antarctica across trophic levels. This Index is derived from publically available Earth System
Model (ESM) data. 

Previous and current CESM versions are freely available online at the CESM2 website: 
https://www.cesm.ucar.edu/models/cesm2/

The CESM2 Large Ensemble data are freely available at: https://www.earthsystemgrid.org/dataset/ucar.cgd.cesm2le.output.html

The CESM2 FOSI data are freely available at: https://app.globus.org/file-manager?origin_id=6f5e56da-0353-4bd4-bac0-04a104e05d58&origin_path=%2FLR%2F&two_pane=false

# Repo Contents
- [data_processing](./data_processing): JupyterHub notebooks for processing the AEV Index from ESM data inputs.
- [figures](./figures): JupyterHub notebooks for creating manuscript figures.
- [environment](./environment): Information about the analysis environment

# System Requirements
This code was run on Jupyter Hub the NSF NCAR high performance computing Casper machine for data analysis and visualization. 

Information about the Casper system including all available software is found here: https://ncar-hpc-docs.readthedocs.io/en/latest/compute-systems/casper/

Information about the JupyterHub installation on Casper is found here: https://ncar-hpc-docs.readthedocs.io/en/latest/compute-systems/jupyterhub/

# Installation Guide
On Casper, we have created the following files to recreate the analysis environment by doing the following:
1. From command line, activate environment:
```
conda activate analysis3
```

2. To get a list of human readable packages, once you have the environment activated do the following:
```
conda list >> conda_list.txt
```
The results of this command are in the file called "conda_list.txt" in the environment. 

3. We have exported the environment as a yml file:
```
conda env export --from-history > environment.yml
```

4. To recreate the python environment, do the following at the command line:
```
conda env create -f environment.yml -n new_env_name
```

# Demo

TEXT HERE

# Citation
This code was created for a manuscript that is currently in review at Nature Communications.

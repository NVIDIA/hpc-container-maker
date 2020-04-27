[![Python 3](https://github.com/NVIDIA/hpc-container-maker/workflows/Python%203/badge.svg)](https://github.com/NVIDIA/hpc-container-maker/actions?query=workflow%3A%22Python+3%22)
[![Python 2](https://github.com/NVIDIA/hpc-container-maker/workflows/Python%202/badge.svg)](https://github.com/NVIDIA/hpc-container-maker/actions?query=workflow%3A%22Python+2%22)
[![Conda](https://img.shields.io/conda/dn/conda-forge/hpccm?label=Conda%20downloads)](https://anaconda.org/conda-forge/hpccm)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/hpccm?label=PyPI%20downloads)](https://pypi.org/project/hpccm/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/NVIDIA/hpc-container-maker.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/NVIDIA/hpc-container-maker/context:python)
[![License](https://img.shields.io/github/license/NVIDIA/hpc-container-maker)](https://github.com/NVIDIA/hpc-container-maker/blob/master/LICENSE)

# HPC Container Maker

HPC Container Maker (HPCCM - pronounced H-P-see-M) is an open source
tool to make it easier to generate container specification files.

- [Documentation](/docs)
    - [Getting Started](/docs/getting_started.md)
    - [Tutorial](/docs/tutorial.md)
    - [Recipes](/docs/recipes.md)
    - [Workflows](/docs/workflows.md)
    - [API: Building Blocks](/docs/building_blocks.md)
    - [API: Primitives](/docs/primitives.md)
    - [API: Miscellaneous](/docs/misc_api.md)
- [Examples](/recipes/)
- [Citation](/docs/citation.md)
- [License](/LICENSE)

## Overview

HPC Container Maker generates Dockerfiles or Singularity definition
files from a high level Python recipe.  HPCCM recipes have some
distinct advantages over "native" container specification formats.

1. A library of HPC [building blocks](/docs/building_blocks.md) that
   separate the choice of what to include in a container image from
   the details of how it's done.  The building blocks transparently
   provide the latest component and container best practices.

2. Python provides increased flexibility over static container
   specification formats.  Python-based recipes can branch, validate
   user input, etc. - the same recipe can generate multiple container
   specifications.

3. Generate either Dockerfiles or Singularity definition files from
   the same recipe.

## Additional Resources

- [Making Containers Easier With HPC Container Maker (paper)](https://github.com/HPCSYSPROS/Workshop18/blob/master/Making_Containers_Easier_with_HPC_Container_Maker/ws_hpcsysp103.pdf), presented at the [HPC Systems Professionals Workshop at SC18](/docs/citation.md)
- [Overview presentation at SC18 (video)](http://on-demand.gputechconf.com/supercomputing/2018/video/sc1843-making-containers-easier-hpc-container-maker.html)
- [Making Containers Easier with HPC Container Maker (webinar)](https://www.nvidia.com/content/webinar-portal/src/webinar-portal.html?D2C=1802760&isSocialSharing=Y&partnerref=emailShareFromGateway)
- [ADMIN Magazine article](http://www.admin-magazine.com/HPC/Articles/HPC-Container-Maker) by Jeff Layton
- [NVIDIA Developer Blog](https://devblogs.nvidia.com/making-containers-easier-with-hpc-container-maker/) by Scott McMillan

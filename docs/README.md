# HPC Container Maker Documentation

HPC Container Maker (HPCCM - pronounced H-P-see-M) is an open source
tool to make it easier to generate container specification files.

- [Getting Started](/docs/getting_started.md)
- [Tutorial](/docs/tutorial.md)
- [Recipes](/docs/recipes.md)
- [Workflows](/docs/workflows.md)
- [Examples](/recipes/)
- [API: Building Blocks](/docs/building_blocks.md)
- [API: Primitives](/docs/primitives.md)
- [License](/LICENSE)

## Overview

HPC Container Maker generates Dockerfiles or Singularity definition
files from a high level Python recipe.  HPCCM recipes have some
distinct advantages over "native" container specification formats.

1. A library of HPC [buildling blocks](/docs/building_blocks.md) that
   separate the choice of what to include in a container image from
   the details of how it's done.  The building blocks transparently
   take advantage of the latest component and container best
   practices.

2. Python provides increased flexibility over static container
   specification formats.  Python-based recipes can branch, validate
   user input, etc. - the same recipe can generate multiple container
   specifications.

3. Generate either Dockerfiles or Singularity definition files from
   the same recipe.

## Citation

```
@InProceedings{McMillanHPCSYSPROS18,
  author = {McMillan, Scott},
  title = {Making Containers Easier with HPC Container Maker},
  url = {https://github.com/HPCSYSPROS/Workshop18/tree/master/Making_Container_Easier_with_HPC_Container_Maker},
  booktitle = {In HPCSYSPROS18: HPC System Professionals Workshop},
  year = {2018},
  month = {November},
  address = {Dallas, TX},
}
```

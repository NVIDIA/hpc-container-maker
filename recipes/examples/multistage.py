"""This example demonstrates how to specify a multi-stage recipe.

Usage:
$ hpccm.py --recipe recipes/examples/multistage.py
"""

######
# Devel stage
######

# Devel stage base image
Stage0.name = 'devel'
Stage0.baseimage('nvidia/cuda:9.0-devel-ubuntu16.04')

# Install compilers (upstream)
g = gnu()
Stage0 += g

# Build FFTW using all default options
f = fftw()
Stage0 += f

######
# Runtime stage
######

# Runtime stage base image
Stage1.baseimage('nvidia/cuda:9.0-runtime-ubuntu16.04')

# Compiler runtime (upstream)
Stage1 += g.runtime()

# Copy the FFTW build from the devel stage and setup the runtime environment.
# The _from option is not necessary, but increases clarity.
Stage1 += f.runtime(_from=Stage0.name)

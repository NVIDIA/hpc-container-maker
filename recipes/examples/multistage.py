"""This example demonstrates how to specify a multi-stage recipe.

Usage:
$ hpccm.py --recipe recipes/examples/multistage.py
"""

######
# Devel stage
######

# Devel stage base image
Stage0 += baseimage(image='nvcr.io/nvidia/cuda:9.0-devel-ubuntu16.04',
                    _as='devel')

# Install compilers (upstream)
Stage0 += gnu()

# Build FFTW using all default options
Stage0 += fftw()

######
# Runtime stage
######

# Runtime stage base image
Stage1 += baseimage(image='nvcr.io/nvidia/cuda:9.0-runtime-ubuntu16.04')

# Copy the compiler runtime and FFTW from the devel stage and setup the
# runtime environment.
# The _from option is not necessary, but increases clarity.
Stage1 += Stage0.runtime(_from='devel')

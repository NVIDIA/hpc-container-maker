"""
Julia 1.1.0 with GPU support
"""

Stage0 += baseimage(image='nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04')

# The latest CUDAnative package (v2.2.0) does not pass its self tests.
# Manually specify the list of JuliaGPU packages to use 2.1.3 instead.
Stage0 += julia(depot='~/.julia-ngc', ldconfig=True,
                packages=['PackageSpec(name="CUDAnative", rev="v2.1.3")',
                          'CuArrays', 'GPUArrays'],
                version='1.1.0')

Stage0 += copy(src='examples', dest='/workspace/examples', _mkdir=True)

Stage0 += copy(src='entrypoint.sh', dest='/usr/local/bin/entrypoint.sh')
Stage0 += runscript(commands=['/usr/local/bin/entrypoint.sh'])

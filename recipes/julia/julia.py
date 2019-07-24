"""
Julia with GPU support
"""

Stage0 += baseimage(image='nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04')

# Pin the version of each package for a reproducible container image build.
Stage0 += julia(depot='~/.julia-ngc', ldconfig=True,
                packages=['PackageSpec(name="CUDAnative", rev="v2.1.3")',
                          'PackageSpec(name="CuArrays", rev="v1.0.2")',
                          'PackageSpec(name="GPUArrays", rev="v0.7.2")'],
                version='1.1.1')

Stage0 += copy(src='examples', dest='/workspace/examples', _mkdir=True)

Stage0 += copy(src='entrypoint.sh', dest='/usr/local/bin/entrypoint.sh')
Stage0 += runscript(commands=['/usr/local/bin/entrypoint.sh'])

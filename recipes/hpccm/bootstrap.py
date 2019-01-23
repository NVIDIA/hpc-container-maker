"""
Recipe for a HPC Container Maker (HPCCM) container image

Docker:
$ sudo docker build -t hpccm -f Dockerfile .
$ sudo docker run --rm -v $(pwd):/recipes hpccm --recipe /recipes/...

Singularity:
$ sudo singularity build hpccm.simg Singularity.def
$ ./hpccm.simg --recipe ...
"""
from hpccm.common import container_type

Stage0 += comment(__doc__, reformat=False)

Stage0 += baseimage(image='python:3-slim', _distro='ubuntu', _docker_env=False)

Stage0 += shell(commands=['pip install --no-cache-dir hpccm'], chdir=False)

if hpccm.config.g_ctype == container_type.DOCKER:
  # Docker automatically passes through command line arguments
  Stage0 += runscript(commands=['hpccm'])
elif hpccm.config.g_ctype == container_type.SINGULARITY:
  # Singularity does not automatically pass through command line arguments
  Stage0 += runscript(commands=['hpccm $@'])

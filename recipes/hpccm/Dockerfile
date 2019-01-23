# 
# Recipe to bootstrap HPC Container Maker (HPCCM) as a container
# 
# Docker:
# $ sudo docker build -t hpccm -f Dockerfile .
# $ sudo docker run --rm -v $(pwd):/recipes hpccm --recipe /recipes/...
# 
# Singularity:
# $ sudo singularity build hpccm.simg Singularity.def
# $ singularity exec hpccm.simg --recipe ...
# 

FROM python:3-slim

RUN pip install --no-cache-dir hpccm

ENTRYPOINT ["hpccm"]



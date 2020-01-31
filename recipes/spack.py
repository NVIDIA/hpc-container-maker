"""Spack container (https://github.com/spack/spack)
   Set the user argument 'package' to specify the Spack package to
   install.  Otherwise, it will just build a base Spack container
   image.

   Sample workflow:
$ hpccm.py --recipe recipes/spack.py --userarg package="gromacs@2018.2 +cuda" > Dockerfile.gromacs.spack
$ docker build -t gromacs.spack -f Dockerfile.gromacs.spack .
$ nvidia-docker run --rm -ti gromacs.spack bash -l
container:/> spack load gromacs
"""
# pylint: disable=invalid-name, undefined-variable, used-before-assignment
from hpccm.templates.git import git

spack_branch = 'master'

Stage0 += comment(__doc__, reformat=False)

Stage0 += baseimage(image='ubuntu:16.04')

# Base dependencies
Stage0 += python()
Stage0 += gnu()

# Additional dependencies
ospackages = ['autoconf', 'build-essential', 'bzip2', 'ca-certificates',
              'coreutils', 'curl', 'environment-modules', 'git', 'gzip',
              'libssl-dev', 'make', 'openssh-client', 'patch', 'pkg-config',
              'tcl', 'tar', 'unzip', 'zlib1g']
Stage0 += apt_get(ospackages=ospackages)

# Setup and install Spack
Stage0 += shell(commands=[
    git().clone_step(repository='https://github.com/spack/spack',
                     branch=spack_branch, path='/opt'),
    '/opt/spack/bin/spack bootstrap',
    'ln -s /opt/spack/share/spack/setup-env.sh /etc/profile.d/spack.sh',
    'ln -s /opt/spack/share/spack/spack-completion.bash /etc/profile.d'])
Stage0 += environment(variables={'PATH': '/opt/spack/bin:$PATH',
                                 'FORCE_UNSAFE_CONFIGURE': '1'})

spack_package = USERARG.get('package', None)
if spack_package:
     Stage0 += shell(commands=['spack install {}'.format(spack_package),
                               'spack clean --all'])

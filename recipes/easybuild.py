"""EasyBuild container (https://github.com/easybuilders/easybuild)
   Set the user argument 'easyconfig' to specify the EasyConfig to
   build.  Otherwise, it will just build a base EasyBuild container
   image.

   Sample workflow:
$ hpccm.py --recipe recipes/easybuild.py --userarg easyconfig=GROMACS-2016.3-foss-2016b-GPU-enabled.eb > Dockerfile.gromacs.eb
$ docker build -t gromacs.eb -f Dockerfile.gromacs.eb .
$ nvidia-docker run --rm -ti gromacs.eb bash -l
container:/tmp> module load GROMACS
...
"""
# pylint: disable=invalid-name, undefined-variable, used-before-assignment
import os

Stage0 += comment(__doc__, reformat=False)

Stage0.baseimage('ubuntu:16.04')

# Base dependencies
Stage0 += python()
Stage0 += gnu()
Stage0 += ofed()

# Additional dependencies
ospackages = ['build-essential', 'bzip2', 'file', 'git', 'gzip',
              'libssl-dev', 'libtool', 'lmod', 'make', 'openssh-client',
              'patch', 'python-pip', 'python-setuptools', 'rsh-client',
              'tar', 'wget', 'unzip', 'xz-utils']
Stage0 += apt_get(ospackages=ospackages)

# lmod setup
Stage0 += shell(commands=[
    'ln -s /usr/share/lmod/lmod/init/profile /etc/profile.d/lmod.sh'])

# Setup and install EasyBuild
Stage0 += shell(commands=['useradd -m easybuild',
                          'mkdir -p /opt/easybuild',
                          'chown easybuild:easybuild /opt/easybuild',
                          'easy_install easybuild==3.6.2'])

Stage0 += environment(variables={'MODULEPATH': '/opt/easybuild/modules/all:/home/easybuild/.local/easybuild/modules/all:$MODULEPATH'})

easyconfig = USERARG.get('easyconfig', None)
if easyconfig:
     # If the easyconfig is a file in the local build context, inject it
     # into the container image
     if os.path.isfile(easyconfig):
          Stage0 += copy(src=easyconfig, dest='/home/easybuild')

     Stage0 += shell(commands=['runuser easybuild -l -c "eb {} -r --installpath /opt/easybuild"'.format(easyconfig)])

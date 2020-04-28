"""EasyBuild container (https://github.com/easybuilders/easybuild)
   Set the user argument 'easyconfig' to specify the EasyConfig to
   build.  Otherwise, it will just build a base EasyBuild container
   image.

   Sample workflow:
$ hpccm.py --recipe recipes/easybuild.py --userarg easyconfig=GROMACS-2019.3-fosscuda-2019b.eb > Dockerfile.gromacs.eb
$ docker build -t gromacs.eb -f Dockerfile.gromacs.eb .
$ nvidia-docker run --rm -ti gromacs.eb bash -l
container:/tmp> module load GROMACS
...
"""
# pylint: disable=invalid-name, undefined-variable, used-before-assignment
import os

Stage0 += comment(__doc__, reformat=False)

Stage0.baseimage('centos:8')

Stage0 += shell(commands=['yum update -y centos-release',
                          'rm -rf /var/cache/yum/*'])

# Base dependencies
Stage0 += python(python3=False)
Stage0 += gnu()
Stage0 += ofed()
Stage0 += packages(epel=True, powertools=True,
                   yum=['bzip2', 'diffutils', 'file', 'git', 'gzip',
                        'libtool', 'Lmod', 'make', 'openssh-clients',
                        'openssl-devel', 'patch', 'rsh', 'tar', 'unzip',
                        'which', 'xz'])

# Setup and install EasyBuild
Stage0 += pip(packages=['easybuild'], pip='pip2')
Stage0 += shell(commands=['useradd -m easybuild',
                          'mkdir -p /opt/easybuild',
                          'chown easybuild:easybuild /opt/easybuild'])

# Module environment
Stage0 += environment(variables={'MODULEPATH': '/opt/easybuild/modules/all:/home/easybuild/.local/easybuild/modules/all:$MODULEPATH'})

easyconfig = USERARG.get('easyconfig', None)
if easyconfig:
     # If the easyconfig is a file in the local build context, inject it
     # into the container image
     if os.path.isfile(easyconfig):
          Stage0 += copy(src=easyconfig, dest='/home/easybuild')

     Stage0 += shell(commands=['runuser easybuild -l -c "eb {} -r --installpath /opt/easybuild"'.format(easyconfig)])

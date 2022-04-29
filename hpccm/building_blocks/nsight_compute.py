# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=invalid-name, too-few-public-methods
# pylint: disable=too-many-instance-attributes

"""NVIDIA Nsight Compute building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
import os

from distutils.version import StrictVersion
import posixpath

import hpccm.config
import hpccm.templates.envvars

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.building_blocks.generic_build import generic_build
from hpccm.common import cpu_arch, linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.environment import environment

class nsight_compute(bb_base, hpccm.templates.envvars):
    """The `nsight_compute` building block downloads and installs the
    [NVIDIA Nsight Compute
    profiler]](https://developer.nvidia.com/nsight-compute).

    # Parameters

    eula: Required, by setting this value to `True`, you agree to the
    Nsight Compute End User License Agreement that is displayed when
    running the installer interactively.  The default value is
    `False`.

    ospackages: List of OS packages to install prior to building.
    When using a runfile, the default values are `perl` for Ubuntu and
    `perl` and `perl-Env` for RHEL-based Linux distributions.
    Otherwise, the default values are `apt-transport-https`,
    `ca-certificates`, `gnupg`, and `wget` for Ubuntu and an empty
    list for RHEL-based Linux distributions.

    prefix: The top level install prefix. The default value is
    `/usr/local/NVIDIA-Nsight-Compute`.  This parameter is ignored
    unless `runfile` is set.

    runfile: Path or URL to NSight Compute's `.run` file relative to the
    local build context. The default value is empty.

    version: the version of Nsight Compute to install.  Note when
    `runfile` is set this parameter is ignored.  The default value is
    `2022.1.1`.

    # Examples

    ```python
    nsight_compute(version='2020.2.1')
    ```

    ```python
    nsight_compute(eula=True, runfile='nsight-compute-linux-2020.2.0.18-28964561.run')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(nsight_compute, self).__init__(**kwargs)

        self.__arch_label = ''   # Filled in __cpu_arch
        self.__distro_label = ''     # Filled in by __distro
        self.__eula = kwargs.get('eula', False)
        self.__ospackages = kwargs.get('ospackages', [])
        self.__prefix = kwargs.get('prefix',
                                   '/usr/local/NVIDIA-Nsight-Compute')
        self.__runfile = kwargs.get('runfile', None)
        self.__version = kwargs.get('version', '2022.1.1')
        self.__wd = kwargs.get('wd', posixpath.join(
            hpccm.config.g_wd, 'nsight_compute')) # working directory

        # Set the Linux distribution specific parameters
        self.__distro()

        # Disables deployment of section files to prevent warning
        # when there is no home or home is read-only:
        self.environment_variables[
            'NV_COMPUTE_PROFILER_DISABLE_STOCK_FILE_DEPLOYMENT'
        ] = '1'

        if self.__runfile:
            # Runfile based installation
            if not self.__eula:
                raise RuntimeError('Nsight Compute EULA was not accepted.')

            self.__instructions_runfile()

        else:
            # Package repository based installation

            # Set the CPU architecture specific parameters
            self.__cpu_arch()

            # Fill in container instructions
            self.__instructions_repository()

    def __cpu_arch(self):
        """Based on the CPU architecture, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_cpu_arch == cpu_arch.AARCH64:
            self.__arch_label = 'arm64'
        elif hpccm.config.g_cpu_arch == cpu_arch.PPC64LE:
            if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
                self.__arch_label = 'ppc64el'
            else:
                self.__arch_label = 'ppc64le'
        elif hpccm.config.g_cpu_arch == cpu_arch.X86_64:
            if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
                self.__arch_label = 'amd64'
            else:
                self.__arch_label = 'x86_64'
        else: # pragma: no cover
            raise RuntimeError('Unknown CPU architecture')

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                if self.__runfile:
                    self.__ospackages = ['perl', 'wget']
                else:
                    self.__ospackages = ['apt-transport-https',
                                         'ca-certificates', 'gnupg', 'wget']

            if hpccm.config.g_linux_version >= StrictVersion('20.04'):
                self.__distro_label = 'ubuntu2004'
            elif hpccm.config.g_linux_version >= StrictVersion('18.0'):
                self.__distro_label = 'ubuntu1804'
            else:
                self.__distro_label = 'ubuntu1604'

        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                if self.__runfile:
                    self.__ospackages = ['perl', 'perl-Env', 'wget']

            if hpccm.config.g_linux_version >= StrictVersion('8.0'):
                self.__distro_label = 'rhel8'
            else:
                self.__distro_label = 'rhel7'

        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __instructions_repository(self):
        """Fill in container instructions"""

        self += comment('NVIDIA Nsight Compute {}'.format(self.__version))

        if self.__ospackages:
            self += packages(ospackages=self.__ospackages)

        self += packages(
            apt_keys=['https://developer.download.nvidia.com/devtools/repos/{0}/{1}/nvidia.pub'.format(self.__distro_label, self.__arch_label)],
            apt_repositories=['deb https://developer.download.nvidia.com/devtools/repos/{0}/{1}/ /'.format(self.__distro_label, self.__arch_label)],
            # https://github.com/NVIDIA/hpc-container-maker/issues/367
            force_add_repo=True,
            ospackages=['nsight-compute-{}'.format(self.__version)],
            yum_keys=['https://developer.download.nvidia.com/devtools/repos/{0}/{1}/nvidia.pub'.format(self.__distro_label, self.__arch_label)],
            yum_repositories=['https://developer.download.nvidia.com/devtools/repos/{0}/{1}'.format(self.__distro_label, self.__arch_label)])

        # The distro packages do not link nsight-compute binaries to /usr/local/bin
        self.environment_variables['PATH'] = '/opt/nvidia/nsight-compute/{}:$PATH'.format(self.__version)
        self += environment(variables=self.environment_step())

    def __instructions_runfile(self):
        """Fill in container instructions"""

        pkg = os.path.basename(self.__runfile)

        install_cmds = [
            'sh ./{} --nox11 -- -noprompt -targetpath={}'.format(
                pkg, self.__prefix)
        ]

        # Commands needed to predeploy target-specific files. When
        # connecting through the GUI on another machine to the
        # container, this removes the need to copy the files over.
        install_cmds += [
            'mkdir -p /tmp/var/target',
            'ln -sf {}/target/* /tmp/var/target'.format(self.__prefix),
            'ln -sf {}/sections /tmp/var/'.format(self.__prefix),
            'chmod -R a+w /tmp/var'
        ]

        kwargs = {}
        if self.__runfile.strip().startswith(('http://', 'https://')):
            kwargs['url'] = self.__runfile
        else:
            kwargs['package'] = self.__runfile

        self.__bb = generic_build(
            annotations={'runfile': pkg},
            base_annotation=self.__class__.__name__,
            comment = False,
            devel_environment={'PATH': '{}:$PATH'.format(self.__prefix)},
            directory=self.__wd,
            install=install_cmds,
            unpack=False,
            wd=self.__wd,
            **kwargs
        )

        self += comment('NVIDIA Nsight Compute {}'.format(pkg), reformat=False)
        self += packages(ospackages=self.__ospackages)
        self += self.__bb
        self += environment(variables=self.environment_variables)

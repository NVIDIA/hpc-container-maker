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

"""HPC-X building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from packaging.version import Version
import posixpath
import re

import hpccm.config
import hpccm.templates.envvars
import hpccm.templates.ldconfig
import hpccm.templates.rm
import hpccm.templates.tar
import hpccm.templates.wget

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.primitives.environment import environment
from hpccm.primitives.shell import shell
from hpccm.toolchain import toolchain

class hpcx(bb_base, hpccm.templates.envvars, hpccm.templates.ldconfig,
            hpccm.templates.rm, hpccm.templates.tar, hpccm.templates.wget):
    """The `hpcx` building block downloads and installs the [Mellanox
    HPC-X](https://developer.nvidia.com/networking/hpc-x)
    component.

    # Parameters

    buildlabel: The build label assigned by Mellanox to the tarball.
    For versions 2.17 and later, the default value is `cuda12`.
    For version 2.16 the default value is `cuda12-gdrcopy2-nccl2.18`.
    For version 2.15 the default value is `cuda12-gdrcopy2-nccl2.17`.
    For version 2.14 the default value is `cuda11-gdrcopy2-nccl2.16`.
    For versions 2.12 and 2.13 the default value is `cuda11-gdrcopy2-nccl2.12`.
    For versions 2.10 and 2.11 the default value is `cuda11-gdrcopy2-nccl2.11`.
    This value is ignored for HPC-X version 2.9 and earlier.

    environment: Boolean flag to specify whether the environment
    should be modified to include HPC-X. This option is only
    recognized if `hpcxinit` is False. The default is True.

    hpcxinit: Mellanox HPC-X provides an environment script
    (`hpcx-init.sh`) to setup the HPC-X environment.  If this value is
    `True`, the bashrc is modified to automatically source this
    environment script.  However, HPC-X is not automatically available
    to subsequent container image build steps; the environment is
    available when the container image is run.  To set the HPC-X
    environment in subsequent build steps you can explicitly call
    `source /usr/local/hpcx/hpcx-init.sh && hpcx_load` in each build
    step.  If this value is set to `False`, then the environment is
    set such that the environment is visible to both subsequent
    container image build steps and when the container image is run.
    However, the environment may differ slightly from that set by
    `hpcx-init.sh`.  The default value is `True`.

    inbox: Boolean flag to specify whether to use Mellanox HPC-X built
    for Inbox OFED.  If the value is `True`, use Inbox OFED.  If the
    value is `False`, use Mellanox OFED.  The default is `False`.

    ldconfig: Boolean flag to specify whether the Mellanox HPC-X
    library directories should be added dynamic linker cache.  If
    False, then `LD_LIBRARY_PATH` is modified to include the HPC-X
    library directories. This value is ignored if `hpcxinit` is
    `True`. The default value is False.

    mlnx_ofed: The version of Mellanox OFED that should be matched.
    This value is ignored if Inbox OFED is selected, or for HPC-X 2.21
    and later.  The default value is `5` for HPC-X version 2.10 and
    later, and `5.2-2.2.0.0` for earlier HPC-X versions.

    multi_thread: Boolean flag to specify whether the multi-threaded
    version of Mellanox HPC-X should be used.  The default is `False`.

    ofedlabel: The Mellanox OFED label assigned by Mellanox to the
    tarball.  For version 2.21 and later, the default value is
    `gcc-doca_ofed`.  For version 2.16 through 2.18, the default value is
    `gcc-mlnx_ofed`.  For earlier versions, the default value is
    `gcc-MLNX_OFED_LINUX-5`.  This value is ignored if `inbox` is `True`.

    oslabel: The Linux distribution label assigned by Mellanox to the
    tarball.  For Ubuntu, the default value is `ubuntu16.04` for
    Ubuntu 16.04, `ubuntu18.04` for Ubuntu 18.04, `ubuntu20.04` for
    Ubuntu 20.04, and `ubuntu22.04` for Ubuntu 22.04.  For HPC-X
    version 2.10 and later and RHEL-based Linux distributions, the
    default value is `redhat7` for version 7 and `redhat8` for version
    8.  For HPC-X version 2.9 and earlier and RHEL-based Linux
    distributions, the default value is `redhat7.6` for version 7 and
    `redhat8.0` for version 8.

    ospackages: List of OS packages to install prior to installing
    Mellanox HPC-X.  For Ubuntu, the default values are `bzip2`,
    `libnuma1`, `openssh-client`, `tar`, and `wget`.  For RHEL-based
    distributions the default values are `bzip2`, `numactl-libs`,
    `openssh-clients`, `tar`, and `wget`.

    prefix: The top level installation location.  The default value is
    `/usr/local/hpcx`.

    version: The version of Mellanox HPC-X to install.  The default
    value is `2.22.1`.

    # Examples

    ```python
    hpcx(prefix='/usr/local/hpcx', version='2.16')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(hpcx, self).__init__(**kwargs)

        self.__arch = hpccm.config.get_cpu_architecture()
        self.__baseurl = kwargs.get('baseurl',
                                    'https://content.mellanox.com/hpc/hpc-x')
        self.__bashrc = '' # Filled in by __distro()
        self.__buildlabel = kwargs.get('buildlabel', None)
        self.__hpcxinit = kwargs.get('hpcxinit', True)
        self.__inbox = kwargs.get('inbox', False)
        self.__mlnx_ofed = kwargs.get('mlnx_ofed', None)
        self.__multi_thread = kwargs.get('multi_thread', False)
        self.__ofedlabel = kwargs.get('ofedlabel', None)
        self.__oslabel = kwargs.get('oslabel', '') # Filled in by __distro()
        self.__ospackages = kwargs.get('ospackages', []) # Filled in by _distro()
        self.__packages = kwargs.get('packages', [])
        self.__prefix = kwargs.get('prefix', '/usr/local/hpcx')
        self.__version = kwargs.get('version', '2.22.1')

        self.__commands = [] # Filled in by __setup()
        self.__wd = kwargs.get('wd', hpccm.config.g_wd) # working directory

        if not self.__buildlabel:
            if Version(self.__version) >= Version('2.17'):
                self.__buildlabel = 'cuda12'
            elif Version(self.__version) >= Version('2.16'):
                self.__buildlabel = 'cuda12-gdrcopy2-nccl2.18'
            elif Version(self.__version) >= Version('2.15'):
                self.__buildlabel = 'cuda12-gdrcopy2-nccl2.17'
            elif Version(self.__version) >= Version('2.14'):
                self.__buildlabel = 'cuda11-gdrcopy2-nccl2.16'
            elif Version(self.__version) >= Version('2.12'):
                self.__buildlabel = 'cuda11-gdrcopy2-nccl2.12'
            elif Version(self.__version) >= Version('2.10'):
                self.__buildlabel = 'cuda11-gdrcopy2-nccl2.11'

        if not self.__mlnx_ofed:
            if Version(self.__version) >= Version('2.10'):
                self.__mlnx_ofed = '5'
            else:
                self.__mlnx_ofed = '5.2-2.2.0.0'

        if not self.__ofedlabel:
            if Version(self.__version) >= Version('2.21'):
                self.__ofedlabel = 'gcc-doca_ofed'
            elif Version(self.__version) >= Version('2.16'):
                self.__ofedlabel = 'gcc-mlnx_ofed'
            else:
                self.__ofedlabel = 'gcc-MLNX_OFED_LINUX-{}'.format(self.__mlnx_ofed)

        # Output toolchain
        self.toolchain = toolchain(CC='mpicc', CXX='mpicxx', F77='mpif77',
                                   F90='mpif90', FC='mpifort')

        # Set the Linux distribution specific parameters
        self.__distro()

        # Construct the series of steps to execute
        self.__setup()

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        self += comment('Mellanox HPC-X version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += shell(commands=self.__commands)
        self += environment(variables=self.environment_step())

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
           specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__oslabel:
                if hpccm.config.g_linux_version >= Version('24.0'):
                    self.__oslabel = 'ubuntu24.04'
                elif hpccm.config.g_linux_version >= Version('22.0'):
                    self.__oslabel = 'ubuntu22.04'
                elif hpccm.config.g_linux_version >= Version('20.0'):
                    self.__oslabel = 'ubuntu20.04'
                elif hpccm.config.g_linux_version >= Version('18.0'):
                    self.__oslabel = 'ubuntu18.04'
                else:
                    self.__oslabel = 'ubuntu16.04'
            if not self.__ospackages:
                self.__ospackages = ['bzip2', 'libnuma1', 'openssh-client',
                                     'tar', 'wget']

            self.__bashrc = '/etc/bash.bashrc'

        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__oslabel:
                if hpccm.config.g_linux_version >= Version('9.0'):
                    self.__oslabel = 'redhat9'
                elif hpccm.config.g_linux_version >= Version('8.0'):
                    if Version(self.__version) >= Version('2.10'):
                        self.__oslabel = 'redhat8'
                    else:
                        self.__oslabel = 'redhat8.0'
                else:
                    if Version(self.__version) >= Version('2.10'):
                        self.__oslabel = 'redhat7'
                    else:
                        self.__oslabel = 'redhat7.6'
            if not self.__ospackages:
                self.__ospackages = ['bzip2', 'numactl-libs',
                                     'openssh-clients', 'tar', 'wget']

            self.__bashrc = '/etc/bashrc'

        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __setup(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        # For version 2.8 and earlier, the download URL has the format
        # MAJOR.MINOR in the path and the tarball contains
        # MAJOR.MINOR.REVISION, so pull apart the full version to get
        # the individual components.
        version_string = self.__version
        if Version(self.__version) <= Version('2.8'):
            match = re.match(r'(?P<major>\d+)\.(?P<minor>\d+)\.(?P<revision>\d+)',
                             self.__version)
            version_string = '{0}.{1}'.format(match.groupdict()['major'],
                                              match.groupdict()['minor'])

        if self.__inbox:
            # Use inbox OFED
            if Version(self.__version) >= Version('2.10'):
                # Version 2.11 and later include an extra label
                self.__label = 'hpcx-v{0}-gcc-inbox-{1}-{2}-{3}'.format(
                    self.__version, self.__oslabel, self.__buildlabel,
                    self.__arch)
            else:
                self.__label = 'hpcx-v{0}-gcc-inbox-{1}-{2}'.format(
                    self.__version, self.__oslabel, self.__arch)
        else:
            # Use MLNX OFED
            if Version(self.__version) >= Version('2.10'):
                # Version 2.10 and later include an extra label
                self.__label = 'hpcx-v{0}-{1}-{2}-{3}-{4}'.format(
                    self.__version, self.__ofedlabel, self.__oslabel, self.__buildlabel, self.__arch)
            else:
                self.__label = 'hpcx-v{0}-{1}-{2}-{3}'.format(
                    self.__version, self.__ofedlabel, self.__oslabel, self.__arch)

        tarball = self.__label + '.tbz'
        url = '{0}/v{1}/{2}'.format(self.__baseurl, version_string, tarball)

        # Download source from web
        self.__commands.append(self.download_step(url=url, directory=self.__wd))

        # "Install"
        self.__commands.append(self.untar_step(
            tarball=posixpath.join(self.__wd, tarball), directory=self.__wd))
        self.__commands.append('cp -a {0} {1}'.format(
            posixpath.join(self.__wd, self.__label), self.__prefix))

        # Set the environment
        if self.__hpcxinit:
            # Use hpcxinit script
            if self.__multi_thread:
                self.__commands.append('echo "source {0}" >> {1}'.format(
                    posixpath.join(self.__prefix, 'hpcx-mt-init-ompi.sh'),
                    self.__bashrc))
            else:
                self.__commands.append('echo "source {0}" >> {1}'.format(
                    posixpath.join(self.__prefix, 'hpcx-init-ompi.sh'),
                    self.__bashrc))
            self.__commands.append('echo "hpcx_load" >> {0}'.format(
                self.__bashrc))
        else:
            # Set environment manually
            hpcx_dir = self.__prefix
            if self.__multi_thread:
                hpcx_ucx_dir = posixpath.join(hpcx_dir, 'ucx', 'mt')
            else:
                hpcx_ucx_dir = posixpath.join(hpcx_dir, 'ucx')
            hpcx_sharp_dir = posixpath.join(hpcx_dir, 'sharp')
            hpcx_nccl_rdma_sharp_plugin_dir = posixpath.join(
                hpcx_dir, 'nccl_rdma_sharp_plugin')
            hpcx_hcoll_dir = posixpath.join(hpcx_dir, 'hcoll')
            hpcx_mpi_dir = posixpath.join(hpcx_dir, 'ompi')
            hpcx_oshmem_dir = hpcx_mpi_dir
            hpcx_mpi_tests_dir = posixpath.join(hpcx_mpi_dir, 'tests')
            if Version(self.__version) >= Version('2.7'):
                hpcx_osu_dir = posixpath.join(hpcx_mpi_tests_dir,
                                              'osu-micro-benchmarks-5.6.2')
                hpcx_osu_cuda_dir = posixpath.join(
                    hpcx_mpi_tests_dir, 'osu-micro-benchmarks-5.6.2-cuda')
            else:
                hpcx_osu_dir = posixpath.join(hpcx_mpi_tests_dir,
                                              'osu-micro-benchmarks-5.3.2')
                hpcx_osu_cuda_dir = posixpath.join(
                    hpcx_mpi_tests_dir, 'osu-micro-benchmarks-5.3.2-cuda')
            hpcx_ipm_dir = posixpath.join(hpcx_mpi_tests_dir, 'ipm-2.0.6')
            hpcx_ipm_lib = posixpath.join(hpcx_ipm_dir, 'lib', 'libipm.so')
            hpcx_clusterkit_dir = posixpath.join(hpcx_dir, 'clusterkit')

            self.environment_variables = {
                'CPATH': ':'.join([
                    posixpath.join(hpcx_hcoll_dir, 'include'),
                    posixpath.join(hpcx_mpi_dir, 'include'),
                    posixpath.join(hpcx_sharp_dir, 'include'),
                    posixpath.join(hpcx_ucx_dir, 'include'),
                    '$CPATH']),
                'HPCX_CLUSTERKIT_DIR': hpcx_clusterkit_dir,
                'HPCX_DIR': hpcx_dir,
                'HPCX_HCOLL_DIR': hpcx_hcoll_dir,
                'HPCX_IPM_DIR': hpcx_ipm_dir,
                'HPCX_IPM_LIB': hpcx_ipm_lib,
                'HPCX_MPI_DIR': hpcx_mpi_dir,
                'HPCX_MPI_TESTS_DIR': hpcx_mpi_tests_dir,
                'HPCX_NCCL_RDMA_SHARP_PLUGIN_DIR': hpcx_nccl_rdma_sharp_plugin_dir,
                'HPCX_OSHMEM_DIR': hpcx_oshmem_dir,
                'HPCX_OSU_CUDA_DIR': hpcx_osu_cuda_dir,
                'HPCX_OSU_DIR': hpcx_osu_dir,
                'HPCX_SHARP_DIR': hpcx_sharp_dir,
                'HPCX_UCX_DIR': hpcx_ucx_dir,
                'LIBRARY_PATH': ':'.join([
                    posixpath.join(hpcx_hcoll_dir, 'lib'),
                    posixpath.join(hpcx_mpi_dir, 'lib'),
                    posixpath.join(hpcx_nccl_rdma_sharp_plugin_dir, 'lib'),
                    posixpath.join(hpcx_sharp_dir, 'lib'),
                    posixpath.join(hpcx_ucx_dir, 'lib'),
                    '$LIBRARY_PATH']),
                'MPI_HOME': hpcx_mpi_dir,
                'OMPI_HOME': hpcx_mpi_dir,
                'OPAL_PREFIX': hpcx_mpi_dir,
                'OSHMEM_HOME': hpcx_mpi_dir,
                'PATH': ':'.join([
                    posixpath.join(hpcx_clusterkit_dir, 'bin'),
                    posixpath.join(hpcx_hcoll_dir, 'bin'),
                    posixpath.join(hpcx_mpi_dir, 'bin'),
                    posixpath.join(hpcx_ucx_dir, 'bin'),
                    '$PATH']),
                'PKG_CONFIG_PATH': ':'.join([
                    posixpath.join(hpcx_hcoll_dir, 'lib', 'pkgconfig'),
                    posixpath.join(hpcx_mpi_dir, 'lib', 'pkgconfig'),
                    posixpath.join(hpcx_sharp_dir, 'lib', 'pkgconfig'),
                    posixpath.join(hpcx_ucx_dir, 'lib', 'pkgconfig'),
                    '$PKG_CONFIG_PATH']),
                'SHMEM_HOME': hpcx_mpi_dir}

            # Set library path
            if self.ldconfig:
                self.__commands.append(self.ldcache_step(
                    directory=posixpath.join(hpcx_hcoll_dir, 'lib')))
                self.__commands.append(self.ldcache_step(
                    directory=posixpath.join(hpcx_mpi_dir, 'lib')))
                self.__commands.append(self.ldcache_step(
                    directory=posixpath.join(hpcx_nccl_rdma_sharp_plugin_dir,
                                             'lib')))
                self.__commands.append(self.ldcache_step(
                    directory=posixpath.join(hpcx_sharp_dir, 'lib')))
                self.__commands.append(self.ldcache_step(
                    directory=posixpath.join(hpcx_ucx_dir, 'lib')))
                self.__commands.append(self.ldcache_step(
                    directory=posixpath.join(hpcx_ucx_dir, 'lib', 'ucx')))
            else:
                self.environment_variables['LD_LIBRARY_PATH'] = ':'.join([
                    posixpath.join(hpcx_hcoll_dir, 'lib'),
                    posixpath.join(hpcx_mpi_dir, 'lib'),
                    posixpath.join(hpcx_nccl_rdma_sharp_plugin_dir, 'lib'),
                    posixpath.join(hpcx_sharp_dir, 'lib'),
                    posixpath.join(hpcx_ucx_dir, 'lib'),
                    posixpath.join(hpcx_ucx_dir, 'lib', 'ucx'),
                    '$LD_LIBRARY_PATH'])

        # Cleanup tarball and directory
        self.__commands.append(self.cleanup_step(
            items=[posixpath.join(self.__wd, tarball),
                   posixpath.join(self.__wd, self.__label)]))

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        h = hpcx(...)
        Stage0 += h
        Stage1 += h.runtime()
        ```
        """
        return str(self)

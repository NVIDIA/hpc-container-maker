# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
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

"""MVAPICH2 building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import posixpath
import re
from copy import copy as _copy

import hpccm.config
import hpccm.templates.envvars
import hpccm.templates.ldconfig
import hpccm.templates.sed

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.generic_autotools import generic_autotools
from hpccm.building_blocks.packages import packages
from hpccm.common import linux_distro
from hpccm.primitives.comment import comment
from hpccm.toolchain import toolchain

class mvapich2(bb_base, hpccm.templates.envvars, hpccm.templates.ldconfig,
               hpccm.templates.sed):
    """The `mvapich2` building block configures, builds, and installs the
    [MVAPICH2](http://mvapich.cse.ohio-state.edu) component.
    Depending on the parameters, the source will be downloaded from
    the web (default) or copied from a source directory in the local
    build context.

    An InfiniBand building block ([OFED](#ofed) or [Mellanox
    OFED](#mlnx_ofed)) should be installed prior to this building
    block.

    As a side effect, a toolchain is created containing the MPI
    compiler wrappers.  The tool can be passed to other operations
    that want to build using the MPI compiler wrappers.

    # Parameters

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

    check: Boolean flag to specify whether the `make check` step
    should be performed.  The default is False.

    configure_opts: List of options to pass to `configure`.  The
    default values are `--disable-mcast`.

    cuda: Boolean flag to control whether a CUDA aware build is
    performed.  If True, adds `--enable-cuda --with-cuda` to the list
    of `configure` options, otherwise adds `--disable-cuda`.  If the
    toolchain specifies `CUDA_HOME`, then that path is used, otherwise
    `/usr/local/cuda` is used for the path.  The default value is
    True.

    directory: Path to the unpackaged source directory relative to
    the local build context.  The default value is empty.  If this is
    defined, the source in the local build context will be used rather
    than downloading the source from the web.

    disable_FEATURE: Flags to control disabling features when
    configuring.  For instance, `disable_foo=True` maps to
    `--disable-foo`.  Underscores in the parameter name are converted
    to dashes.

    enable_FEATURE[=ARG]: Flags to control enabling features when
    configuring.  For instance, `enable_foo=True` maps to
    `--enable-foo` and `enable_foo='yes'` maps to `--enable-foo=yes`.
    Underscores in the parameter name are converted to dashes.

    environment: Boolean flag to specify whether the environment
    (`LD_LIBRARY_PATH` and `PATH`) should be modified to include
    MVAPICH2. The default is True.

    gpu_arch: The GPU architecture to use.  Older versions of MVAPICH2
    (2.3b and previous) were hard-coded to use "sm_20".  This option
    has no effect on more recent MVAPICH2 versions.  The default value
    is to use the MVAPICH2 default.

    ldconfig: Boolean flag to specify whether the MVAPICH2 library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the MVAPICH2 library
    directory. The default value is False.

    ospackages: List of OS packages to install prior to configuring
    and building.  For Ubuntu, the default values are `byacc`, `file`,
    `make`, `openssh-client`, and `wget`.  For RHEL-based Linux
    distributions, the default values are `byacc`, `file`, `make`,
    `openssh-clients`, and `wget`.

    prefix: The top level install location.  The default value is
    `/usr/local/mvapich2`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default is empty.

    version: The version of MVAPICH2 source to download.  This value
    is ignored if `directory` is set.  The default value is `2.3.3`.

    with_PACKAGE[=ARG]: Flags to control optional packages when
    configuring.  For instance, `with_foo=True` maps to `--with-foo`
    and `with_foo='/usr/local/foo'` maps to
    `--with-foo=/usr/local/foo`.  Underscores in the parameter name
    are converted to dashes.

    without_PACKAGE: Flags to control optional packages when
    configuring.  For instance `without_foo=True` maps to
    `--without-foo`.  Underscores in the parameter name are converted
    to dashes.

    # Examples

    ```python
    mvapich2(cuda=False, prefix='/opt/mvapich2/2.3a', version='2.3a')
    ```

    ```python
    mvapich2(directory='sources/mvapich2-2.3b')
    ```

    ```python
    p = pgi(eula=True)
    mvapich2(toolchain=p.toolchain)
    ```

    ```python
    mvapich2(configure_opts=['--disable-fortran', '--disable-mcast'])
    ```
    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(mvapich2, self).__init__(**kwargs)

        self.__baseurl = kwargs.pop('baseurl',
                                    'http://mvapich.cse.ohio-state.edu/download/mvapich/mv2')
        self.__configure_opts = kwargs.pop('configure_opts', ['--disable-mcast'])
        self.__cuda = kwargs.pop('cuda', True)
        self.__gpu_arch = kwargs.pop('gpu_arch', None)
        self.__ospackages = kwargs.pop('ospackages', [])
        self.__preconfigure = []
        self.__prefix = kwargs.pop('prefix', '/usr/local/mvapich2')
        self.__runtime_ospackages = [] # Filled in by __distro()
        # Input toolchain, i.e., what to use when building
        self.__toolchain = kwargs.pop('toolchain', toolchain())
        self.__version = kwargs.pop('version', '2.3.3')

        # MVAPICH2 does not accept F90
        self.toolchain_control = {'CC': True, 'CXX': True, 'F77': True,
                                  'F90': False, 'FC': True}

        # Output toolchain
        self.toolchain = toolchain(CC='mpicc', CXX='mpicxx', F77='mpif77',
                                   F90='mpif90', FC='mpifort')

        # Set the configure options
        self.__configure()

        # Set the Linux distribution specific parameters
        self.__distro()

        # Setup the environment variables
        # Set library path
        self.environment_variables['PATH'] = '{}:$PATH'.format(
            posixpath.join(self.__prefix, 'bin'))
        self.runtime_environment_variables['PATH'] = '{}:$PATH'.format(
            posixpath.join(self.__prefix, 'bin'))
        if not self.ldconfig:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(posixpath.join(self.__prefix, 'lib'))
            self.runtime_environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(posixpath.join(self.__prefix, 'lib'))
        if self.__cuda:
            # Workaround for using compiler wrappers in the build stage
            self.environment_variables['PROFILE_POSTLIB'] = '"-L{} -lnvidia-ml -lcuda"'.format('/usr/local/cuda/lib64/stubs')

        # Setup build configuration
        self.__bb = generic_autotools(
            annotations={'version': self.__version},
            base_annotation=self.__class__.__name__,
            comment=False,
            configure_opts=self.__configure_opts,
            devel_environment=self.environment_variables,
            preconfigure=self.__preconfigure,
            prefix=self.__prefix,
            runtime_environment=self.runtime_environment_variables,
            toolchain=self.__toolchain,
            url='{0}/mvapich2-{1}.tar.gz'.format(self.__baseurl,
                                                 self.__version),
            **kwargs)

        # Container instructions
        self += comment('MVAPICH2 version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += self.__bb

    def __distro(self):
        """Based on the Linux distribution, set values accordingly.  A user
        specified value overrides any defaults."""

        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if not self.__ospackages:
                self.__ospackages = ['byacc', 'file', 'make',
                                     'openssh-client', 'wget']
            self.__runtime_ospackages = ['openssh-client']
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if not self.__ospackages:
                self.__ospackages = ['byacc', 'file', 'make',
                                     'openssh-clients', 'wget']
            self.__runtime_ospackages = ['openssh-clients']
        else: # pragma: no cover
            raise RuntimeError('Unknown Linux distribution')

    def __set_gpu_arch(self):
        """Older versions of MVAPICH2 (2.3b and previous) were hard-coded to
        use the "sm_20" GPU architecture.  Use the specified value
        instead."""

    def __configure(self):
        """Construct the series of shell commands, i.e., fill in
           self.__commands"""

        # Create a copy of the toolchain so that it can be modified
        # without impacting the original.
        self.__toolchain = _copy(self.__toolchain)

        # MVAPICH2 does not accept F90
        self.__toolchain.F90 = ''

        # CUDA
        if self.__cuda:
            cuda_home = "/usr/local/cuda"
            if self.__toolchain.CUDA_HOME:
                cuda_home = toolchain.CUDA_HOME

            # The PGI compiler needs some special handling for CUDA.
            # http://mvapich.cse.ohio-state.edu/static/media/mvapich/mvapich2-2.0-userguide.html#x1-120004.5
            if self.__toolchain.CC and re.match('.*pgcc', self.__toolchain.CC):
                self.__configure_opts.append(
                    '--enable-cuda=basic --with-cuda={}'.format(cuda_home))

                # Work around issue when using PGI 19.4
                self.__configure_opts.append('--enable-fast=O1')

                if not self.__toolchain.CFLAGS:
                    self.__toolchain.CFLAGS = '-ta=tesla:nordc'

                if not self.__toolchain.CPPFLAGS:
                    self.__toolchain.CPPFLAGS = '-D__x86_64 -D__align__\(n\)=__attribute__\(\(aligned\(n\)\)\) -D__location__\(a\)=__annotate__\(a\) -DCUDARTAPI='

                if not self.__toolchain.LD_LIBRARY_PATH:
                    self.__toolchain.LD_LIBRARY_PATH = posixpath.join(
                        cuda_home, 'lib64', 'stubs') + ':$LD_LIBRARY_PATH'
            else:
                if not self.__toolchain.LD_LIBRARY_PATH:
                    self.__toolchain.LD_LIBRARY_PATH = posixpath.join(
                        cuda_home, 'lib64', 'stubs') + ':$LD_LIBRARY_PATH'
                self.__configure_opts.append(
                    '--enable-cuda --with-cuda={}'.format(cuda_home))

            # Workaround for using compiler wrappers in the build stage
            self.__preconfigure.append('ln -s {0} {1}'.format(
                posixpath.join(cuda_home, 'lib64', 'stubs', 'libnvidia-ml.so'),
                posixpath.join(cuda_home, 'lib64', 'stubs',
                               'libnvidia-ml.so.1')))
            self.__preconfigure.append('ln -s {0} {1}'.format(
                posixpath.join(cuda_home, 'lib64', 'stubs', 'libcuda.so'),
                posixpath.join(cuda_home, 'lib64', 'stubs', 'libcuda.so.1')))

            # Older versions of MVAPICH2 (2.3b and previous) were
            # hard-coded to use the "sm_20" GPU architecture.  Use the
            # specified value instead.
            if self.__gpu_arch:
                self.__preconfigure.append(
                    self.sed_step(file='Makefile.in',
                                  patterns=[r's/-arch sm_20/-arch {}/g'.format(self.__gpu_arch)]))

        else:
            self.__configure_opts.append('--disable-cuda')

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        m = mvapich2(...)
        Stage0 += m
        Stage1 += m.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('MVAPICH2'))
        # TODO: move the definition of runtime ospackages
        instructions.append(packages(ospackages=self.__runtime_ospackages))
        instructions.append(self.__bb.runtime(_from=_from))
        return '\n'.join(str(x) for x in instructions)

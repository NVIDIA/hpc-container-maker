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

"""FFTW building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import posixpath

import hpccm.config
import hpccm.templates.envvars
import hpccm.templates.ldconfig

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.generic_autotools import generic_autotools
from hpccm.building_blocks.packages import packages
from hpccm.common import cpu_arch
from hpccm.primitives.comment import comment

class fftw(bb_base, hpccm.templates.envvars, hpccm.templates.ldconfig):
    """The `fftw` building block downloads, configures, builds, and
    installs the [FFTW](http://www.fftw.org) component.  Depending on
    the parameters, the source will be downloaded from the web
    (default) or copied from a source directory in the local build
    context.

    # Parameters

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

    check: Boolean flag to specify whether the `make check` step
    should be performed.  The default is False.

    configure_opts: List of options to pass to `configure`.  For
    x86_64 processors, the default values are `--enable-shared`,
    `--enable-openmp`, `--enable-threads`, and `--enable-sse2`.  For
    other processors, the default values are `--enable-shared`,
    `--enable-openmp`, and `--enable-threads`.

    directory: Path to the unpackaged source directory relative to the
    local build context.  The default value is empty.  If this is
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
    (`LD_LIBRARY_PATH`) should be modified to include FFTW. The
    default is True.

    ldconfig: Boolean flag to specify whether the FFTW library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the FFTW library
    directory. The default value is False.

    mpi: Boolean flag to specify whether to build with MPI support
    enabled.  The default is False.

    ospackages: List of OS packages to install prior to configuring
    and building.  The default values are `file`, `make`, and `wget`.

    prefix: The top level install location.  The default value is
    `/usr/local/fftw`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default is empty.

    version: The version of FFTW source to download.  This value is
    ignored if `directory` is set.  The default value is `3.3.8`.

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
    fftw(prefix='/opt/fftw/3.3.7', version='3.3.7')
    ```

    ```python
    fftw(directory='sources/fftw-3.3.7')
    ```

    ```python
    p = pgi(eula=True)
    fftw(toolchain=p.toolchain)
    ```

    ```python
    fftw(check=True, configure_opts=['--enable-shared', '--enable-threads',
                                     '--enable-sse2', '--enable-avx'])
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(fftw, self).__init__(**kwargs)

        self.__baseurl = kwargs.pop('baseurl', 'ftp://ftp.fftw.org/pub/fftw')
        self.__check = kwargs.pop('check', False)
        self.__configure_opts = kwargs.pop('configure_opts', [])
        self.__directory = kwargs.pop('directory', '')
        self.__mpi = kwargs.pop('mpi', False)
        self.__ospackages = kwargs.pop('ospackages', ['file', 'make', 'wget'])
        self.__prefix = kwargs.pop('prefix', '/usr/local/fftw')
        self.__version = kwargs.pop('version', '3.3.8')

        # Set the configure options
        self.__configure()

        # Set the environment variables
        if not self.ldconfig:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(posixpath.join(self.__prefix, 'lib'))

        # Setup build configuration
        self.__bb = generic_autotools(
            annotations={'version': self.__version},
            base_annotation=self.__class__.__name__,
            check=self.__check,
            configure_opts=self.__configure_opts,
            comment=False,
            devel_environment=self.environment_variables,
            # PGI compiler needs a larger stack size
            postconfigure=['ulimit -s unlimited'] if self.__check else None,
            prefix=self.__prefix,
            runtime_environment=self.environment_variables,
            url='{0}/fftw-{1}.tar.gz'.format(self.__baseurl, self.__version),
            **kwargs)

        # Container instructions
        self += comment('FFTW version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += self.__bb

    def __configure(self):
        """Setup configure options based on user parameters and CPU
           architecture"""

        if hpccm.config.g_cpu_arch == cpu_arch.X86_64:
            if not self.__configure_opts:
                self.__configure_opts = ['--enable-shared', '--enable-openmp',
                                         '--enable-threads', '--enable-sse2']
        else:
            if not self.__configure_opts:
                self.__configure_opts = ['--enable-shared', '--enable-openmp',
                                       '--enable-threads']

        if self.__mpi:
            self.__configure_opts.append('--enable-mpi')

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        f = fftw(...)
        Stage0 += f
        Stage1 += f.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('FFTW'))
        instructions.append(self.__bb.runtime(_from=_from))
        return '\n'.join(str(x) for x in instructions)

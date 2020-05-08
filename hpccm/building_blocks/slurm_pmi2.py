# Copyright (c) 2019, NVIDIA CORPORATION.  All rights reserved.
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

"""SLURM PMI2 building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import posixpath

import hpccm.templates.envvars
import hpccm.templates.ldconfig

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.generic_autotools import generic_autotools
from hpccm.building_blocks.packages import packages
from hpccm.primitives.comment import comment

class slurm_pmi2(bb_base, hpccm.templates.envvars, hpccm.templates.ldconfig):
    """The `slurm_pmi2` building block configures, builds, and installs
    the PMI2 component from SLURM.

    Note: this building block does not install SLURM itself.

    # Parameters

    annotate: Boolean flag to specify whether to include annotations
    (labels).  The default is False.

    configure_opts: List of options to pass to `configure`.  The
    default is an empty list.

    disable_FEATURE: Flags to control disabling features when
    configuring.  For instance, `disable_foo=True` maps to
    `--disable-foo`.  Underscores in the parameter name are converted
    to dashes.

    enable_FEATURE[=ARG]: Flags to control enabling features when
    configuring.  For instance, `enable_foo=True` maps to
    `--enable-foo` and `enable_foo='yes'` maps to `--enable-foo=yes`.
    Underscores in the parameter name are converted to dashes.

    environment: Boolean flag to specify whether the environment
    (`CPATH` and `LD_LIBRARY_PATH`) should be modified to include
    PMI2. The default is False.

    ldconfig: Boolean flag to specify whether the PMI2 library
    directory should be added dynamic linker cache.  If False, then
    `LD_LIBRARY_PATH` is modified to include the PMI2 library
    directory. The default value is False.

    ospackages: List of OS packages to install prior to configuring
    and building.  The default values are `bzip2`, `file`, `make`,
    `perl`, `tar`, and `wget`.

    prefix: The top level install location.  The default value is
    `/usr/local/slurm-pmi2`.

    toolchain: The toolchain object.  This should be used if
    non-default compilers or other toolchain options are needed.  The
    default value is empty.

    version: The version of SLURM source to download.  The default
    value is `19.05.5`.

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
    slurm_pmi2(prefix='/opt/pmi', version='19.05.4')
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(slurm_pmi2, self).__init__(**kwargs)

        self.__baseurl = kwargs.pop('baseurl', 'https://download.schedmd.com/slurm')
        self.__environment = kwargs.pop('environment', False)
        self.__ospackages = kwargs.pop('ospackages', ['bzip2', 'file', 'make',
                                                      'perl', 'tar', 'wget'])
        self.__prefix = kwargs.pop('prefix', '/usr/local/slurm-pmi2')
        self.__version = kwargs.pop('version', '19.05.5')

        # Setup the environment variables
        self.environment_variables['CPATH'] = '{}:$CPATH'.format(
            posixpath.join(self.__prefix, 'include', 'slurm'))
        if not self.ldconfig:
            self.environment_variables['LD_LIBRARY_PATH'] = '{}:$LD_LIBRARY_PATH'.format(posixpath.join(self.__prefix, 'lib'))

        # Setup build configuration
        self.__bb = generic_autotools(
            annotations={'version': self.__version},
            base_annotation=self.__class__.__name__,
            comment=False,
            devel_environment=self.environment_variables,
            environment=self.__environment,
            install=False,
            make=False,
            postconfigure=['make -C contribs/pmi2 install'],
            prefix=self.__prefix,
            runtime_environment=self.environment_variables,
            url='{0}/slurm-{1}.tar.bz2'.format(self.__baseurl, self.__version),
            **kwargs)

        # Container instructions
        self += comment('SLURM PMI2 version {}'.format(self.__version))
        self += packages(ospackages=self.__ospackages)
        self += self.__bb

    def runtime(self, _from='0'):
        """Generate the set of instructions to install the runtime specific
        components from a build in a previous stage.

        # Examples

        ```python
        p = slurm_pmi2(...)
        Stage0 += p
        Stage1 += p.runtime()
        ```
        """
        instructions = []
        instructions.append(comment('SLURM PMI2'))
        instructions.append(self.__bb.runtime(_from=_from))
        return '\n'.join(str(x) for x in instructions).rstrip()

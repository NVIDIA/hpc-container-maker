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

import hpccm.config

from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.packages import packages
from hpccm.building_blocks.generic_build import generic_build
from hpccm.primitives.comment import comment

class nsight_compute(bb_base):
    """The `nsight_compute` building block installs the
    [NVIDIA Nsight Compute
    profiler]](https://developer.nvidia.com/nsight-compute).

    # Parameters

    eula: Required, by setting this value to `True`, you agree to the Nsight Compute End User License Agreement 
    that is displayed when running the installer interactively.
    The default value is `False`.

    run_file: Path to NSight Compute's `.run` file to install. The default value is `None`.

    install_path: Path where files are installed. Default is `/usr/local/NVIDIA-Nsight-Compute`.

    ospackages: List of OS packages to install prior to building.  The
    default values is `['perl']`.

    # Examples

    ```python
    nsight_compute(eula=True, run_file='nsight-compute-linux-2020.2.0.18-28964561.run')
    ```
    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(nsight_compute, self).__init__(**kwargs)

        self.__run_file = kwargs.get('run_file', None)
        self.__eula = kwargs.get('eula', False)
        self.__wd = '/var/tmp'
        self.__ospackages = kwargs.pop('ospackages', ['perl'])
        self.__target = kwargs.get('target', '/usr/local/NVIDIA-Nsight-Compute')

        if self.__run_file is None or not self.__run_file.endswith('.run'):
            raise RuntimeError('Nsight Compute\'s block requires a \'`.run` file\' to be specified via the `run_file` argument.')
        if not os.path.exists(self.__run_file):
            raise RuntimeError("Specified Nsight Compute run file path does not exist: `{}`.".format(self.__run_file))
        if not self.__eula:
            raise RuntimeError('Nsight Compute EULA was not accepted. To accept, see the documentation for this building block')

        self.__instructions()

    def __instructions(self):
        """Fill in container instructions"""

        path = self.__run_file
        pkg = os.path.basename(path)

        install_cmds = [
            'sh ./{} --nox11 -- -noprompt -targetpath={}'.format(pkg, self.__target)
        ]

        install_cmds += self._predeploy_target_commands(self.__target)

        self.__bb = generic_build(
            annotations={'file': pkg},
            base_annotation=self.__class__.__name__,
            comment = False,
            package=self.__run_file,
            install=install_cmds,
            directory=self.__wd,
            target=self.__target,
            devel_environment={'PATH': '{}:$PATH'.format(self.__target)},
            unpack=False
        )

        self += comment('NVIDIA Nsight Compute {}'.format(pkg))
        self += packages(ospackages=self.__ospackages)
        self += self.__bb


    def _predeploy_target_commands(self, install_dir):
        """Gets commands needed to predeploy target-specific files

        When connecting through the GUI on another machine to the container, 
        this removes the need to copy the files over."""
        return [
            'mkdir -p /tmp/var/target',
            'ln -sf {}/target/*-x?? /tmp/var/target/'.format(install_dir),
            'ln -sf {}/sections /tmp/var/'.format(install_dir),
            'chmod -R a+w /tmp/var'
        ]

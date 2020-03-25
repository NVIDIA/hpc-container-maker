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

"""packages building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import hpccm.config

from hpccm.building_blocks.apt_get import apt_get
from hpccm.building_blocks.base import bb_base
from hpccm.building_blocks.yum import yum
from hpccm.common import linux_distro

class packages(bb_base):
    """The `packages` building block specifies the set of operating system
    packages to install.  Based on the Linux distribution, the
    building block invokes either `apt-get` (Ubuntu) or `yum`
    (RHEL-based).

    This building block is preferred over directly using the
    [`apt_get`](#apt_get) or [`yum`](#yum) building blocks.

    # Parameters

    apt: A list of Debian packages to install.  The default is an
    empty list.

    aptitude: Boolean flag to specify whether `aptitude` should be
    used instead of `apt-get`.  The default is False.

    apt_keys: A list of GPG keys to add.  The default is an empty
    list.

    apt_ppas: A list of personal package archives to add.  The default
    is an empty list.

    apt_repositories: A list of apt repositories to add.  The default
    is an empty list.

    download: Boolean flag to specify whether to download the deb /
    rpm packages instead of installing them.  The default is False.

    download_directory: The deb package download location. This
    parameter is ignored if `download` is False. The default value is
    `/var/tmp/packages_download`.

    epel: Boolean flag to specify whether to enable the Extra Packages
    for Enterprise Linux (EPEL) repository.  The default is False.
    This parameter is ignored if the Linux distribution is not
    RHEL-based.

    extract: Location where the downloaded packages should be
    extracted. Note, this extracts and does not install the packages,
    i.e., the package manager is bypassed. After the downloaded
    packages are extracted they are deleted. This parameter is ignored
    if `download` is False. If empty, then the downloaded packages are
    not extracted. The default value is an empty string.

    ospackages: A list of packages to install.  The list is used for
    both Ubuntu and RHEL-based Linux distributions, therefore only
    packages with the consistent names across Linux distributions
    should be specified.  This parameter is ignored if `apt` or `yum`
    is specified.  The default value is an empty list.

    powertools: Boolean flag to specify whether to enable the
    PowerTools repository.  The default is False.  This parameter is
    ignored if the Linux distribution is not RHEL-based.

    release_stream: Boolean flag to specify whether to enable the [CentOS release stream](https://wiki.centos.org/Manuals/ReleaseNotes/CentOSStream)
    repository.  The default is False.  This parameter is only
    recognized if the Linux distribution is RHEL-based and the version
    is 8.x.

    scl: Boolean flag to specify whether to enable the Software
    Collections (SCL) repository.  The default is False.  This
    parameter is only recognized if the Linux distribution is
    RHEL-based and the version is 7.x.

    yum: A list of RPM packages to install.  The default value is an
    empty list.

    yum4: Boolean flag to specify whether `yum4` should be used
    instead of `yum`.  The default is False.  This parameter is only
    recognized if the CentOS version is 7.x.

    yum_keys: A list of GPG keys to import.  The default is an empty
    list.

    yum_repositories: A list of yum repositories to add.  The default
    is an empty list.

    # Examples

    ```python
    packages(ospackages=['make', 'wget'])
    ```

    ```python
    packages(apt=['zlib1g-dev'], yum=['zlib-devel'])
    ```

    ```python
    packages(apt=['python3'], yum=['python34'], epel=True)
    ```

    """

    def __init__(self, **kwargs):
        """Initialize building block"""

        super(packages, self).__init__()

        self.__apt = kwargs.get('apt', [])
        self.__apt_keys = kwargs.get('apt_keys', [])
        self.__apt_ppas = kwargs.get('apt_ppas', [])
        self.__apt_repositories = kwargs.get('apt_repositories', [])
        self.__aptitude = kwargs.get('aptitude', False)
        self.__download = kwargs.get('download', False)
        self.__download_directory = kwargs.get('download_directory',
                                               '/var/tmp/packages_download')
        self.__extra_opts = kwargs.get('extra_opts', [])
        self.__extract = kwargs.get('extract', None)
        self.__epel = kwargs.get('epel', False)
        self.__ospackages = kwargs.get('ospackages', [])
        self.__powertools = kwargs.get('powertools', False)
        self.__release_stream = kwargs.get('release_stream', False)
        self.__scl = kwargs.get('scl', False)
        self.__yum = kwargs.get('yum', [])
        self.__yum4 = kwargs.get('yum4', False)
        self.__yum_keys = kwargs.get('yum_keys', [])
        self.__yum_repositories = kwargs.get('yum_repositories', [])

        # Fill in container instructions
        self.__instructions()

    def __instructions(self):
        """String representation of the building block"""
        if hpccm.config.g_linux_distro == linux_distro.UBUNTU:
            if self.__apt:
                ospackages = self.__apt
            else:
                ospackages = self.__ospackages

            self += apt_get(aptitude=self.__aptitude,
                            download=self.__download,
                            download_directory=self.__download_directory,
                            extra_opts=self.__extra_opts,
                            extract=self.__extract,
                            keys=self.__apt_keys,
                            ospackages=ospackages,
                            ppas=self.__apt_ppas,
                            repositories=self.__apt_repositories)
        elif hpccm.config.g_linux_distro == linux_distro.CENTOS:
            if self.__yum:
                ospackages = self.__yum
            else:
                ospackages = self.__ospackages

            self += yum(download=self.__download,
                        download_directory=self.__download_directory,
                        extra_opts=self.__extra_opts,
                        extract=self.__extract,
                        epel=self.__epel,
                        keys=self.__yum_keys,
                        ospackages=ospackages,
                        powertools=self.__powertools,
                        release_stream=self.__release_stream,
                        scl=self.__scl,
                        repositories=self.__yum_repositories,
                        yum4=self.__yum4)
        else:
            raise RuntimeError('Unknown Linux distribution')

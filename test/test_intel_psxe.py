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

# pylint: disable=invalid-name, too-few-public-methods, bad-continuation

"""Test cases for the intel_psxe module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.intel_psxe import intel_psxe

class Test_intel_psxe(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults(self):
        """Default intel_psxe building block, no eula agreement"""
        with self.assertRaises(RuntimeError):
            psxe = intel_psxe()
            str(psxe)

    @ubuntu
    @docker
    def test_license_file(self):
        """intel_psxe building license file"""
        psxe = intel_psxe(eula=True, license='XXXXXXXX.lic', tarball='parallel_studio_xe_2018_update1_professional_edition.tgz')
        self.assertEqual(str(psxe),
r'''# Intel Parallel Studio XE
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        cpio && \
    rm -rf /var/lib/apt/lists/*
COPY parallel_studio_xe_2018_update1_professional_edition.tgz /var/tmp/parallel_studio_xe_2018_update1_professional_edition.tgz
COPY XXXXXXXX.lic /var/tmp/license.lic
RUN mkdir -p /var/tmp && tar -x -f /var/tmp/parallel_studio_xe_2018_update1_professional_edition.tgz -C /var/tmp -z && \
    sed -i -e 's/^#\?\(COMPONENTS\)=.*/\1=intel-icc__x86_64;intel-ifort__x86_64/g' \
        -e 's|^#\?\(PSET_INSTALL_DIR\)=.*|\1=/opt/intel|g' \
        -e 's/^#\?\(ACCEPT_EULA\)=.*/\1=accept/g' \
        -e 's/^#\?\(ACTIVATION_TYPE\)=.*/\1=license_file/g' \
        -e 's|^#\?\(ACTIVATION_LICENSE_FILE\)=.*|\1=/var/tmp/license.lic|g' /var/tmp/parallel_studio_xe_2018_update1_professional_edition/silent.cfg && \
    cd /var/tmp/parallel_studio_xe_2018_update1_professional_edition && ./install.sh --silent=silent.cfg && \
    mkdir -p /var/tmp/intel_psxe_runtime && cp -a /opt/intel/lib/intel64/*.so* /var/tmp/intel_psxe_runtime && \
    rm -rf /var/tmp/parallel_studio_xe_2018_update1_professional_edition.tgz /var/tmp/parallel_studio_xe_2018_update1_professional_edition
ENV LD_LIBRARY_PATH=/opt/intel/lib/intel64:$LD_LIBRARY_PATH \
    PATH=/opt/intel/bin:$PATH''')

    @ubuntu
    @docker
    def test_license_server(self):
        """intel_psxe building license server"""
        psxe = intel_psxe(eula=True, license='12345@server-lic', tarball='parallel_studio_xe_2018_update1_professional_edition.tgz')
        self.assertEqual(str(psxe),
r'''# Intel Parallel Studio XE
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        cpio && \
    rm -rf /var/lib/apt/lists/*
COPY parallel_studio_xe_2018_update1_professional_edition.tgz /var/tmp/parallel_studio_xe_2018_update1_professional_edition.tgz
RUN mkdir -p /var/tmp && tar -x -f /var/tmp/parallel_studio_xe_2018_update1_professional_edition.tgz -C /var/tmp -z && \
    sed -i -e 's/^#\?\(COMPONENTS\)=.*/\1=intel-icc__x86_64;intel-ifort__x86_64/g' \
        -e 's|^#\?\(PSET_INSTALL_DIR\)=.*|\1=/opt/intel|g' \
        -e 's/^#\?\(ACCEPT_EULA\)=.*/\1=accept/g' \
        -e 's/^#\?\(ACTIVATION_TYPE\)=.*/\1=license_server/g' \
        -e 's/^#\?\(ACTIVATION_LICENSE_FILE\)=.*/\1=12345@server-lic/g' /var/tmp/parallel_studio_xe_2018_update1_professional_edition/silent.cfg && \
    cd /var/tmp/parallel_studio_xe_2018_update1_professional_edition && ./install.sh --silent=silent.cfg && \
    mkdir -p /var/tmp/intel_psxe_runtime && cp -a /opt/intel/lib/intel64/*.so* /var/tmp/intel_psxe_runtime && \
    rm -rf /var/tmp/parallel_studio_xe_2018_update1_professional_edition.tgz /var/tmp/parallel_studio_xe_2018_update1_professional_edition
ENV LD_LIBRARY_PATH=/opt/intel/lib/intel64:$LD_LIBRARY_PATH \
    PATH=/opt/intel/bin:$PATH''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        psxe = intel_psxe(eula=True, tarball='parallel_studio_xe_2018_update1_professional_edition.tgz')
        r = psxe.runtime()
        s = '\n'.join(str(x) for x in r)
        self.assertEqual(s,
r'''# Intel Parallel Studio XE
COPY --from=0 /var/tmp/intel_psxe_runtime/* /opt/intel/lib/intel64/
ENV LD_LIBRARY_PATH=/opt/intel/lib/intel64:$LD_LIBRARY_PATH''')

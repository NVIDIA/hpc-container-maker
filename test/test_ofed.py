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

"""Test cases for the ofed module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from hpccm.common import container_type
from hpccm.ofed import ofed

class Test_ofed(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    def test_defaults(self):
        """Default ofed building block"""
        o = ofed()
        self.assertEqual(o.toString(container_type.DOCKER),
r'''# OFED
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        dapl2-utils \
        ibutils \
        ibverbs-utils \
        infiniband-diags \
        libdapl-dev \
        libibcm-dev \
        libibmad5 \
        libibmad-dev \
        libibverbs1 \
        libibverbs-dev \
        libmlx4-1 \
        libmlx4-dev \
        libmlx5-1 \
        libmlx5-dev \
        librdmacm1 \
        librdmacm-dev \
        opensm \
        rdmacm-utils && \
    rm -rf /var/lib/apt/lists/*''')

    def test_runtime(self):
        """Runtime"""
        o = ofed()
        r = o.runtime()
        self.assertEqual(r.toString(container_type.DOCKER),
r'''# OFED
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        dapl2-utils \
        ibutils \
        ibverbs-utils \
        infiniband-diags \
        libdapl-dev \
        libibcm-dev \
        libibmad5 \
        libibmad-dev \
        libibverbs1 \
        libibverbs-dev \
        libmlx4-1 \
        libmlx4-dev \
        libmlx5-1 \
        libmlx5-dev \
        librdmacm1 \
        librdmacm-dev \
        opensm \
        rdmacm-utils && \
    rm -rf /var/lib/apt/lists/*''')

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

# pylint: disable=invalid-name, too-few-public-methods, bad-continuation

"""Test cases for the generic_cmake module"""

from __future__ import unicode_literals
from __future__ import print_function

import logging # pylint: disable=unused-import
import unittest

from helpers import centos, docker, ubuntu

from hpccm.building_blocks.generic_cmake import generic_cmake
from hpccm.toolchain import toolchain

class Test_generic_cmake(unittest.TestCase):
    def setUp(self):
        """Disable logging output messages"""
        logging.disable(logging.ERROR)

    @ubuntu
    @docker
    def test_defaults_ubuntu(self):
        """Default generic_cmake building block"""
        g = generic_cmake(
            cmake_opts=['-D CMAKE_BUILD_TYPE=Release',
                        '-D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda',
                        '-D GMX_BUILD_OWN_FFTW=ON',
                        '-D GMX_GPU=ON',
                        '-D GMX_MPI=OFF',
                        '-D GMX_OPENMP=ON',
                        '-D GMX_PREFER_STATIC_LIBS=ON',
                        '-D MPIEXEC_PREFLAGS=--allow-run-as-root'],
            directory='gromacs-2018.2',
            prefix='/usr/local/gromacs',
            url='https://github.com/gromacs/gromacs/archive/v2018.2.tar.gz')
        self.assertEqual(str(g),
r'''# https://github.com/gromacs/gromacs/archive/v2018.2.tar.gz
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/gromacs/gromacs/archive/v2018.2.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v2018.2.tar.gz -C /var/tmp -z && \
    mkdir -p /var/tmp/gromacs-2018.2/build && cd /var/tmp/gromacs-2018.2/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/gromacs -D CMAKE_BUILD_TYPE=Release -D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda -D GMX_BUILD_OWN_FFTW=ON -D GMX_GPU=ON -D GMX_MPI=OFF -D GMX_OPENMP=ON -D GMX_PREFER_STATIC_LIBS=ON -D MPIEXEC_PREFLAGS=--allow-run-as-root /var/tmp/gromacs-2018.2 && \
    cmake --build /var/tmp/gromacs-2018.2/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/gromacs-2018.2/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/gromacs-2018.2 /var/tmp/v2018.2.tar.gz''')

    @ubuntu
    @docker
    def test_no_url(self):
        """missing url"""
        with self.assertRaises(RuntimeError):
            g = generic_cmake()

    @ubuntu
    @docker
    def test_both_repository_and_url(self):
        """both repository and url"""
        with self.assertRaises(RuntimeError):
            g = generic_cmake(repository='foo', url='bar')

    @ubuntu
    @docker
    def test_invalid_package(self):
        """invalid package url"""
        with self.assertRaises(RuntimeError):
            g = generic_cmake(url='https://foo/bar.sh')

    @ubuntu
    @docker
    def test_package(self):
        """local package"""
        g = generic_cmake(
            cmake_opts=['-D CMAKE_BUILD_TYPE=Release',
                        '-D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda',
                        '-D GMX_BUILD_OWN_FFTW=ON',
                        '-D GMX_GPU=ON',
                        '-D GMX_MPI=OFF',
                        '-D GMX_OPENMP=ON',
                        '-D GMX_PREFER_STATIC_LIBS=ON',
                        '-D MPIEXEC_PREFLAGS=--allow-run-as-root',
                        '-D REGRESSIONTEST_DOWNLOAD=ON'],
            directory='gromacs-2018.2',
            package='gromacs/v2018.2.tar.gz',
            prefix='/usr/local/gromacs')
        self.assertEqual(str(g),
r'''# gromacs/v2018.2.tar.gz
COPY gromacs/v2018.2.tar.gz /var/tmp/v2018.2.tar.gz
RUN mkdir -p /var/tmp && tar -x -f /var/tmp/v2018.2.tar.gz -C /var/tmp -z && \
    mkdir -p /var/tmp/gromacs-2018.2/build && cd /var/tmp/gromacs-2018.2/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/gromacs -D CMAKE_BUILD_TYPE=Release -D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda -D GMX_BUILD_OWN_FFTW=ON -D GMX_GPU=ON -D GMX_MPI=OFF -D GMX_OPENMP=ON -D GMX_PREFER_STATIC_LIBS=ON -D MPIEXEC_PREFLAGS=--allow-run-as-root -D REGRESSIONTEST_DOWNLOAD=ON /var/tmp/gromacs-2018.2 && \
    cmake --build /var/tmp/gromacs-2018.2/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/gromacs-2018.2/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/gromacs-2018.2 /var/tmp/v2018.2.tar.gz''')

    @ubuntu
    @docker
    def test_build_directory(self):
        """build directory option"""
        g = generic_cmake(
            build_directory='/tmp/build',
            directory='spdlog-1.4.2',
            url='https://github.com/gabime/spdlog/archive/v1.4.2.tar.gz')
        self.assertEqual(str(g),
r'''# https://github.com/gabime/spdlog/archive/v1.4.2.tar.gz
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/gabime/spdlog/archive/v1.4.2.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v1.4.2.tar.gz -C /var/tmp -z && \
    mkdir -p /tmp/build && cd /tmp/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local /var/tmp/spdlog-1.4.2 && \
    cmake --build /tmp/build --target all -- -j$(nproc) && \
    cmake --build /tmp/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/spdlog-1.4.2 /var/tmp/v1.4.2.tar.gz /tmp/build''')

    @ubuntu
    @docker
    def test_pre_and_post(self):
        """Preconfigure and postinstall options"""
        g = generic_cmake(
            directory='/var/tmp/spdlog-1.4.2',
            postinstall=['echo "post"'],
            preconfigure=['echo "pre"'],
            prefix='/usr/local/spdlog',
            url='https://github.com/gabime/spdlog/archive/v1.4.2.tar.gz')
        self.assertEqual(str(g),
r'''# https://github.com/gabime/spdlog/archive/v1.4.2.tar.gz
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/gabime/spdlog/archive/v1.4.2.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v1.4.2.tar.gz -C /var/tmp -z && \
    cd /var/tmp/spdlog-1.4.2 && \
    echo "pre" && \
    mkdir -p /var/tmp/spdlog-1.4.2/build && cd /var/tmp/spdlog-1.4.2/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/spdlog /var/tmp/spdlog-1.4.2 && \
    cmake --build /var/tmp/spdlog-1.4.2/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/spdlog-1.4.2/build --target install -- -j$(nproc) && \
    cd /usr/local/spdlog && \
    echo "post" && \
    rm -rf /var/tmp/spdlog-1.4.2 /var/tmp/v1.4.2.tar.gz''')

    @ubuntu
    @docker
    def test_build_environment_and_toolchain(self):
        """build environment and toolchain"""
        tc = toolchain(CC='gcc', CXX='g++', FC='gfortran')
        g = generic_cmake(
            build_environment={'FOO': 'BAR'},
            check=True,
            cmake_opts=['-D CMAKE_BUILD_TYPE=Release',
                        '-D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda',
                        '-D GMX_BUILD_OWN_FFTW=ON',
                        '-D GMX_GPU=ON',
                        '-D GMX_MPI=OFF',
                        '-D GMX_OPENMP=ON',
                        '-D GMX_PREFER_STATIC_LIBS=ON',
                        '-D MPIEXEC_PREFLAGS=--allow-run-as-root',
                        '-D REGRESSIONTEST_DOWNLOAD=ON'],
            directory='gromacs-2018.2',
            prefix='/usr/local/gromacs',
            toolchain=tc,
            url='https://github.com/gromacs/gromacs/archive/v2018.2.tar.gz')
        self.assertEqual(str(g),
r'''# https://github.com/gromacs/gromacs/archive/v2018.2.tar.gz
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/gromacs/gromacs/archive/v2018.2.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v2018.2.tar.gz -C /var/tmp -z && \
    mkdir -p /var/tmp/gromacs-2018.2/build && cd /var/tmp/gromacs-2018.2/build && FOO=BAR CC=gcc CXX=g++ FC=gfortran cmake -DCMAKE_INSTALL_PREFIX=/usr/local/gromacs -D CMAKE_BUILD_TYPE=Release -D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda -D GMX_BUILD_OWN_FFTW=ON -D GMX_GPU=ON -D GMX_MPI=OFF -D GMX_OPENMP=ON -D GMX_PREFER_STATIC_LIBS=ON -D MPIEXEC_PREFLAGS=--allow-run-as-root -D REGRESSIONTEST_DOWNLOAD=ON /var/tmp/gromacs-2018.2 && \
    cmake --build /var/tmp/gromacs-2018.2/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/gromacs-2018.2/build --target check -- -j$(nproc) && \
    cmake --build /var/tmp/gromacs-2018.2/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/gromacs-2018.2 /var/tmp/v2018.2.tar.gz''')

    @ubuntu
    @docker
    def test_ldconfig_and_environment(self):
        """ldconfig and environment"""
        g = generic_cmake(
            devel_environment={'CPATH': '/usr/local/spdlog/include:$CPATH'},
            directory='spdlog-1.4.2',
            ldconfig=True,
            prefix='/usr/local/spdlog',
            runtime_environment={'CPATH': '/usr/local/spdlog/include:$CPATH'},
            url='https://github.com/gabime/spdlog/archive/v1.4.2.tar.gz')
        self.assertEqual(str(g),
r'''# https://github.com/gabime/spdlog/archive/v1.4.2.tar.gz
RUN mkdir -p /var/tmp && wget -q -nc --no-check-certificate -P /var/tmp https://github.com/gabime/spdlog/archive/v1.4.2.tar.gz && \
    mkdir -p /var/tmp && tar -x -f /var/tmp/v1.4.2.tar.gz -C /var/tmp -z && \
    mkdir -p /var/tmp/spdlog-1.4.2/build && cd /var/tmp/spdlog-1.4.2/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/spdlog /var/tmp/spdlog-1.4.2 && \
    cmake --build /var/tmp/spdlog-1.4.2/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/spdlog-1.4.2/build --target install -- -j$(nproc) && \
    echo "/usr/local/spdlog/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig && \
    rm -rf /var/tmp/spdlog-1.4.2 /var/tmp/v1.4.2.tar.gz
ENV CPATH=/usr/local/spdlog/include:$CPATH''')

        r = g.runtime()
        self.assertEqual(r,
r'''# https://github.com/gabime/spdlog/archive/v1.4.2.tar.gz
COPY --from=0 /usr/local/spdlog /usr/local/spdlog
RUN echo "/usr/local/spdlog/lib" >> /etc/ld.so.conf.d/hpccm.conf && ldconfig
ENV CPATH=/usr/local/spdlog/include:$CPATH''')

    @ubuntu
    @docker
    def test_repository(self):
        """test repository option"""
        g = generic_cmake(branch='v0.8.0',
                          cmake_opts=['-D CMAKE_BUILD_TYPE=RELEASE',
                                      '-D QUDA_DIRAC_CLOVER=ON',
                                      '-D QUDA_DIRAC_DOMAIN_WALL=ON',
                                      '-D QUDA_DIRAC_STAGGERED=ON',
                                      '-D QUDA_DIRAC_TWISTED_CLOVER=ON',
                                      '-D QUDA_DIRAC_TWISTED_MASS=ON',
                                      '-D QUDA_DIRAC_WILSON=ON',
                                      '-D QUDA_FORCE_GAUGE=ON',
                                      '-D QUDA_FORCE_HISQ=ON',
                                      '-D QUDA_GPU_ARCH=sm_70',
                                      '-D QUDA_INTERFACE_MILC=ON',
                                      '-D QUDA_INTERFACE_QDP=ON',
                                      '-D QUDA_LINK_HISQ=ON',
                                      '-D QUDA_MPI=ON'],
                          prefix='/usr/local/quda',
                          recursive=True,
                          repository='https://github.com/lattice/quda.git')
        self.assertEqual(str(g),
r'''# https://github.com/lattice/quda.git
RUN mkdir -p /var/tmp && cd /var/tmp && git clone --depth=1 --branch v0.8.0 --recursive https://github.com/lattice/quda.git quda && cd - && \
    mkdir -p /var/tmp/quda/build && cd /var/tmp/quda/build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/quda -D CMAKE_BUILD_TYPE=RELEASE -D QUDA_DIRAC_CLOVER=ON -D QUDA_DIRAC_DOMAIN_WALL=ON -D QUDA_DIRAC_STAGGERED=ON -D QUDA_DIRAC_TWISTED_CLOVER=ON -D QUDA_DIRAC_TWISTED_MASS=ON -D QUDA_DIRAC_WILSON=ON -D QUDA_FORCE_GAUGE=ON -D QUDA_FORCE_HISQ=ON -D QUDA_GPU_ARCH=sm_70 -D QUDA_INTERFACE_MILC=ON -D QUDA_INTERFACE_QDP=ON -D QUDA_LINK_HISQ=ON -D QUDA_MPI=ON /var/tmp/quda && \
    cmake --build /var/tmp/quda/build --target all -- -j$(nproc) && \
    cmake --build /var/tmp/quda/build --target install -- -j$(nproc) && \
    rm -rf /var/tmp/quda''')

    @ubuntu
    @docker
    def test_runtime(self):
        """Runtime"""
        g = generic_cmake(
            cmake_opts=['-D CMAKE_BUILD_TYPE=Release',
                        '-D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda',
                        '-D GMX_BUILD_OWN_FFTW=ON',
                        '-D GMX_GPU=ON',
                        '-D GMX_MPI=OFF',
                        '-D GMX_OPENMP=ON',
                        '-D GMX_PREFER_STATIC_LIBS=ON',
                        '-D MPIEXEC_PREFLAGS=--allow-run-as-root'],
            directory='gromacs-2018.2',
            prefix='/usr/local/gromacs',
            url='https://github.com/gromacs/gromacs/archive/v2018.2.tar.gz')
        r = g.runtime()
        self.assertEqual(r,
r'''# https://github.com/gromacs/gromacs/archive/v2018.2.tar.gz
COPY --from=0 /usr/local/gromacs /usr/local/gromacs''')

    @ubuntu
    @docker
    def test_runtime_annotate(self):
        """Runtime"""
        g = generic_cmake(
            annotate=True,
            base_annotation='gromacs',
            cmake_opts=['-D CMAKE_BUILD_TYPE=Release',
                        '-D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda',
                        '-D GMX_BUILD_OWN_FFTW=ON',
                        '-D GMX_GPU=ON',
                        '-D GMX_MPI=OFF',
                        '-D GMX_OPENMP=ON',
                        '-D GMX_PREFER_STATIC_LIBS=ON',
                        '-D MPIEXEC_PREFLAGS=--allow-run-as-root'],
            directory='gromacs-2018.2',
            prefix='/usr/local/gromacs',
            url='https://github.com/gromacs/gromacs/archive/v2018.2.tar.gz')
        r = g.runtime()
        self.assertEqual(r,
r'''# https://github.com/gromacs/gromacs/archive/v2018.2.tar.gz
COPY --from=0 /usr/local/gromacs /usr/local/gromacs
LABEL hpccm.gromacs.cmake='cmake -DCMAKE_INSTALL_PREFIX=/usr/local/gromacs -D CMAKE_BUILD_TYPE=Release -D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda -D GMX_BUILD_OWN_FFTW=ON -D GMX_GPU=ON -D GMX_MPI=OFF -D GMX_OPENMP=ON -D GMX_PREFER_STATIC_LIBS=ON -D MPIEXEC_PREFLAGS=--allow-run-as-root' \
    hpccm.gromacs.url=https://github.com/gromacs/gromacs/archive/v2018.2.tar.gz''')

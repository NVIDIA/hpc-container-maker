Stage0 += baseimage(image='nvidia/cuda:10.1-devel-ubuntu18.04')
Stage0 += gnu()
Stage0 += apt_get(ospackages=['cmake','wget','unzip'])
Stage0 += kokkos(cmake_opts=['-DCMAKE_CXX_COMPILER=$(pwd)/../bin/nvcc_wrapper',
'-DKokkos_ENABLE_CUDA=ON',
'-DKokkos_ARCH_VOLTA72=ON',
'-DKokkos_ENABLE_TESTS=ON',
'-DKokkos_ENABLE_EXAMPLES=OFF',
'-DCMAKE_VERBOSE_MAKEFILE=ON',
'-DCMAKE_CXX_EXTENSIONS=OFF',
'-DCMAKE_BUILD_TYPE=RELEASE'], 
directory='kokkos-master',
install=True,
prefix='/usr/local/kokkos',
url='https://github.com/kokkos/kokkos/archive/master.tar.gz'
)

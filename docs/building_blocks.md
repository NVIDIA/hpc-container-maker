# arm_allinea_studio
```python
arm_allinea_studio(self, **kwargs)
```
The `arm_allinea_studio` building block downloads and installs the
[Arm Allinea
Studio](https://developer.arm.com/tools-and-software/server-and-hpc/arm-architecture-tools/arm-allinea-studio).

You must agree to the [Arm End User License Agreement](https://developer.arm.com/tools-and-software/server-and-hpc/arm-architecture-tools/arm-allinea-studio/licensing/eula)
to use this building block.

As a side effect, a toolchain is created containing the Arm
Allinea Studio compilers.  The toolchain can be passed to other
operations that want to build using the Arm Allinea Studio
compilers.

__Parameters__


- __armpl_generic_aarch64_only__: Boolean flag to specify whether only
the aarch64-generic version of the Arm Performance Libraries
should be installed.  If False, then all variants of the Arm
Performance Libraries, e.g., Cortex-A72, Generic-SVE,
ThunderX2CN99, and Generic-AArch64 are installed, but note that
this will very significantly increase the size of the container
image. The default is True.

- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH`, `PATH`, and potentially other variables)
should be modified to include Arm Allinea Studio. The default is
True.

- __eula__: By setting this value to `True`, you agree to the [Arm End User License Agreement](https://developer.arm.com/tools-and-software/server-and-hpc/arm-architecture-tools/arm-allinea-studio/licensing/eula).
The default value is `False`.

- __ospackages__: List of OS packages to install prior to installing Arm
Allinea Studio.  For Ubuntu, the default values are `libc6-dev`,
`python`, `tar`, `wget`.  For RHEL-based Linux distributions, the
default values are `glibc-devel`, `tar`, `wget`.

- __prefix__: The top level install prefix.  The default value is
`/opt/arm`.

- __tarball__: Path to the Arm Allinea Studio tarball relative to the
local build context.  The default value is empty.  If this is
defined, the tarball in the local build context will be used
rather than downloading the tarball from the web.

- __version__: The version of Arm Allinea Studio to install.  The
default value is `19.3`.

__Examples__


```python
arm_allinea_studio(eula=True, version='19.3')
```


## runtime
```python
arm_allinea_studio.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
a = arm_allinea_compiler(...)
Stage0 += a
Stage1 += a.runtime()
```

# apt_get
```python
apt_get(self, **kwargs)
```
The `apt_get` building block specifies the set of operating system
packages to install.  This building block should only be used on
images that use the Debian package manager (e.g., Ubuntu).

In most cases, the [`packages` building block](#packages) should be
used instead of `apt_get`.

__Parameters__


- __aptitude__: Boolean flag to specify whether `aptitude` should be
used instead of `apt-get`.  The default is False.

- __download__: Boolean flag to specify whether to download the deb
packages instead of installing them.  The default is False.

- __download_directory__: The deb package download location. This
parameter is ignored if `download` is False. The default value is
`/var/tmp/apt_get_download`.

- __extract__: Location where the downloaded packages should be
extracted. Note, this extracts and does not install the packages,
i.e., the package manager is bypassed. After the downloaded
packages are extracted they are deleted. This parameter is ignored
if `download` is False. If empty, then the downloaded packages are
not extracted. The default value is an empty string.

- __keys__: A list of GPG keys to add.  The default is an empty list.

- __ospackages__: A list of packages to install.  The default is an
empty list.

- __ppas__: A list of personal package archives to add.  The default is
an empty list.

- __repositories__: A list of apt repositories to add.  The default is
an empty list.

__Examples__


```python
apt_get(ospackages=['make', 'wget'])
```


# boost
```python
boost(self, **kwargs)
```
The `boost` building block downloads and installs the
[Boost](https://www.boost.org) component.

__Parameters__


- __bootstrap_opts__: List of options to pass to `bootstrap.sh`.  The
default is an empty list.

- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH`) should be modified to include Boost. The
default is True.

- __ldconfig__: Boolean flag to specify whether the Boost library
directory should be added dynamic linker cache.  If False, then
`LD_LIBRARY_PATH` is modified to include the Boost library
directory. The default value is False.

- __ospackages__: List of OS packages to install prior to building.  For
Ubuntu, the default values are `bzip2`, `libbz2-dev`, `tar`,
`wget`, and `zlib1g-dev`.  For RHEL-based Linux distributions the
default values are `bzip2`, `bzip2-devel`, `tar`, `wget`, `which`,
and `zlib-devel`.

- __prefix__: The top level installation location.  The default value
is `/usr/local/boost`.

- __python__: Boolean flag to specify whether Boost should be built with
Python support.  If enabled, the Python C headers need to be
installed (typically this can be done by adding `python-dev` or
`python-devel` to the list of OS packages).  The default is False.

- __sourceforge__: Boolean flag to specify whether Boost should be
downloaded from SourceForge rather than the current Boost
repository.  For versions of Boost older than 1.63.0, the
SourceForge repository should be used.  The default is False.

- __version__: The version of Boost source to download.  The default
value is `1.70.0`.

__Examples__


```python
boost(prefix='/opt/boost/1.67.0', version='1.67.0')
```

```python
boost(sourceforge=True, version='1.57.0')
```


## runtime
```python
boost.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
b = boost(...)
Stage0 += b
Stage1 += b.runtime()
```

# catalyst
```python
catalyst(self, **kwargs)
```
The `catalyst` building block configures, builds, and installs the
[ParaView Catalyst](https://www.paraview.org/in-situ/) component.

The [CMake](#cmake) building block should be installed prior to
this building block.

A MPI building block should be installed prior to this building
block.

If GPU rendering will be used then a
[cudagl](https://hub.docker.com/r/nvidia/cudagl) base image is
recommended.

__Parameters__


- __cmake_opts__: List of options to pass to `cmake`.  The default is an
empty list.

- __edition__: The Catalyst edition to use. Valid choices are `Base`,
`Base-Essentials`, `Base-Essentials-Extras`,
`Base-Essentials-Extras-Rendering-Base`, `Base-Enable-Python`,
`Base-Enable-Python-Essentials`,
`Base-Enable-Python-Essentials-Extras`, and
`Base-Enable-Python-Essentials-Extras-Rendering-Base`.  If a
Python edition is selected, then the [Python](#python) building
block should be installed with development libraries prior to this
building block. The default value is
`Base-Enable-Python-Essentials-Extras-Rendering-Base`.

- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH` and `PATH`) should be modified to include
ParaView Catalyst. The default is True.

- __ldconfig__: Boolean flag to specify whether the Catalyst library
directory should be added dynamic linker cache.  If False, then
`LD_LIBRARY_PATH` is modified to include the Catalyst library
directory. The default value is False.

- __ospackages__: List of OS packages to install prior to configuring
and building.  For Ubuntu, the default values are `git`, `gzip`,
`make`, `tar`, and `wget`.  If a rendering edition is selected
then `libxau-dev`, `libxext-dev`, `libxt-dev`, `libice-dev`,
`libsm-dev`, `libx11-dev`, `libgl1-mesa-dev` are also included.
For RHEL-based Linux distributions, the default values are `git`,
`gzip`, `make`, `tar`, `wget`, and `which`.  If a rendering
edition is selected then `libX11-devel`, `libXau-devel`,
`libXext-devel`, `libXt-devel`, `libICE-devel`, `libSM-devel`,
`libglvnd-devel`, `mesa-libGL-devel` are also included.

- __prefix__: The top level install location.  The default value is
`/usr/local/catalyst`.

- __toolchain__: The toolchain object.  This should be used if
non-default compilers or other toolchain options are needed.  The
default is empty.

- __version__: The version of Catalyst source to download.  The default
value is `5.6.1`.

__Examples__


```python
catalyst(prefix='/opt/catalyst/5.6.0', version='5.6.0')
```


## runtime
```python
catalyst.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__

```python
c = catalyst(...)
Stage0 += c
Stage1 += c.runtime()
```

# cgns
```python
cgns(self, **kwargs)
```
The `cgns` building block downloads and installs the
[CGNS](https://cgns.github.io/index.html) component.

The [HDF5](#hdf5) building block should be installed prior to this
building block.

__Parameters__


- __check__: Boolean flag to specify whether the test cases should be
run.  The default is False.

- __configure_opts__: List of options to pass to `configure`.  The
default value is `--with-hdf5=/usr/local/hdf5` and `--with-zlib`.

- __prefix__: The top level install location.  The default value is
`/usr/local/cgns`.

- __ospackages__: List of OS packages to install prior to configuring
and building.  For Ubuntu, the default values are `file`, `make`,
`wget`, and `zlib1g-dev`.  For RHEL-based Linux distributions the
default values are `bzip2`, `file`, `make`, `wget` and
`zlib-devel`.

- __toolchain__: The toolchain object.  This should be used if
non-default compilers or other toolchain options are needed.  The
default is empty.

- __version__: The version of CGNS source to download.  The default
value is `3.4.0`.

__Examples__


```python
cgns(prefix='/opt/cgns/3.3.1', version='3.3.1')
```

## runtime
```python
cgns.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Example__


```python
c = cgns(...)
Stage0 += c
Stage1 += c.runtime()
```

# charm
```python
charm(self, **kwargs)
```
The `charm` building block downloads and install the
[Charm++](http://charm.cs.illinois.edu/research/charm) component.

__Parameters__


- __basedir__: List of additional include and library paths for building
Charm++.  The default is an empty list.

- __check__: Boolean flag to specify whether the test cases should be
run.  The default is False.

- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH`, `PATH`, and other variables) should be
modified to include Charm++. The default is True.

- __ldconfig__: Boolean flag to specify whether the Charm++ library
directory should be added dynamic linker cache.  If False, then
`LD_LIBRARY_PATH` is modified to include the Charm++ library
directory. The default value is False.

- __options__: List of additional options to use when building Charm++.
The default values are `--build-shared`, and `--with-production`.

- __ospackages__: List of OS packages to install prior to configuring
and building.  The default values are `autoconf`, `automake`,
`git`, `libtool`, `make`, and `wget`.

- __prefix__: The top level install prefix.  The default value is
`/usr/local`.

- __target__: The target Charm++ framework to build.  The default value
is `charm++`.

- __target_architecture__: The target machine architecture to build.
For x86_64 processors, the default value is
`multicore-linux-x86_64`.  For aarch64 processors, the default
value is `multicore-arm8`.  For ppc64le processors, the default is
`multicore-linux-ppc64le`.

- __version__: The version of Charm++ to download.  The default value is
`6.9.0`.

__Examples__


```python
charm(prefix='/opt', version='6.8.2')
```

```python
charm(target_architecture='mpi-linux-x86_64')
```


## runtime
```python
charm.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Example__


```python
c = charm(...)
Stage0 += c
Stage1 += c.runtime()
```

# cmake
```python
cmake(self, **kwargs)
```
The `cmake` building block downloads and installs the
[CMake](https://cmake.org) component.

__Parameters__


- __bootstrap_opts__: List of options to pass to `bootstrap` when
building from source.  The default is an empty list.

- __eula__: By setting this value to `True`, you agree to the [CMake End-User License Agreement](https://gitlab.kitware.com/cmake/cmake/raw/master/Copyright.txt).
The default value is `False`.

- __ospackages__: List of OS packages to install prior to installing.
The default value is `wget`.

- __prefix__: The top level install location.  The default value is
`/usr/local`.

- __source__: Boolean flag to specify whether to build CMake from
source.  For x86_64 processors, the default is False, i.e., use
the available pre-compiled package.  For all other processors, the
default is True.

- __version__: The version of CMake to download.  The default value is
`3.14.5`.

__Examples__


```python
cmake(eula=True)
```

```python
cmake(eula=True, version='3.10.3')
```


# conda
```python
conda(self, **kwargs)
```
The `conda` building block installs Anaconda.

You must agree to the [Anaconda End User License Agreement](https://docs.anaconda.com/anaconda/eula/) to use this building block.

__Parameters__


- __channels__: List of additional Conda channels to enable.  The
default is an empty list.

- __environment__: Path to the Conda environment file to clone.  The
default value is empty.

- __eula__: By setting this value to `True`, you agree to the [Anaconda End User License Agreement](https://docs.anaconda.com/anaconda/eula/).
The default value is `False`.

- __ospackages__: List of OS packages to install prior to installing
Conda.  The default values are `ca-certificates` and `wget`.

- __packages__: List of Conda packages to install.  The default is an
empty list.

- __prefix__: The top level install location.  The default value is
`/usr/local/anaconda`.

- __python2__: Boolean flag to specify that the Python 2 version of
Anaconda should be installed.  The default is False.

- __version__: The version of Anaconda to download.  The default value
is `4.7.12`.

__Examples__


```python
conda(packages=['numpy'])
```

```python
conda(channels=['conda-forge', 'nvidia'], prefix='/opt/conda')
```

```python
conda(environment='environment.yml')
```


## runtime
```python
conda.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
c = conda(...)
Stage0 += c
Stage1 += c.runtime()
```

# fftw
```python
fftw(self, **kwargs)
```
The `fftw` building block downloads, configures, builds, and
installs the [FFTW](http://www.fftw.org) component.  Depending on
the parameters, the source will be downloaded from the web
(default) or copied from a source directory in the local build
context.

__Parameters__


- __check__: Boolean flag to specify whether the `make check` step
should be performed.  The default is False.

- __configure_opts__: List of options to pass to `configure`.  For
x86_64 processors, the default values are `--enable-shared`,
`--enable-openmp`, `--enable-threads`, and `--enable-sse2`.  For
other processors, the default values are `--enable-shared`,
`--enable-openmp`, and `--enable-threads`.

- __directory__: Path to the unpackaged source directory relative to the
local build context.  The default value is empty.  If this is
defined, the source in the local build context will be used rather
than downloading the source from the web.

- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH`) should be modified to include FFTW. The
default is True.

- __ldconfig__: Boolean flag to specify whether the FFTW library
directory should be added dynamic linker cache.  If False, then
`LD_LIBRARY_PATH` is modified to include the FFTW library
directory. The default value is False.

- __mpi__: Boolean flag to specify whether to build with MPI support
enabled.  The default is False.

- __ospackages__: List of OS packages to install prior to configuring
and building.  The default values are `file`, `make`, and `wget`.

- __prefix__: The top level install location.  The default value is
`/usr/local/fftw`.

- __toolchain__: The toolchain object.  This should be used if
non-default compilers or other toolchain options are needed.  The
default is empty.

- __version__: The version of FFTW source to download.  This value is
ignored if `directory` is set.  The default value is `3.3.8`.

__Examples__


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


## runtime
```python
fftw.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
f = fftw(...)
Stage0 += f
Stage1 += f.runtime()
```

# gdrcopy
```python
gdrcopy(self, **kwargs)
```
The `gdrcopy` building block builds and installs the user space
library from the [gdrcopy](https://github.com/NVIDIA/gdrcopy)
component.

__Parameters__


- __environment__: Boolean flag to specify whether the environment
(`CPATH`, `LIBRARY_PATH`, and `LD_LIBRARY_PATH`) should be
modified to include the gdrcopy. The default is True.

- __ldconfig__: Boolean flag to specify whether the gdrcopy library
directory should be added dynamic linker cache.  If False, then
`LD_LIBRARY_PATH` is modified to include the gdrcopy library
directory. The default value is False.

- __ospackages__: List of OS packages to install prior to building.  The
default values are `make` and `wget`.

- __prefix__: The top level install location.  The default value is
`/usr/local/gdrcopy`.

- __version__: The version of gdrcopy source to download.  The default
value is `1.3`.

__Examples__


```python
gdrcopy(prefix='/opt/gdrcopy/1.3', version='1.3')
```


## runtime
```python
gdrcopy.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
g = gdrcopy(...)
Stage0 += g
Stage1 += g.runtime()
```

# generic_autotools
```python
generic_autotools(self, **kwargs)
```
The `generic_autotools` building block downloads, configures,
builds, and installs a specified GNU Autotools enabled package.

__Parameters__


- __branch__: The git branch to clone.  Only recognized if the
`repository` parameter is specified.  The default is empty, i.e.,
use the default branch for the repository.

- __build_directory__: The location to build the package.  The default
value is the source code location.

- __check__: Boolean flag to specify whether the `make check` step
should be performed.  The default is False.

- __commit__: The git commit to clone.  Only recognized if the
`repository` parameter is specified.  The default is empty, i.e.,
use the latest commit on the default branch for the repository.

- __configure_opts__: List of options to pass to `configure`.  The
default value is an empty list.

- __directory__: The source code location.  The default value is the
basename of the downloaded package.  If the value is not an
absolute path, then the temporary working directory is prepended.

- __install__: Boolean flag to specify whether the `make install` step
should be performed.  The default is True.

- __make__: Boolean flag to specify whether the `make` step should be
performed.  The default is True.

- __postinstall__: List of shell commands to run after running 'make
install'.  The working directory is the install prefix.  The
default is an empty list.

- __preconfigure__: List of shell commands to run prior to running
`configure`.  The working directory is the source code location.
The default is an empty list.

- __prefix__: The top level install location.  The default value is
`/usr/local`. It is highly recommended not use use this default
and instead set the prefix to a package specific directory.

- __recursive__: Initialize and checkout git submodules. `repository` parameter
must be specified. The default is False.

- __repository__: The git repository of the package to build.  One of
this paramter or the `url` parameter must be specified.

- __toolchain__: The toolchain object.  This should be used if
non-default compilers or other toolchain options are needed.  The
default is empty.

- __url__: The URL of the tarball package to build.  One of this
parameter or the `repository` parameter must be specified.

__Examples__


```python
generic_autotools(directory='tcl8.6.9/unix',
                  prefix='/usr/local/tcl',
                  url='https://prdownloads.sourceforge.net/tcl/tcl8.6.9-src.tar.gz')
```

```python
generic_autotools(preconfigure=['./autogen.sh'],
                  prefix='/usr/local/zeromq',
                  repository='https://github.com/zeromq/libzmq.git')
```


## runtime
```python
generic_autotools.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
g = generic_autotools(...)
Stage0 += g
Stage1 += g.runtime()
```

# generic_build
```python
generic_build(self, **kwargs)
```
The `generic_build` building block downloads and builds
a specified package.

__Parameters__


- __build__: List of shell commands to run in order to build the
package.  The working directory is the source directory.  The
default is an empty list.

- __branch__: The git branch to clone.  Only recognized if the
`repository` parameter is specified.  The default is empty, i.e.,
use the default branch for the repository.

- __commit__: The git commit to clone.  Only recognized if the
`repository` parameter is specified.  The default is empty, i.e.,
use the latest commit on the default branch for the repository.

- __directory__: The source code location.  The default value is the
basename of the downloaded package.  If the value is not an
absolute path, then the temporary working directory is prepended.

- __install__: List of shell commands to run in order to install the
package.  The working directory is the source directory.  If
`prefix` is defined, it will be automatically created if the list
is non-empty.  The default is an empty list.

- __prefix__: The top level install location.  The default value is
empty. If defined then the location is copied as part of the
runtime method.

- __recursive__: Initialize and checkout git submodules. `repository` parameter
must be specified. The default is False.

- __repository__: The git repository of the package to build.  One of
this paramter or the `url` parameter must be specified.

- __url__: The URL of the tarball package to build.  One of this
parameter or the `repository` parameter must be specified.

__Examples__


```python
generic_build(build=['make ARCH=sm_70'],
              install=['cp stream /usr/local/bin/cuda-stream'],
              repository='https://github.com/bcumming/cuda-stream')
```


## runtime
```python
generic_build.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
g = generic_build(...)
Stage0 += g
Stage1 += g.runtime()
```

# generic_cmake
```python
generic_cmake(self, **kwargs)
```
The `generic_cmake` building block downloads, configures,
builds, and installs a specified CMake enabled package.

__Parameters__


- __branch__: The git branch to clone.  Only recognized if the
`repository` parameter is specified.  The default is empty, i.e.,
use the default branch for the repository.

- __build_directory__: The location to build the package.  The default
value is a `build` subdirectory in the source code location.

- __check__: Boolean flag to specify whether the `make check` step
should be performed.  The default is False.

- __cmake_opts__: List of options to pass to `cmake`.  The default value
is an empty list.

- __commit__: The git commit to clone.  Only recognized if the
`repository` parameter is specified.  The default is empty, i.e.,
use the latest commit on the default branch for the repository.

- __directory__: The source code location.  The default value is the
basename of the downloaded package.  If the value is not an
absolute path, then the temporary working directory is prepended.

- __install__: Boolean flag to specify whether the `make install` step
should be performed.  The default is True.

- __make__: Boolean flag to specify whether the `make` step should be
performed.  The default is True.

- __postinstall__: List of shell commands to run after running 'make
install'.  The working directory is the install prefix.  The
default is an empty list.

- __preconfigure__: List of shell commands to run prior to running
`cmake`.  The working directory is the source code location.  The
default is an empty list.

- __prefix__: The top level install location.  The default value is
`/usr/local`. It is highly recommended not to use this default and
instead set the prefix to a package specific directory.

- __recursive__: Initialize and checkout git submodules. `repository` parameter
must be specified. The default is False.

- __repository__: The git repository of the package to build.  One of
this paramter or the `url` parameter must be specified.

- __toolchain__: The toolchain object.  This should be used if
non-default compilers or other toolchain options are needed.  The
default is empty.

- __url__: The URL of the tarball package to build.  One of this
parameter or the `repository` parameter must be specified.

__Examples__


```python
generic_cmake(cmake_opts=['-D CMAKE_BUILD_TYPE=Release',
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
```

```python
generic_cmake(branch='v0.8.0',
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
              repository='https://github.com/lattice/quda.git')
```


## runtime
```python
generic_cmake.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
g = generic_cmake(...)
Stage0 += g
Stage1 += g.runtime()
```

# gnu
```python
gnu(self, **kwargs)
```
The `gnu` building block installs the GNU compilers from the
upstream Linux distribution.

As a side effect, a toolchain is created containing the GNU
compilers.  The toolchain can be passed to other operations that
want to build using the GNU compilers.

__Parameters__


- __cc__: Boolean flag to specify whether to install `gcc`.  The default
is True.

- __configure_opts__: List of options to pass to `configure`.  The
default value is `--disable-multilib`. This option is only
recognized if a source build is enabled.

- __cxx__: Boolean flag to specify whether to install `g++`.  The
default is True.

- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH` and `PATH`) should be modified to include
the GNU compiler. The default is True.

- __extra_repository__: Boolean flag to specify whether to enable an
extra package repository containing addition GNU compiler
packages.  For Ubuntu, setting this flag to True enables the
- __`ppa__:ubuntu-toolchain-r/test` repository.  For RHEL-based Linux
distributions, setting this flag to True enables the Software
Collections (SCL) repository.  The default is False.

- __fortran__: Boolean flag to specify whether to install `gfortran`.
The default is True.

- __ldconfig__: Boolean flag to specify whether the GNU library
directory should be added dynamic linker cache.  If False, then
`LD_LIBRARY_PATH` is modified to include the GNU library
directory. The default value is False. This option is only
recognized if a source build is enabled.

- __openacc__: Boolean flag to control whether a OpenACC enabled
compiler is built. If True, adds `--with-cuda-driver` and
`--enable-offload-targets=nvptx-none` to the list of host compiler
`configure` options and also builds the accelerator compiler and
dependencies (`nvptx-tools` and `nvptx-newlib`). The default value
is False. This option is only recognized if a source build is
enabled.

- __ospackages__: List of OS packages to install prior to configuring
and building.  For Ubuntu, the default values are `bzip2`, `file`,
`gcc`, `g++`, `git`, `make`, `perl`, `tar`, `wget`, and
`xz-utils`.  For RHEL-based Linux distributions, the default
values are `bzip2`, `file`, `gcc`, `gcc-c++`, `git`, `make`,
`perl`, `tar`, `wget`, and `xz`. This option is only recognized if
a source build is enabled.

- __prefix__: The top level install location.  The default value is
`/usr/local/gnu`. This option is only recognized if a source build
is enabled.

- __source__: Boolean flag to control whether to build the GNU compilers
from source. The default value is False.

- __version__: The version of the GNU compilers to install.  Note that
the version refers to the Linux distribution packaging, not the
actual compiler version.  For Ubuntu, the version is appended to
the default package name, e.g., `gcc-7`.  For RHEL-based Linux
distributions, the version is inserted into the SCL Developer
Toolset package name, e.g., `devtoolset-7-gcc`.  For RHEL-based
Linux distributions, specifying the version automatically sets
`extra_repository` to True.  If a source build is enabled, the
version is the compiler tarball version on the GNU FTP site and
the version must be specified. The default is an empty value.

__Examples__


```python
gnu()
```

```python
gnu(fortran=False)
```

```python
gnu(extra_repository=True, version='7')
```

```python
gnu(openacc=True, source=True, version='9.1.0')
```

```python
g = gnu()
openmpi(..., toolchain=g.toolchain, ...)
```


## runtime
```python
gnu.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
g = gnu(...)
Stage0 += g
Stage1 += g.runtime()
```

# hdf5
```python
hdf5(self, **kwargs)
```
The `hdf5` building block downloads, configures, builds, and
installs the [HDF5](http://www.hdfgroup.org) component.  Depending
on the parameters, the source will be downloaded from the web
(default) or copied from a source directory in the local build
context.

__Parameters__


- __check__: Boolean flag to specify whether the `make check` step
should be performed.  The default is False.

- __configure_opts__: List of options to pass to `configure`.  The
default values are `--enable-cxx` and `--enable-fortran`.

- __directory__: Path to the unpackaged source directory relative to the
local build context.  The default value is empty.  If this is
defined, the source in the local build context will be used rather
than downloading the source from the web.

- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH`, `PATH`, and others) should be modified to
include HDF5. The default is True.

- __ldconfig__: Boolean flag to specify whether the HDF5 library
directory should be added dynamic linker cache.  If False, then
`LD_LIBRARY_PATH` is modified to include the HDF5 library
directory. The default value is False.

- __ospackages__: List of OS packages to install prior to configuring
and building.  For Ubuntu, the default values are `bzip2`, `file`,
`make`, `wget`, and `zlib1g-dev`.  For RHEL-based Linux
distributions the default values are `bzip2`, `file`, `make`,
`wget` and `zlib-devel`.

- __prefix__: The top level install location.  The default value is
`/usr/local/hdf5`.

- __toolchain__: The toolchain object.  This should be used if
non-default compilers or other toolchain options are needed.  The
default is empty.

- __version__: The version of HDF5 source to download.  This value is
ignored if `directory` is set.  The default value is `1.10.5`.

__Examples__


```python
hdf5(prefix='/opt/hdf5/1.10.1', version='1.10.1')
```

```python
hdf5(directory='sources/hdf5-1.10.1')
```

```python
p = pgi(eula=True)
hdf5(toolchain=p.toolchain)
```

```python
hdf5(check=True, configure_opts=['--enable-cxx', '--enable-fortran',
                                 '--enable-profiling=yes'])
```

## runtime
```python
hdf5.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
h = hdf5(...)
Stage0 += h
Stage1 += h.runtime()
```

# hpcx
```python
hpcx(self, **kwargs)
```
The `hpcx` building block downloads and installs the [Mellanox
HPC-X](https://www.mellanox.com/page/products_dyn?product_family=189&mtag=hpc-x)
component.

__Parameters__


- __hpcxinit__: Mellanox HPC-X provides an environment script
(`hpcx-init.sh`) to setup the HPC-X environment.  If this value is
`True`, the bashrc is modified to automatically source this
environment script.  However, HPC-X is not automatically available
to subsequent container image build steps; the environment is
available when the container image is run.  To set the HPC-X
environment in subsequent build steps you can explicitly call
`source /usr/local/hpcx/hpcx-init.sh && hpcx_init` in each build
step.  If this value is set to `False`, then the environment is
set such that the environment is visible to both subsequent
container image build steps and when the container image is run.
However, the environment may differ slightly from that set by
`hpcx-init.sh`.  The default value is `True`.

- __inbox__: Boolean flag to specify whether to use Mellanox HPC-X built
for Inbox OFED.  If the value is `True`, use Inbox OFED.  If the
value is `False`, use Mellanox OFED.  The default is `False`.

- __ldconfig__: Boolean flag to specify whether the Mellanox HPC-X
library directories should be added dynamic linker cache.  If
False, then `LD_LIBRARY_PATH` is modified to include the HPC-X
library directories. This value is ignored if `hpcxinit` is
`True`. The default value is False.

- __mlnx_ofed__: The version of Mellanox OFED that should be matched.
This value is ignored if Inbox OFED is selected.  The default
value is `4.6-1.0.1.1`.

- __multi_thread__: Boolean flag to specify whether the multi-threaded
version of Mellanox HPC-X should be used.  The default is `False`.

- __oslabel__: The Linux distribution label assigned by Mellanox to the
tarball.  For Ubuntu, the default value is `ubuntu16.04` for
Ubuntu 16.04 and `ubuntu18.04` for Ubuntu 18.04.  For RHEL-based
Linux distributions, the default value is `redhat7.6` for version
7 and `redhat8.0` for version 8.

- __ospackages__: List of OS packages to install prior to installing
Mellanox HPC-X.  For Ubuntu, the default values are `bzip2`,
`openssh-client`, `tar`, and `wget`.  For RHEL-based distributions
the default values are `bzip2`, `openssh-clients`, `tar`, and
`wget`.

- __prefix__: The top level installation location.  The default value is
`/usr/local/hpcx`.

- __version__: The version of Mellanox HPC-X to install.  The default
value is `2.5.0`.

__Examples__


```python
hpcx(prefix='/usr/local/hpcx', version='2.5.0')
```


## runtime
```python
hpcx.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
h = hpcx(...)
Stage0 += h
Stage1 += h.runtime()
```

# intel_mpi
```python
intel_mpi(self, **kwargs)
```
The `intel_mpi` building block downloads and installs the [Intel
MPI Library](https://software.intel.com/en-us/intel-mpi-library).

You must agree to the [Intel End User License Agreement](https://software.intel.com/en-us/articles/end-user-license-agreement)
to use this building block.

__Parameters__


- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH`, `PATH`, and others) should be modified to
include Intel MPI. `mpivars` has precedence. The default is True.

- __eula__: By setting this value to `True`, you agree to the [Intel End User License Agreement](https://software.intel.com/en-us/articles/end-user-license-agreement).
The default value is `False`.

- __mpivars__: Intel MPI provides an environment script (`mpivars.sh`)
to setup the Intel MPI environment.  If this value is `True`, the
bashrc is modified to automatically source this environment
script.  However, the Intel MPI environment is not automatically
available to subsequent container image build steps; the
environment is available when the container image is run.  To set
the Intel MPI environment in subsequent build steps you can
explicitly call `source
/opt/intel/compilers_and_libraries/linux/mpi/intel64/bin/mpivars.sh
intel64` in each build step.  If this value is to set `False`,
then the environment is set such that the environment is visible
to both subsequent container image build steps and when the
container image is run.  However, the environment may differ
slightly from that set by `mpivars.sh`.  The default value is
`True`.

- __ospackages__: List of OS packages to install prior to installing
Intel MPI.  For Ubuntu, the default values are
`apt-transport-https`, `ca-certificates`, `gnupg`, `man-db`,
`openssh-client`, and `wget`.  For RHEL-based Linux distributions,
the default values are `man-db` and `openssh-clients`.

- __version__: The version of Intel MPI to install.  The default value
is `2019.4-070`.

__Examples__


```python
intel_mpi(eula=True, version='2018.3-051')
```

## runtime
```python
intel_mpi.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
i = intel_mpi(...)
Stage0 += i
Stage1 += i.runtime()
```

# intel_psxe
```python
intel_psxe(self, **kwargs)
```
The `intel_psxe` building block installs [Intel Parallel Studio
XE](https://software.intel.com/en-us/parallel-studio-xe).

You must agree to the [Intel End User License Agreement](https://software.intel.com/en-us/articles/end-user-license-agreement)
to use this building block.

__Parameters__


- __components__: List of Intel Parallel Studio XE components to
install.  The default values is `DEFAULTS`.  If only the Intel C++
and Fortran compilers are desired, then use `intel-icc__x86_64`
and `intel-ifort__x86_64`.  Please note that the values are not
consistent between versions; for a list of components, extract
`pset/mediaconfig.xml` from the tarball and grep for `Abbr`.

- __daal__: Boolean flag to specify whether the Intel Data Analytics
Acceleration Library environment should be configured when
`psxevars` is False.  This flag also controls whether to install
- __the corresponding runtime in the `runtime` method.  Note__: this
flag does not control whether the developer environment is
installed; see `components`.  The default is True.

- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH`, `PATH`, and others) should be modified to
include Intel Parallel Studio XE. `psxevars` has precedence. The
default is True.

- __eula__: By setting this value to `True`, you agree to the [Intel End User License Agreement](https://software.intel.com/en-us/articles/end-user-license-agreement).
The default value is `False`.

- __icc__: Boolean flag to specify whether the Intel C++ Compiler
environment should be configured when `psxevars` is False.  This
flag also controls whether to install the corresponding runtime in
- __the `runtime` method.  Note__: this flag does not control whether
the developer environment is installed; see `components`.  The
default is True.

- __ifort__: Boolean flag to specify whether the Intel Fortran Compiler
environment should be configured when `psxevars` is False.  This
flag also controls whether to install the corresponding runtime in
- __the `runtime` method.  Note__: this flag does not control whether
the developer environment is installed; see `components`.  The
default is True.

- __ipp__: Boolean flag to specify whether the Intel Integrated
Performance Primitives environment should be configured when
`psxevars` is False.  This flag also controls whether to install
- __the corresponding runtime in the `runtime` method.  Note__: this
flag does not control whether the developer environment is
installed; see `components`.  The default is True.

- __license__: The license to use to activate Intel Parallel Studio XE.
If the string contains a `@` the license is interpreted as a
network license, e.g., `12345@lic-server`.  Otherwise, the string
is interpreted as the path to the license file relative to the
local build context.  The default value is empty.  While this
value is not required, the installation is unlikely to be
successful without a valid license.

- __mkl__: Boolean flag to specify whether the Intel Math Kernel Library
environment should be configured when `psxevars` is False.  This
flag also controls whether to install the corresponding runtime in
- __the `runtime` method.  Note__: this flag does not control whether
the developer environment is installed; see `components`.  The
default is True.

- __mpi__: Boolean flag to specify whether the Intel MPI Library
environment should be configured when `psxevars` is False.  This
flag also controls whether to install the corresponding runtime in
- __the `runtime` method.  Note__: this flag does not control whether
the developer environment is installed; see `components`.  The
default is True.

- __ospackages__: List of OS packages to install prior to installing
Intel MPI.  For Ubuntu, the default values are `build-essential`
and `cpio`.  For RHEL-based Linux distributions, the default
values are `gcc`, `gcc-c++`, `make`, and `which`.

- __prefix__: The top level install location.  The default value is
`/opt/intel`.

- __psxevars__: Intel Parallel Studio XE provides an environment script
(`compilervars.sh`) to setup the environment.  If this value is
`True`, the bashrc is modified to automatically source this
environment script.  However, the Intel runtime environment is not
automatically available to subsequent container image build steps;
the environment is available when the container image is run.  To
set the Intel Parallel Studio XE environment in subsequent build
steps you can explicitly call `source
/opt/intel/compilers_and_libraries/linux/bin/compilervars.sh
intel64` in each build step.  If this value is to set `False`,
then the environment is set such that the environment is visible
to both subsequent container image build steps and when the
container image is run.  However, the environment may differ
slightly from that set by `compilervars.sh`.  The default value is
`True`.

- __runtime_version__: The version of Intel Parallel Studio XE runtime
to install via the `runtime` method.  The runtime is installed
using the [intel_psxe_runtime](#intel_psxe_runtime) building
block.  This value is passed as its `version` parameter.  In
general, the major version of the runtime should correspond to the
tarball version.  The default value is `2019.5-281`.

- __tarball__: Path to the Intel Parallel Studio XE tarball relative to
the local build context.  The default value is empty.  This
parameter is required.

- __tbb__: Boolean flag to specify whether the Intel Threading Building
Blocks environment should be configured when `psxevars` is False.
This flag also controls whether to install the corresponding
- __runtime in the `runtime` method.  Note__: this flag does not control
whether the developer environment is installed; see `components`.
The default is True.

__Examples__


```python
intel_psxe(eula=True, license='XXXXXXXX.lic',
           tarball='parallel_studio_xe_2018_update1_professional_edition.tgz')
```

```python
i = intel_psxe(...)
openmpi(..., toolchain=i.toolchain, ...)
```


## runtime
```python
intel_psxe.runtime(self, _from=u'0')
```
Install the runtime from a full build in a previous stage
# intel_psxe_runtime
```python
intel_psxe_runtime(self, **kwargs)
```
The `intel_mpi` building block downloads and installs the [Intel
Parallel Studio XE runtime](https://software.intel.com/en-us/articles/intel-parallel-studio-xe-runtime-by-version).

You must agree to the [Intel End User License Agreement](https://software.intel.com/en-us/articles/end-user-license-agreement)
to use this building block.

Note: this building block does *not* install development versions
of the Intel software tools.  Please see the
[intel_psxe](#intel_psxe), [intel_mpi](#intel_mpi), or [mkl](#mkl)
building blocks for development environments.

__Parameters__


- __daal__: Boolean flag to specify whether the Intel Data Analytics
Acceleration Library runtime should be installed.  The default is
True.

- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH`, `PATH`, and others) should be modified to
include Intel Parallel Studio XE runtime. `psxevars` has
precedence. The default is True.

- __eula__: By setting this value to `True`, you agree to the [Intel End User License Agreement](https://software.intel.com/en-us/articles/end-user-license-agreement).
The default value is `False`.

- __icc__: Boolean flag to specify whether the Intel C++ Compiler
runtime should be installed.  The default is True.

- __ifort__: Boolean flag to specify whether the Intel Fortran Compiler
runtime should be installed.  The default is True.

- __ipp__: Boolean flag to specify whether the Intel Integrated
Performance Primitives runtime should be installed.  The default
is True.

- __mkl__: Boolean flag to specify whether the Intel Math Kernel Library
runtime should be installed.  The default is True.

- __mpi__: Boolean flag to specify whether the Intel MPI Library runtime
should be installed.  The default is True.

- __psxevars__: Intel Parallel Studio XE provides an environment script
(`psxevars.sh`) to setup the environment.  If this value is
`True`, the bashrc is modified to automatically source this
environment script.  However, the Intel runtime environment is not
automatically available to subsequent container image build steps;
the environment is available when the container image is run.  To
set the Intel Parallel Studio XE runtime environment in subsequent
build steps you can explicitly call `source
/opt/intel/psxe_runtime/linux/bin/psxevars.sh intel64` in each
build step.  If this value is to set `False`, then the environment
is set such that the environment is visible to both subsequent
container image build steps and when the container image is run.
However, the environment may differ slightly from that set by
`psxevars.sh`.  The default value is `True`.

- __ospackages__: List of OS packages to install prior to installing
Intel MPI.  For Ubuntu, the default values are
`apt-transport-https`, `ca-certificates`, `gcc`, `gnupg`,
`man-db`, `openssh-client`, and `wget`.  For RHEL-based Linux
distributions, the default values are `man-db`, `openssh-clients`,
and `which`.

- __tbb__: Boolean flag to specify whether the Intel Threading Building
Blocks runtime should be installed.  The default is True.

- __version__: The version of the Intel Parallel Studio XE runtime to
install.  The default value is `2019.5-281`.

__Examples__


```python
intel_psxe_runtime(eula=True, version='2018.5-281')
```

```python
intel_psxe_runtime(daal=False, eula=True, ipp=False, psxevars=False)
```


## runtime
```python
intel_psxe_runtime.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
i = intel_psxe_runtime(...)
Stage0 += i
Stage1 += i.runtime()
```

# julia
```python
julia(self, **kwargs)
```
The `julia` building block downloads and installs the
[Julia](https://julialang.org) programming environment.

__Parameters__


- __cuda__: Boolean flag to specify whether the JuliaGPU packages should
be installed.  If True, the `CUDAapi`, `CUDAdrv`, `CUDAnative`,
and `CuArrays` packages are installed. Note that the `CUDAdrv`
package must be rebuilt when the container is running to align
with the host CUDA driver. The default is False.

- __depot__: Path to the location of "user" Julia package depot. The
default is an empty string, i.e., `~/.julia`. The depot location
needs to be writable by the user running the container.

- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH` and `PATH`) should be modified to include
Julia. The default is True.

- __history__: Path to the Julia history file. The default value is an
empty string, i.e., `~/.julia/logs/repl_history.jl`. The history
location needs to be writable by the user running the container.

- __ldconfig__: Boolean flag to specify whether the Julia library
directory should be added dynamic linker cache.  If False, then
`LD_LIBRARY_PATH` is modified to include the Julia library
directory. The default value is False.

- __ospackages__: List of OS packages to install prior to building. The
default values are `tar` and `wget`.

- __packages__: List of Julia packages to install. The default is an
empty list.

- __prefix__: The top level installation location.  The default value
is `/usr/local/julia`.

- __version__: The version of Julia to install.  The default value is
`1.2.0`.

__Examples__


```python
julia(prefix='/usr/local/julia', version='1.2.0')
```

```python
julia(depot='/tmp', history='/tmp/repl_history.jl')
```


## runtime
```python
julia.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
j = julia(...)
Stage0 += j
Stage1 += j.runtime()
```

# knem
```python
knem(self, **kwargs)
```
The `knem` building block install the headers from the
[KNEM](http://knem.gforge.inria.fr) component.

__Parameters__


- __environment__: Boolean flag to specify whether the environment
(`CPATH`) should be modified to include knem. The default is True.

- __ospackages__: List of OS packages to install prior to installing.
The default values are `ca-certificates` and `git`.

- __prefix__: The top level install location.  The default value is
`/usr/local/knem`.

- __version__: The version of KNEM source to download.  The default
value is `1.1.3`.

__Examples__


```python
knem(prefix='/opt/knem/1.1.3', version='1.1.3')
```


## runtime
```python
knem.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
k = knem(...)
Stage0 += k
Stage1 += k.runtime()
```

# kokkos
```python
kokkos(self, **kwargs)
```
The `kokkos` building block downloads and installs the
[Kokkos](https://github.com/kokkos/kokkos) component.

__Parameters__


- __arch__: Flag to set the target architecture. If set adds
`--arch=value` to the list of `generate_makefile.bash` options.
The default value is `Pascal60`, i.e., sm_60.  If a cuda aware
build is not selected, then a non-default value should be used.

- __cuda__: Flag to control whether a CUDA aware build is performed.  If
True, adds `--with-cuda` to the list of `generate_makefile.bash`
options.  If a string, uses the value of the string as the CUDA
path.  If False, does nothing.  The default value is True.

- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH` and `PATH`) should be modified to include
Kokkos. The default is True.

- __hwloc__: Flag to control whether a hwloc aware build is performed.
If True, adds `--with-hwloc` to the list of
`generate_makefile.bash` options.  If a string, uses the value of
the string as the hwloc path.  If False, does nothing.  The
default value is True.

- __opts__: List of options to pass to `generate_makefile.bash`.  The
default is an empty list.

- __ospackages__: List of OS packages to install prior to building.  For
Ubuntu, the default values are `bc`, `gzip`, `libhwloc-dev`,
`make`, `tar`, and `wget`.  For RHEL-based Linux distributions the
default values are `bc`, `gzip`, `hwloc-devel`, `make`, `tar`,
`wget`, and `which`.

- __prefix__: The top level installation location.  The default value
is `/usr/local/kokkos`.

- __version__: The version of Kokkos source to download.  The default
value is `2.9.00`.

__Examples__


```python
kokkos(prefix='/opt/kokkos/2.8.00', version='2.8.00')
```


## runtime
```python
kokkos.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
k = kokkos(...)
Stage0 += k
Stage1 += k.runtime()
```

# libsim
```python
libsim(self, **kwargs)
```
The `libsim` building block configures, builds, and installs the
[VisIt
Libsim](http://www.visitusers.org/index.php?title=Libsim_Batch)
component.

If GPU rendering will be used then a
[cudagl](https://hub.docker.com/r/nvidia/cudagl) base image is
recommended.

__Parameters__


- __build_opts__: List of VisIt build script options. The default values
are `--xdb` and `--server-components-only`.

- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH` and `PATH`) should be modified to include
Libsim. The default is True.

- __ldconfig__: Boolean flag to specify whether the Libsim library
directories should be added dynamic linker cache.  If False, then
`LD_LIBRARY_PATH` is modified to include the Libsim library
directories. The default value is False.

- __mpi__: Boolean flag to specify whether Libsim should be built with
MPI support.  VisIt uses MPI-1 routines that have been removed
from the MPI standard; the MPI library may need to be built with
special compatibility options, e.g., `--enable-mpi1-compatibility`
for OpenMPI.  If True, then the build script options `--parallel`
and `--no-icet` are added and the environment variable
`PAR_COMPILER` is set to `mpicc`. If True, a MPI library building
block should be installed prior this building block.  The default
value is True.

- __ospackages__: List of OS packages to install prior to configuring
and building.  For Ubuntu, the default values are `gzip`, `make`,
`patch`, `tar`, `wget`, `zlib1g-dev`, `libxt-dev`,
`libgl1-mesa-dev`, and `libglu1-mesa-dev`.  For RHEL-based Linux
distributions, the default values are `gzip`, `make`, `patch`,
`tar`, `wget`, `which`, `zlib-devel`, `libXt-devel`,
`libglvnd-devel`, `mesa-libGL-devel`, and `mesa-libGLU-devel`.

- __prefix__: The top level install location.  The default value is
`/usr/local/visit`.

- __system_cmake__: Boolean flag to specify whether the system provided
cmake should be used.  If False, then the build script downloads a
private copy of cmake.  If True, then the build script option
`--system-cmake` is added.  If True, then the [cmake](#cmake)
building block should be installed prior to this building block.
The default is True.

- __system_python__: Boolean flag to specify whether the system provided
python should be used.  If False, then the build script downloads
a private copy of python.  If True, then the build script option
`--system-python` is added.  If True, then the [Python](#python)
building block should be installed with development libraries
prior to this building block.  The default is True.

- __thirdparty__: Boolean flag to specify whether third-party components
included by the build script should be retained.  If True, then
the build script option `--thirdparty-path` is added and set to
`<prefix>/third-party`.  The default is True.

- __version__: The version of Libsim source to download.  The default
value is `2.13.3`.

__Examples__


```python
libsim(prefix='/opt/libsim', version='2.13.3')
```


## runtime
```python
libsim.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__

```python
l = libsim(...)
Stage0 += l
Stage1 += l.runtime()
```

# llvm
```python
llvm(self, **kwargs)
```
The `llvm` building block installs the LLVM compilers (clang and
clang++) from the upstream Linux distribution.

As a side effect, a toolchain is created containing the LLVM
compilers.  A toolchain can be passed to other operations that
want to build using the LLVM compilers.

__Parameters__


- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH` and `PATH`) should be modified to include the
LLVM compilers. The default is True.

- __extra_repository__: Boolean flag to specify whether to enable an
extra package repository containing addition LLVM compiler
packages.  For Ubuntu, setting this flag to True enables the
- __`ppa__:ubuntu-toolchain-r/test` repository.  For RHEL-based Linux
distributions, setting this flag to True enables the Software
Collections (SCL) repository.  The default is False.

- __version__: The version of the LLVM compilers to install.  Note that
the version refers to the Linux distribution packaging, not the
actual compiler version.  For Ubuntu, the version is appended to
the default package name, e.g., `clang-6.0`.  For RHEL-based Linux
distributions, the version is inserted into the SCL Developer
Toolset package name, e.g., `llvm-toolset-7-clang`.  For
RHEL-based Linux distributions, specifying the version
automatically sets `extra_repository` to True.  The default is an
empty value.

__Examples__


```python
llvm()
```

```python
llvm(extra_repository=True, version='7')
```

```python
l = llvm()
openmpi(..., toolchain=l.toolchain, ...)
```


## runtime
```python
llvm.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
l = llvm(...)
Stage0 += l
Stage1 += l.runtime()
```

# mkl
```python
mkl(self, **kwargs)
```
The `mkl` building block downloads and installs the [Intel Math
Kernel Library](http://software.intel.com/mkl).

You must agree to the [Intel End User License Agreement](https://software.intel.com/en-us/articles/end-user-license-agreement)
to use this building block.

__Parameters__


- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH`, `PATH`, and other variables) should be
modified to include MKL. The default is True.

- __eula__: By setting this value to `True`, you agree to the [Intel End User License Agreement](https://software.intel.com/en-us/articles/end-user-license-agreement).
The default value is `False`.

- __mklvars__: MKL provides an environment script (`mklvars.sh`) to
setup the MKL environment.  If this value is `True`, the bashrc is
modified to automatically source this environment script.
However, the MKL environment is not automatically available to
subsequent container image build steps; the environment is
available when the container image is run.  To set the MKL
environment in subsequent build steps you can explicitly call
`source /opt/intel/mkl/bin/mklvars.sh intel64` in each build step.
If this value is to set `False`, then the environment is set such
that the environment is visible to both subsequent container image
build steps and when the container image is run.  However, the
environment may differ slightly from that set by `mklvars.sh`.
The default value is `True`.

- __ospackages__: List of OS packages to install prior to installing
MKL.  For Ubuntu, the default values are `apt-transport-https`,
`ca-certificates`, `gnupg`, and `wget`.  For RHEL-based Linux
distributions, the default is an empty list.

- __version__: The version of MKL to install.  The default value is
`2019.4-070`.

__Examples__


```python
mkl(eula=True, version='2018.3-051')
```


## runtime
```python
mkl.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
m = mkl(...)
Stage0 += m
Stage1 += m.runtime()
```

# mlnx_ofed
```python
mlnx_ofed(self, **kwargs)
```
The `mlnx_ofed` building block downloads and installs the [Mellanox
OpenFabrics Enterprise Distribution for
Linux](http://www.mellanox.com/page/products_dyn?product_family=26).

__Parameters__


- __oslabel__: The Linux distribution label assigned by Mellanox to the
tarball.  For Ubuntu, the default value is `ubuntu16.04`.  For
RHEL-based Linux distributions, the default value is `rhel7.2` for
x86_64 processors and `rhel7.6alternate` for aarch64 processors.

- __ospackages__: List of OS packages to install prior to installing
OFED.  For Ubuntu, the default values are `findutils`,
`libnl-3-200`, `libnl-route-3-200`, `libnuma1`, and `wget`.  For
RHEL-based 7.x distributions, the default values are `findutils`,
`libnl`, `libnl3`, `numactl-libs`, and `wget`.  For RHEL-based 8.x
distributions, the default values are `findutils`, `libnl3`,
`numactl-libs`, and `wget`.

- __packages__: List of packages to install from Mellanox OFED.  For
Ubuntu, the default values are `libibverbs1`, `libibverbs-dev`,
`libibmad`, `libibmad-devel`, `libibumad`, `libibumad-devel`,
`libmlx4-1`, `libmlx4-dev`, `libmlx5-1`, `libmlx5-dev`,
`librdmacm1`, `librdmacm-dev`, and `ibverbs-utils`.  For
RHEL-based Linux distributions, the default values are
`libibverbs`, `libibverbs-devel`, `libibverbs-utils`, `libibmad`,
`libibmad-devel`, `libibumad`, `libibumad-devel`, `libmlx4`,
`libmlx4-devel`, `libmlx5`, `libmlx5-devel`, `librdmacm`, and
`librdmacm-devel`.

- __prefix__: The top level install location.  Instead of installing the
packages via the package manager, they will be extracted to this
location.  This option is useful if multiple versions of Mellanox
OFED need to be installed.  The environment must be manually
configured to recognize the Mellanox OFED location, e.g., in the
container entry point.  The default value is empty, i.e., install
via the package manager to the standard system locations.

- __version__: The version of Mellanox OFED to download.  The default
value is `4.6-1.0.1.1`.

__Examples__


```python
mlnx_ofed(version='4.2-1.0.0.0')
```


## runtime
```python
mlnx_ofed.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
m = mlnx_ofed(...)
Stage0 += m
Stage1 += m.runtime()
```

# mpich
```python
mpich(self, **kwargs)
```
The `mpich` building block configures, builds, and installs the
[MPICH](https://www.mpich.org) component.

As a side effect, a toolchain is created containing the MPI
compiler wrappers.  The tool can be passed to other operations
that want to build using the MPI compiler wrappers.

__Parameters__


- __check__: Boolean flag to specify whether the `make check` and `make
testing` steps should be performed.  The default is False.

- __configure_opts__: List of options to pass to `configure`.  The
default is an empty list.

- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH` and `PATH`) should be modified to include
MPICH. The default is True.

- __ldconfig__: Boolean flag to specify whether the MPICH library
directory should be added dynamic linker cache.  If False, then
`LD_LIBRARY_PATH` is modified to include the MPICH library
directory. The default value is False.

- __ospackages__: List of OS packages to install prior to configuring
and building.  For Ubuntu, the default values are `file`, `gzip`,
`make`, `openssh-client`, `perl`, `tar`, and `wget`.  For
RHEL-based Linux distributions, the default values are `file`,
`gzip`, `make`, `openssh-clients`, `perl`, `tar`, and `wget`.

- __prefix__: The top level install location.  The default value is
`/usr/local/mpich`.

- __toolchain__: The toolchain object.  This should be used if
non-default compilers or other toolchain options are needed.  The
default is empty.

- __version__: The version of MPICH source to download.  The default
value is `3.3.1`.

__Examples__


```python
mpich(prefix='/opt/mpich/3.3', version='3.3')
```

```python
p = pgi(eula=True)
mpich(toolchain=p.toolchain)
```

## runtime
```python
mpich.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__

```python
m = mpich(...)
Stage0 += m
Stage1 += m.runtime()
```

# multi_ofed
```python
multi_ofed(self, **kwargs)
```
The `multi_ofed` building block downloads and installs multiple
versions of the OpenFabrics Enterprise Distribution (OFED). Please
refer to the [`mlnx_ofed`](#mlnx_ofed) and [`ofed`](#ofed)
building blocks for more information.

__Parameters__


- __inbox__: Boolean flag to specify whether to install the 'inbox' OFED
distributed by the Linux distribution.  The default is True.

- __mlnx_oslabel__: The Linux distribution label assigned by Mellanox to
the tarball. Please see the corresponding
[`mlnx_ofed`](#mlnx_ofed) parameter for more information.

- __mlnx_packages__: List of packages to install from Mellanox
OFED. Please see the corresponding [`mlnx_ofed`](#mlnx_ofed)
parameter for more information.

- __mlnx_versions__: A list of [Mellanox OpenFabrics Enterprise Distribution for Linux](http://www.mellanox.com/page/products_dyn?product_family=26)
versions to install.  The default values are `3.3-1.0.4.0`,
`3.4-2.0.0.0`, `4.0-2.0.0.1`, `4.1-1.0.2.0`, `4.2-1.2.0.0`,
`4.3-1.0.1.0`, `4.4-2.0.7.0`, `4.5-1.0.1.0`, `4.6-1.0.1.1`

- __ospackages__: List of OS packages to install prior to installing
OFED.  For Ubuntu, the default values are `libnl-3-200`,
`libnl-route-3-200`, and `libnuma1`.  For RHEL-based Linux
distributions, the default values are `libnl`, `libnl3`, and
`numactl-libs`.

- __prefix__: The top level install location.  The OFED packages will be
extracted to this location as subdirectories named for the
respective Mellanox OFED version, or `inbox` for the 'inbox'
OFED. The environment must be manually configured to recognize the
desired OFED location, e.g., in the container entry point. The
default value is `/usr/local/ofed`.

__Examples__


```python
multi_ofed(inbox=True, mlnx_versions=['4.5-1.0.1.0', '4.6-1.0.1.1'],
           prefix='/usr/local/ofed')
```


## runtime
```python
multi_ofed.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

# mvapich2
```python
mvapich2(self, **kwargs)
```
The `mvapich2` building block configures, builds, and installs the
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

__Parameters__


- __check__: Boolean flag to specify whether the `make check` step
should be performed.  The default is False.

- __configure_opts__: List of options to pass to `configure`.  The
default values are `--disable-mcast`.

- __cuda__: Boolean flag to control whether a CUDA aware build is
performed.  If True, adds `--enable-cuda --with-cuda` to the list
of `configure` options, otherwise adds `--disable-cuda`.  If the
toolchain specifies `CUDA_HOME`, then that path is used, otherwise
`/usr/local/cuda` is used for the path.  The default value is
True.

- __directory__: Path to the unpackaged source directory relative to
the local build context.  The default value is empty.  If this is
defined, the source in the local build context will be used rather
than downloading the source from the web.

- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH` and `PATH`) should be modified to include
MVAPICH2. The default is True.

- __gpu_arch__: The GPU architecture to use.  Older versions of MVAPICH2
(2.3b and previous) were hard-coded to use "sm_20".  This option
has no effect on more recent MVAPICH2 versions.  The default value
is to use the MVAPICH2 default.

- __ldconfig__: Boolean flag to specify whether the MVAPICH2 library
directory should be added dynamic linker cache.  If False, then
`LD_LIBRARY_PATH` is modified to include the MVAPICH2 library
directory. The default value is False.

- __ospackages__: List of OS packages to install prior to configuring
and building.  For Ubuntu, the default values are `byacc`, `file`,
`make`, `openssh-client`, and `wget`.  For RHEL-based Linux
distributions, the default values are `byacc`, `file`, `make`,
`openssh-clients`, and `wget`.

- __prefix__: The top level install location.  The default value is
`/usr/local/mvapich2`.

- __toolchain__: The toolchain object.  This should be used if
non-default compilers or other toolchain options are needed.  The
default is empty.

- __version__: The version of MVAPICH2 source to download.  This value
is ignored if `directory` is set.  The default value is `2.3.1`.

__Examples__


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

## runtime
```python
mvapich2.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
m = mvapich2(...)
Stage0 += m
Stage1 += m.runtime()
```

# mvapich2_gdr
```python
mvapich2_gdr(self, **kwargs)
```
The `mvapich2_gdr` building blocks installs the
[MVAPICH2-GDR](http://mvapich.cse.ohio-state.edu) component.
Depending on the parameters, the package will be downloaded from
the web (default) or copied from the local build context.

MVAPICH2-GDR is distributed as a binary package, so certain
dependencies need to be met and only certain combinations of
recipe components are supported; please refer to the MVAPICH2-GDR
documentation for more information.

The [GNU compiler](#gnu) or [PGI compiler](#pgi) building blocks
should be installed prior to this building block.

The [Mellanox OFED](#mlnx_ofed) building block should be installed
prior to this building block.

The [gdrcopy](#gdrcopy) building block should be installed prior
to this building block.

As a side effect, a toolchain is created containing the MPI
compiler wrappers.  The toolchain can be passed to other
operations that want to build using the MPI compiler wrappers.

Note: Using MVAPICH2-GDR on non-RHEL-based Linux distributions has
several issues, including compiler version mismatches and libnuma
incompatibilities.

__Parameters__


- __arch__: The processor architecture of the MVAPICH2-GDR package.  The
default value is set automatically based on the processor
architecture of the base image.

- __cuda_version__: The version of CUDA the MVAPICH2-GDR package was
built against.  The version string format is X.Y.  The version
should match the version of CUDA provided by the base image.  This
value is ignored if `package` is set.  The default value is `9.2`.

- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH` and `PATH`) should be modified to include
MVAPICH2-GDR. The default is True.

- __gnu__: Boolean flag to specify whether a GNU build should be used.
The default value is True.

- __ldconfig__: Boolean flag to specify whether the MVAPICH2-GDR library
directory should be added dynamic linker cache.  If False, then
`LD_LIBRARY_PATH` is modified to include the MVAPICH2-GDR library
directory. The default value is False.

- __mlnx_ofed_version__: The version of Mellanox OFED the
MVAPICH2-GDR package was built against.  The version string format
is X.Y.  The version should match the version of Mellanox OFED
installed by the `mlnx_ofed` building block.  This value is
ignored if `package` is set.  The default value is `4.5`.

- __ospackages__: List of OS packages to install prior to installation.
For Ubuntu, the default values are `cpio`, `libnuma1`,
`openssh-client`, `rpm2cpio` and `wget`, plus `libgfortran3` if a
GNU compiled package is selected.  For RHEL-based Linux
distributions, the default values are `libpciaccess`,
`numactl-libs`, `openssh-clients`, and `wget`, plus `libgfortran`
if a GNU compiled package is selected.

- __package__: Specify the package name to download.  The package should
correspond to the other recipe components (e.g., compiler version,
CUDA version, Mellanox OFED version).  If specified, this option
overrides all other building block options (e.g., compiler family,
compiler version, CUDA version, Mellanox OFED version,
MVAPICH2-GDR version).

- __pgi__: Boolean flag to specify whether a PGI build should be used.
The default value is False.

- __version__: The version of MVAPICH2-GDR to download.  The value is
ignored if `package` is set.  The default value is `2.3.1`.  Due
to differences in the packaging scheme, versions prior to 2.3 are
not supported.

__Examples__


```python
mvapich2_gdr(version='2.3.1')
```

```python
mvapich2_gdr(package='mvapich2-gdr-mcast.cuda10.0.mofed4.3.gnu4.8.5-2.3-1.el7.x86_64.rpm')
```


## runtime
```python
mvapich2_gdr.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
m = mvapich2_gdr(...)
Stage0 += m
Stage1 += m.runtime()
```

# netcdf
```python
netcdf(self, **kwargs)
```
The `netcdf` building block downloads, configures, builds, and
installs the
[NetCDF](https://www.unidata.ucar.edu/software/netcdf/) component.

The [HDF5](#hdf5) building block should be installed prior to this
building block.

__Parameters__


- __check__: Boolean flag to specify whether the `make check` step
should be performed.  The default is False.

- __configure_opts__: List of options to pass to `configure`.  The
default value is an empty list.

- __cxx__: Boolean flag to specify whether the NetCDF C++ library should
be installed.  The default is True.

- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH` and `PATH`) should be modified to include
NetCDF. The default is True.

- __fortran__: Boolean flag to specify whether the NetCDF Fortran
library should be installed.  The default is True.

- __hdf5_dir__: Path to the location where HDF5 is installed in the
container image.  The default value is `/usr/local/hdf5`.

- __ldconfig__: Boolean flag to specify whether the NetCDF library
directory should be added dynamic linker cache.  If False, then
`LD_LIBRARY_PATH` is modified to include the NetCDF library
directory. The default value is False.

- __ospackages__: List of OS packages to install prior to configuring
and building.  For Ubuntu, the default values are
`ca-certificates`, `file`, `libcurl4-openssl-dev`, `m4`, `make`,
`wget`, and `zlib1g-dev`.  For RHEL-based Linux distributions the
default values are `ca-certificates`, `file`, `libcurl-devel`
`m4`, `make`, `wget`, and `zlib-devel`.

- __prefix__: The top level install location.  The default location is
`/usr/local/netcdf`.

- __toolchain__: The toolchain object.  This should be used if
non-default compilers or other toolchain options are needed.  The
default is empty.

- __version__: The version of NetCDF to download.  The default value is
`4.7.0`.

- __version_cxx__: The version of NetCDF C++ to download.  The default
value is `4.3.0`.

- __version_fortran__: The version of NetCDF Fortran to download.  The
default value is `4.4.5`.

__Examples__


```python
netcdf(prefix='/opt/netcdf/4.6.1', version='4.6.1')
```

```python
p = pgi(eula=True)
netcdf(toolchain=p.toolchain)
```


## runtime
```python
netcdf.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
n = netcdf(...)
Stage0 += n
Stage1 += n.runtime()
```

# ofed
```python
ofed(self, **kwargs)
```
The `ofed` building block installs the OpenFabrics Enterprise
Distribution packages that are part of the Linux distribution.

For Ubuntu 16.04, the following packages are installed:
`dapl2-utils`, `ibutils`, `ibverbs-utils`, `infiniband-diags`,
`libdapl2`, `libdapl-dev`, `libibcm1`, `libibcm-dev`, `libibmad5`,
`libibmad-dev`, `libibverbs1`, `libibverbs-dev`, `libmlx4-1`,
`libmlx4-dev`, `libmlx5-1`, `libmlx5-dev`, `librdmacm1`,
`librdmacm-dev`, and `rdmacm-utils`.  For Ubuntu 16.04 and aarch64
processors, the `dapl2-utils`, `libdapl2`, `libdapl-dev`,
`libibcm1` and `libibcm-dev` packages are not installed because
they are not available.  For Ubuntu 16.04 and ppc64le processors,
the `libibcm1` and `libibcm-dev` packages are not installed
because they are not available.

For Ubuntu 18.04, the following packages are installed:
`dapl2-utils`, `ibutils`, `ibverbs-providers`, `ibverbs-utils`,
`infiniband-diags`, `libdapl2`, `libdapl-dev`, `libibmad5`,
`libibmad-dev`, `libibverbs1`, `libibverbs-dev`, `librdmacm1`,
`librdmacm-dev`, and `rdmacm-utils`.

For RHEL-based 7.x distributions, the following packages are
installed: `dapl`, `dapl-devel`, `ibutils`, `libibcm`, `libibmad`,
`libibmad-devel`, `libmlx5`, `libibumad`, `libibverbs`,
`libibverbs-utils`, `librdmacm`, `rdma-core`, and
`rdma-core-devel`.

For RHEL-based 8.x distributions, the following packages are
installed: `libibmad`, `libibmad-devel`, `libmlx5`, `libibumad`,
`libibverbs`, `libibverbs-utils`, `librdmacm`, `rdma-core`, and
`rdma-core-devel`.

__Parameters__


- __prefix__: The top level install location. Install of installing the
packages via the package manager, they will be extracted to this
location. This option is useful if multiple versions of OFED need
to be installed. The environment must be manually configured to
recognize the OFED location, e.g., in the container entry
point. The default value is empty, i.e., install via the package
manager to the standard system locations.

__Examples__


```python
ofed()
```


## runtime
```python
ofed.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
o = ofed(...)
Stage0 += o
Stage1 += o.runtime()
```

# openblas
```python
openblas(self, **kwargs)
```
The `openblas` building block builds and installs the
[OpenBLAS](https://www.openblas.net) component.

__Parameters__


- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH` and `PATH`) should be modified to include
OpenBLAS. The default is True.

- __ldconfig__: Boolean flag to specify whether the OpenBLAS library
directory should be added dynamic linker cache.  If False, then
`LD_LIBRARY_PATH` is modified to include the OpenBLAS library
directory. The default value is False.

- __make_opts__: List of options to pass to `make`.  For aarch64
processors, the default values are `TARGET=ARMV8` and
`USE_OPENMP=1`.  For ppc64le processors, the default values are
`TARGET=POWER8` and `USE_OPENMP=1`.  For x86_64 processors, the
default value is `USE_OPENMP=1`.

- __ospackages__: List of OS packages to install prior to building.  The
default values are `make`, `perl`, `tar`, and `wget`.

- __prefix__: The top level installation location.  The default value is
`/usr/local/openblas`.

- __toolchain__: The toolchain object.  This should be used if
non-default compilers or other toolchain options are needed.  The
default is empty.

- __version__: The version of OpenBLAS source to download.  The default
value is `0.3.6`.

__Examples__


```python
openblas(prefix='/opt/openblas/0.3.1', version='0.3.1')
```

```python
p = pgi(eula=True)
openblas(toolchain=p.toolchain)
```


## runtime
```python
openblas.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
o = openblas(...)
Stage0 += o
Stage1 += o.runtime()
```

# openmpi
```python
openmpi(self, **kwargs)
```
The `openmpi` building block configures, builds, and installs the
[OpenMPI](https://www.open-mpi.org) component.  Depending on the
parameters, the source will be downloaded from the web (default)
or copied from a source directory in the local build context.

As a side effect, a toolchain is created containing the MPI
compiler wrappers.  The tool can be passed to other operations
that want to build using the MPI compiler wrappers.

__Parameters__


- __check__: Boolean flag to specify whether the `make check` step
should be performed.  The default is False.

- __configure_opts__: List of options to pass to `configure`.  The
default values are `--disable-getpwuid` and
`--enable-orterun-prefix-by-default`.

- __cuda__: Boolean flag to control whether a CUDA aware build is
performed.  If True, adds `--with-cuda` to the list of `configure`
options, otherwise adds `--without-cuda`.  If the toolchain
specifies `CUDA_HOME`, then that path is used.  The default value
is True.

- __directory__: Path to the unpackaged source directory relative to the
local build context.  The default value is empty.  If this is
defined, the source in the local build context will be used rather
than downloading the source from the web.

- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH` and `PATH`) should be modified to include
OpenMPI. The default is True.

- __infiniband__: Boolean flag to control whether InfiniBand
capabilities are included.  If True, adds `--with-verbs` to the
list of `configure` options, otherwise adds `--without-verbs`.
The default value is True.

- __ldconfig__: Boolean flag to specify whether the OpenMPI library
directory should be added dynamic linker cache.  If False, then
`LD_LIBRARY_PATH` is modified to include the OpenMPI library
directory. The default value is False.

- __ospackages__: List of OS packages to install prior to configuring
and building.  For Ubuntu, the default values are `bzip2`, `file`,
`hwloc`, `libnuma-dev`, `make`, `openssh-client`, `perl`, `tar`,
and `wget`.  For RHEL-based Linux distributions, the default
values are `bzip2`, `file`, `hwloc`, `make`, `numactl-devl`,
`openssh-clients`, `perl`, `tar`, and `wget`.

- __pmi__: Flag to control whether PMI is used by the build.  If True,
adds `--with-pmi` to the list of `configure` options.  If a
string, uses the value of the string as the PMI path, e.g.,
`--with-pmi=/usr/local/slurm-pmi2`.  If False, does nothing.  The
default is False.

- __pmix__: Flag to control whether PMIX is used by the build.  If True,
adds `--with-pmix` to the list of `configure` options.  If a
string, uses the value of the string as the PMIX path, e.g.,
`--with-pmix=/usr/local/pmix`.  If False, does nothing.  The
default is False.

- __prefix__: The top level install location.  The default value is
`/usr/local/openmpi`.

- __toolchain__: The toolchain object.  This should be used if
non-default compilers or other toolchain options are needed.  The
default is empty.

- __ucx__: Flag to control whether UCX is used by the build.  If True,
adds `--with-ucx` to the list of `configure` options.  If a
string, uses the value of the string as the UCX path, e.g.,
`--with-ucx=/path/to/ucx`.  If False, adds `--without-ucx` to the
list of `configure` options.  The default is False.

- __version__: The version of OpenMPI source to download.  This
value is ignored if `directory` is set.  The default value is
`4.0.1`.

__Examples__


```python
openmpi(cuda=False, infiniband=False, prefix='/opt/openmpi/2.1.2',
    version='2.1.2')
```

```python
openmpi(directory='sources/openmpi-3.0.0')
```

```python
p = pgi(eula=True)
openmpi(toolchain=p.toolchain)
```

```python
openmpi(configure_opts=['--disable-getpwuid', '--with-slurm'],
        ospackages=['file', 'hwloc', 'libslurm-dev'])
```

```python
openmpi(pmi='/usr/local/slurm-pmi2', pmix='internal')
```


## runtime
```python
openmpi.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__

```python
o = openmpi(...)
Stage0 += o
Stage1 += o.runtime()
```

# packages
```python
packages(self, **kwargs)
```
The `packages` building block specifies the set of operating system
packages to install.  Based on the Linux distribution, the
building block invokes either `apt-get` (Ubuntu) or `yum`
(RHEL-based).

This building block is preferred over directly using the
[`apt_get`](#apt_get) or [`yum`](#yum) building blocks.

__Parameters__


- __apt__: A list of Debian packages to install.  The default is an
empty list.

- __aptitude__: Boolean flag to specify whether `aptitude` should be
used instead of `apt-get`.  The default is False.

- __apt_keys__: A list of GPG keys to add.  The default is an empty
list.

- __apt_ppas__: A list of personal package archives to add.  The default
is an empty list.

- __apt_repositories__: A list of apt repositories to add.  The default
is an empty list.

- __download__: Boolean flag to specify whether to download the deb /
rpm packages instead of installing them.  The default is False.

- __download_directory__: The deb package download location. This
parameter is ignored if `download` is False. The default value is
`/var/tmp/packages_download`.

- __epel__: Boolean flag to specify whether to enable the Extra Packages
for Enterprise Linux (EPEL) repository.  The default is False.
This parameter is ignored if the Linux distribution is not
RHEL-based.

- __extract__: Location where the downloaded packages should be
extracted. Note, this extracts and does not install the packages,
i.e., the package manager is bypassed. After the downloaded
packages are extracted they are deleted. This parameter is ignored
if `download` is False. If empty, then the downloaded packages are
not extracted. The default value is an empty string.

- __ospackages__: A list of packages to install.  The list is used for
both Ubuntu and RHEL-based Linux distributions, therefore only
packages with the consistent names across Linux distributions
should be specified.  This parameter is ignored if `apt` or `yum`
is specified.  The default value is an empty list.

- __powertools__: Boolean flag to specify whether to enable the
PowerTools repository.  The default is False.  This parameter is
ignored if the Linux distribution is not RHEL-based.

- __scl__: Boolean flag to specify whether to enable the Software
Collections (SCL) repository.  The default is False.  This
parameter is ignored if the Linux distribution is not RHEL-based.

- __yum__: A list of RPM packages to install.  The default value is an
empty list.

- __yum4__: Boolean flag to specify whether `yum4` should be used
instead of `yum`.  The default is False.  This parameter is only
recognized if the CentOS version is 7.x.

- __yum_keys__: A list of GPG keys to import.  The default is an empty
list.

- __yum_repositories__: A list of yum repositories to add.  The default
is an empty list.

__Examples__


```python
packages(ospackages=['make', 'wget'])
```

```python
packages(apt=['zlib1g-dev'], yum=['zlib-devel'])
```

```python
packages(apt=['python3'], yum=['python34'], epel=True)
```


# pgi
```python
pgi(self, **kwargs)
```
The `pgi` building block downloads and installs the PGI compiler.
Currently, the only option is to install the latest community
edition.

You must agree to the [PGI End-User License Agreement](https://www.pgroup.com/doc/LICENSE.txt) to use this
building block.

As a side effect, a toolchain is created containing the PGI
compilers.  The tool can be passed to other operations that want
to build using the PGI compilers.

__Parameters__


- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH`, `PATH`, and potentially other variables)
should be modified to include the PGI compiler. The default is
True.

- __eula__: By setting this value to `True`, you agree to the [PGI End-User License Agreement](https://www.pgroup.com/doc/LICENSE.txt).
The default value is `False`.

- __extended_environment__: Boolean flag to specify whether an extended
set of environment variables should be defined.  If True, the
- __following environment variables will be defined__: `CC`, `CPP`,
`CXX`, `F77`, `F90`, `FC`, and `MODULEPATH`.  In addition, if the
PGI MPI component is selected then `PGI_OPTL_INCLUDE_DIRS` and
`PGI_OPTL_LIB_DIRS` will also be defined and `PATH` and
`LD_LIBRARY_PATH` will include the PGI MPI component.  If False,
then only `PATH` and `LD_LIBRARY_PATH` will be extended to include
the PGI compiler.  The default value is `False`.

- __mpi__: Boolean flag to specify whether the MPI component should be
installed.  If True, MPI will be installed.  The default value is
False.

- __ospackages__: List of OS packages to install prior to installing the
PGI compiler.  For Ubuntu, the default values are `gcc`, `g++`,
`libnuma1` and `perl`, and also `wget` (if downloading the PGI
compiler rather than using a tarball in the local build context).
For RHEL-based Linux distributions, the default values are `gcc`,
`gcc-c++`, `numactl-libs` and `perl`, and also `wget` (if
downloading the PGI compiler rather than using a tarball in the
local build context).

- __prefix__: The top level install prefix.  The default value is
`/opt/pgi`.

- __system_cuda__: Boolean flag to specify whether the PGI compiler
should use the system CUDA.  If False, the version(s) of CUDA
bundled with the PGI compiler will be installed.  The default
value is False.

- __tarball__: Path to the PGI compiler tarball relative to the local
build context.  The default value is empty.  If this is defined,
the tarball in the local build context will be used rather than
downloading the tarball from the web.

- __version__: The version of the PGI compiler to use.  Note this value
is currently only used when setting the environment and does not
control the version of the compiler downloaded.  The default value
is `19.10`.

__Examples__


```python
pgi(eula=True)
```

```python
pgi(eula=True, tarball='pgilinux-2017-1710-x86_64.tar.gz')
```

```python
p = pgi(eula=True)
openmpi(..., toolchain=p.toolchain, ...)
```


## runtime
```python
pgi.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
p = pgi(...)
Stage0 += p
Stage1 += p.runtime()
```

# pip
```python
pip(self, **kwargs)
```
The `pip` building block installs Python packages from PyPi.

__Parameters__


- __alternatives__: Boolean flag to specify whether to configure alternatives for `python` and `pip`.  RHEL-based 8.x distributions do not setup `python` by [default](https://developers.redhat.com/blog/2019/05/07/what-no-python-in-red-hat-enterprise-linux-8/).  The default is False.

- __ospackages__: List of OS packages to install prior to installing
PyPi packages.  For Ubuntu, the default values are `python-pip`,
`python-setuptools`, and `python-wheel` for Python 2.x and
`python3-pip`, `python3-setuptools`, and `python3-wheel` for
Python 3.x.  For RHEL-based distributions, the default
values are `python2-pip` for Python 2.x and `python3-pip` for
Python 3.x.

- __packages__: List of PyPi packages to install.  The default is
an empty list.

- __pip__: The name of the `pip` tool to use. The default is `pip`.

- __requirements__: Path to pip requirements file.  The default is
empty.

- __upgrade__: Boolean flag to control whether pip itself should be
upgraded prior to installing any PyPi packages.  The default is
False.

__Examples__


```python
pip(packages=['hpccm'])
```

```python
pip(packages=['hpccm'], pip='pip3')
```

```python
pip(requirements='requirements.txt')
```


# pmix
```python
pmix(self, **kwargs)
```
The `pmix` building block configures, builds, and installs the
[PMIX](https://github.com/openpmix/openpmix) component.

__Parameters__


- __check__: Boolean flag to specify whether the `make check` step
should be performed.  The default is False.

- __configure_opts__: List of options to pass to `configure`.  The
default is an empty list.

- __environment__: Boolean flag to specify whether the environment
(`CPATH`, `LD_LIBRARY_PATH`, and `PATH`) should be modified to
include PMIX. The default is True.

- __ldconfig__: Boolean flag to specify whether the PMIX library
directory should be added dynamic linker cache.  If False, then
`LD_LIBRARY_PATH` is modified to include the PMIX library
directory. The default value is False.

- __ospackages__: List of OS packages to install prior to configuring
and building.  For Ubuntu, the default values are `file`, `hwloc`,
`libevent-dev`, `make`, `tar`, and `wget`. For RHEL-based Linux
distributions, the default values are `file`, `hwloc`,
`libevent-devel`, `make`, `tar`, and `wget`.

- __prefix__: The top level install location.  The default value is
`/usr/local/pmix`.

- __toolchain__: The toolchain object.  This should be used if
non-default compilers or other toolchain options are needed.  The
default value is empty.

- __version__: The version of PMIX source to download.  The default value
is `3.1.4`.

__Examples__


```python
pmix(prefix='/opt/pmix/3.1.4', version='3.1.4')
```


## runtime
```python
pmix.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
p = pmix(...)
Stage0 += p
Stage1 += p.runtime()
```

# pnetcdf
```python
pnetcdf(self, **kwargs)
```
The `pnetcdf` building block downloads, configures, builds, and
installs the
[PnetCDF](http://cucis.ece.northwestern.edu/projects/PnetCDF/index.html)
component.

__Parameters__


- __check__: Boolean flag to specify whether the `make check` step
should be performed.  The default is False.

- __configure_opts__: List of options to pass to `configure`.  The
default values are `--enable-shared`.

- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH` and `PATH`) should be modified to include
PnetCDF. The default is True.

- __ldconfig__: Boolean flag to specify whether the PnetCDF library
directory should be added dynamic linker cache.  If False, then
`LD_LIBRARY_PATH` is modified to include the PnetCDF library
directory. The default value is False.

- __ospackages__: List of OS packages to install prior to configuring
and building.  The default values are `m4`, `make`, `tar`, and
`wget`.

- __prefix__: The top level install location.  The default value is
`/usr/local/pnetcdf`.

- __toolchain__: The toolchain object.  A MPI compiler toolchain must be
used.  The default is to use the standard MPI compiler wrappers,
e.g., `CC=mpicc`, `CXX=mpicxx`, etc.

- __version__: The version of PnetCDF source to download.  The default
value is `1.11.2`.

__Examples__


```python
pnetcdf(prefix='/opt/pnetcdf/1.10.0', version='1.10.0')
```

```python
ompi = openmpi(...)
pnetcdf(toolchain=ompi.toolchain, ...)
```


## runtime
```python
pnetcdf.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
p = pnetcdf(...)
Stage0 += p
Stage1 += p.runtime()
```

# python
```python
python(self, **kwargs)
```
The `python` building block installs Python from the upstream Linux
distribution.

__Parameters__


- __alternatives__: Boolean flag to specify whether to configure alternatives for `python` and `python-config` (if `devel` is enabled).  RHEL-based 8.x distributions do not setup `python` by [default](https://developers.redhat.com/blog/2019/05/07/what-no-python-in-red-hat-enterprise-linux-8/).  The default is False.

- __devel__: Boolean flag to specify whether to also install the Python
development headers and libraries.  The default is False.

- __python2__: Boolean flag to specify whether to install Python version
2.  The default is True.

- __python3__: Boolean flag to specify whether to install Python version
3.  The default is True.

__Examples__


```python
python()
```

```python
python(python3=False)
```


## runtime
```python
python.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
p = python(...)
Stage0 += p
Stage1 += p.runtime()
```

# scif
```python
scif(self, **kwargs)
```
The `scif` building blocks installs components using the
[Scientific Filesystem (SCI-F)](https://sci-f.github.io).

Other building blocks and / or primitives should be added to
the `scif` building block using the `+=` syntax.

If not generating a Singularity definition file, SCI-F should be
installed using the [`pip`](#pip) building block prior to this
building block.

If not generating a Singularity definition file, this module
creates SCI-F recipe files in the current directory (see also the
`file` parameter).

__Parameters__


- ___arguments__: Specify additional [Dockerfile RUN arguments](https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/experimental.md) (Docker specific).

- ___env__: Boolean flag to specify whether the general container
environment should be also be loaded when executing a SCI-F
`%appinstall` block.  The default is False (Singularity specific).

- __file__: The SCI-F recipe file name.  The default value is the name
parameter with the `.scif` suffix.

- __name__: The name to use to label the SCI-F application.  This
parameter is required.

- ___native__: Boolean flag to specify whether to use the native
Singularity support for SCI-F when generating Singularity
definition files.  The default is True (Singularity specific).

__Examples__


```python
pip(packages=['scif'])
s = scif(name='example')
s += openmpi(prefix='/scif/apps/example')
s += shell(commands=[...])
```


## runtime
```python
scif.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

The entire `/scif` directory is copied into the runtime stage
on the first call.  Subsequent calls do nothing.

__Examples__

```python
s = scif(...)
Stage0 += s
Stage1 += s.runtime()
```


# sensei
```python
sensei(self, **kwargs)
```
The `sensei` building block configures, builds, and installs the
[SENSEI](https://sensei-insitu.org) component.

The [CMake](#cmake) building block should be installed prior to
this building block.

In most cases, one or both of the [Catalyst](#catalyst) or
[Libsim](#libsim) building blocks should be installed.

If GPU rendering will be used then a
[cudagl](https://hub.docker.com/r/nvidia/cudagl) base image is
recommended.

__Parameters__


- __branch__: The branch of SENSEI to use.  The default value is
`v2.1.1`.

- __catalyst__: Flag to specify the location of the ParaView/Catalyst
installation, e.g., `/usr/local/catalyst`.  If set, then the
[Catalyst](#catalyst) building block should be installed prior to
this building block.  The default value is empty.

- __cmake_opts__: List of options to pass to `cmake`.  The default value
is `-DENABLE_SENSEI=ON`.

- __libsim__: Flag to specify the location of the VisIt/Libsim
installation, e.g., `/usr/local/visit`.  If set, then the
[Libsim](#libsim) building block should be installed prior to this
building block.  The `vtk` option should also be set.  The default
value is empty.

- __miniapps__: Boolean flag to specify whether the SENSEI mini-apps
should be built and installed.  The default is False.

- __ospackages__: List of OS packages to install prior to configuring
and building.  The default values are `ca-certificates`, `git`,
and `make`.

- __prefix__: The top level install location.  The default value is
`/usr/local/sensei`.

- __toolchain__: The toolchain object.  This should be used if
non-default compilers or other toolchain options are needed.  The
default is empty.

- __vtk__: Flag to specify the location of the VTK installation.  If
`libsim` is defined, this option must be set to the Libsim VTK
location, e.g.,
`/usr/local/visit/third-party/vtk/6.1.0/linux-x86_64_gcc-5.4/lib/cmake/vtk-6.1`. Note
that the compiler version is embedded in the Libsim VTK path.  The
compiler version may differ depending on which base image is used;
version 5.4 corresponds to Ubuntu 16.04. The default value is
empty.

__Examples__


```python
sensei(branch='v2.1.1', catalyst='/usr/local/catalyst',
       prefix='/opt/sensei')
```

```python
sensei(libsim='/usr/local/visit',
       vtk='/usr/local/visit/third-party/vtk/6.1.0/linux-x86_64_gcc-5.4/lib/cmake/vtk-6.1')
```


## runtime
```python
sensei.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__

```python
s = sensei(...)
Stage0 += s
Stage1 += s.runtime()
```

# slurm_pmi2
```python
slurm_pmi2(self, **kwargs)
```
The `slurm_pmi2` building block configures, builds, and installs
the PMI2 component from SLURM.

Note: this building block does not install SLURM itself.

__Parameters__


- __configure_opts__: List of options to pass to `configure`.  The
default is an empty list.

- __environment__: Boolean flag to specify whether the environment
(`CPATH` and `LD_LIBRARY_PATH`) should be modified to include
PMI2. The default is False.

- __ldconfig__: Boolean flag to specify whether the PMI2 library
directory should be added dynamic linker cache.  If False, then
`LD_LIBRARY_PATH` is modified to include the PMI2 library
directory. The default value is False.

- __ospackages__: List of OS packages to install prior to configuring
and building.  The default values are `bzip2`, `file`, `make`,
`perl`, `tar`, and `wget`.

- __prefix__: The top level install location.  The default value is
`/usr/local/slurm-pmi2`.

- __toolchain__: The toolchain object.  This should be used if
non-default compilers or other toolchain options are needed.  The
default value is empty.

- __version__: The version of SLURM source to download.  The default
value is `19.05.4`.

__Examples__


```python
slurm_pmi2(prefix='/opt/pmi', version='19.05.4')
```


## runtime
```python
slurm_pmi2.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
p = slurm_pmi2(...)
Stage0 += p
Stage1 += p.runtime()
```

# ucx
```python
ucx(self, **kwargs)
```
The `ucx` building block configures, builds, and installs the
[UCX](https://github.com/openucx/ucx) component.

An InfiniBand building block ([OFED](#ofed) or [Mellanox
OFED](#mlnx_ofed)) should be installed prior to this building
block.  One or all of the [gdrcopy](#gdrcopy), [KNEM](#knem), and
[XPMEM](#xpmem) building blocks should also be installed prior to
this building block.

__Parameters__


- __configure_opts__: List of options to pass to `configure`.  The
default values are `--enable-optimizations`, `--disable-logging`,
`--disable-debug`, `--disable-assertions`,
`--disable-params-check`, and `--disable-doxygen-doc`.

- __cuda__: Flag to control whether a CUDA aware build is performed.  If
True, adds `--with-cuda=/usr/local/cuda` to the list of
`configure` options.  If a string, uses the value of the string as
the CUDA path.  If the toolchain specifies `CUDA_HOME`, then that
path is used.  If False, adds `--without-cuda` to the list of
`configure` options.  The default value is an empty string.

- __environment__: Boolean flag to specify whether the environment
(`LD_LIBRARY_PATH` and `PATH`) should be modified to include
UCX. The default is True.

- __gdrcopy__: Flag to control whether gdrcopy is used by the build.  If
True, adds `--with-gdrcopy` to the list of `configure` options.
If a string, uses the value of the string as the gdrcopy path,
e.g., `--with-gdrcopy=/path/to/gdrcopy`.  If False, adds
`--without-gdrcopy` to the list of `configure` options.  The
default is an empty string, i.e., include neither `--with-gdrcopy`
not `--without-gdrcopy` and let `configure` try to automatically
detect whether gdrcopy is present or not.

- __knem__: Flag to control whether KNEM is used by the build.  If True,
adds `--with-knem` to the list of `configure` options.  If a
string, uses the value of the string as the KNEM path, e.g.,
`--with-knem=/path/to/knem`.  If False, adds `--without-knem` to
the list of `configure` options.  The default is an empty string,
i.e., include neither `--with-knem` not `--without-knem` and let
`configure` try to automatically detect whether KNEM is present or
not.

- __ldconfig__: Boolean flag to specify whether the UCX library
directory should be added dynamic linker cache.  If False, then
`LD_LIBRARY_PATH` is modified to include the UCX library
directory. The default value is False.

- __ofed__: Flag to control whether OFED is used by the build.  If True,
adds `--with-verbs` and `--with-rdmacm` to the list of `configure`
options.  If a string, uses the value of the string as the OFED
path, e.g., `--with-verbs=/path/to/ofed`.  If False, adds
`--without-verbs` and `--without-rdmacm` to the list of
`configure` options.  The default is an empty string, i.e.,
include neither `--with-verbs` not `--without-verbs` and let
`configure` try to automatically detect whether OFED is present or
not.

- __ospackages__: List of OS packages to install prior to configuring
and building.  For Ubuntu, the default values are `binutils-dev`,
`file`, `libnuma-dev`, `make`, and `wget`. For RHEL-based Linux
distributions, the default values are `binutils-devel`, `file`,
`make`, `numactl-devel`, and `wget`.

- __prefix__: The top level install location.  The default value is
`/usr/local/ucx`.

- __toolchain__: The toolchain object.  This should be used if
non-default compilers or other toolchain options are needed.  The
default value is empty.

- __version__: The version of UCX source to download.  The default value
is `1.5.2`.

- __xpmem__: Flag to control whether XPMEM is used by the build.  If
True, adds `--with-xpmem` to the list of `configure` options.  If
a string, uses the value of the string as the XPMEM path, e.g.,
`--with-xpmem=/path/to/xpmem`.  If False, adds `--without-xpmem`
to the list of `configure` options.  The default is an empty
string, i.e., include neither `--with-xpmem` not `--without-xpmem`
and let `configure` try to automatically detect whether XPMEM is
present or not.

__Examples__


```python
ucx(cuda=False, prefix='/opt/ucx/1.4.0', version='1.4.0')
```

```python
ucx(cuda='/usr/local/cuda', gdrcopy='/usr/local/gdrcopy',
    knem='/usr/local/knem', xpmem='/usr/local/xpmem')
```


## runtime
```python
ucx.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
u = ucx(...)
Stage0 += u
Stage1 += u.runtime()
```

# xpmem
```python
xpmem(self, **kwargs)
```
The `xpmem` building block builds and installs the user space
library from the [XPMEM](https://gitlab.com/hjelmn/xpmem)
component.

__Parameters__


- __branch__: The branch of XPMEM to use.  The default value is
`master`.

- __configure_opts__: List of options to pass to `configure`.  The
default values are `--disable-kernel-module`.

- __environment__: Boolean flag to specify whether the environment
(`CPATH`, `LD_LIBRARY_PATH` and `LIBRARY_PATH`) should be modified
to include XPMEM. The default is True.

- __ldconfig__: Boolean flag to specify whether the XPMEM library
directory should be added dynamic linker cache.  If False, then
`LD_LIBRARY_PATH` is modified to include the XPMEM library
directory. The default value is False.

- __ospackages__: List of OS packages to install prior to configuring
and building.  The default value are `autoconf`, `automake`,
`ca-certificates`, `file, `git`, `libtool`, and `make`.

- __prefix__: The top level install location.  The default value is
`/usr/local/xpmem`.

- __toolchain__: The toolchain object.  This should be used if
non-default compilers or other toolchain options are needed.  The
default is empty.

__Examples__


```python
xpmem(prefix='/opt/xpmem', branch='master')
```


## runtime
```python
xpmem.runtime(self, _from=u'0')
```
Generate the set of instructions to install the runtime specific
components from a build in a previous stage.

__Examples__


```python
x = xpmem(...)
Stage0 += x
Stage1 += x.runtime()
```

# yum
```python
yum(self, **kwargs)
```
The `yum` building block specifies the set of operating system
packages to install.  This building block should only be used on
images that use the Red Hat package manager (e.g., CentOS).

In most cases, the [`packages` building block](#packages) should
be used instead of `yum`.

__Parameters__


- __download__: Boolean flag to specify whether to download the rpm
packages instead of installing them.  The default is False.

- __download_directory__: The deb package download location. This
parameter is ignored if `download` is False. The default value is
`/var/tmp/yum_download`.

- __epel__: - Boolean flag to specify whether to enable the Extra
Packages for Enterprise Linux (EPEL) repository.  The default is
False.

- __extract__: Location where the downloaded packages should be
extracted. Note, this extracts and does not install the packages,
i.e., the package manager is bypassed. After the downloaded
packages are extracted they are deleted. This parameter is ignored
if `download` is False. If empty, then the downloaded packages are
not extracted. The default value is an empty string.

- __keys__: A list of GPG keys to import.  The default is an empty list.

- __ospackages__: A list of packages to install.  The default is an
empty list.

- __powertools__: Boolean flag to specify whether to enable the
PowerTools repository.  The default is False.  This parameter is
only recognized if the CentOS version is 8.x.

- __repositories__: A list of yum repositories to add.  The default is
an empty list.

- __scl__: - Boolean flag to specify whether to enable the Software
Collections (SCL) repository.  The default is False.

- __yum4__: Boolean flag to specify whether `yum4` should be used
instead of `yum`.  The default is False.  This parameter is only
recognized if the CentOS version is 7.x.

__Examples__


```python
yum(ospackages=['make', 'wget'])
```



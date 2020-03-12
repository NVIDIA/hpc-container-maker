"""
Basic development container image
"""

Stage0 += baseimage(image='ubuntu:18.04')

# GNU compilers
compiler = gnu()
Stage0 += compiler

# Additional development tools
Stage0 += packages(ospackages=['autoconf', 'autoconf-archive', 'automake',
                               'bzip2', 'ca-certificates', 'cmake', 'git',
                               'gzip', 'libtool', 'make', 'patch', 'xz-utils'])

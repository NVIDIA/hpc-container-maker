"""
Demonstrate how to include a recipe in another recipe
"""

# the gnu-devel recipe file must be in the same directory
hpccm.include('gnu-devel.py')

Stage0 += generic_build(branch='v1.3',
                        build=['make COMPILER=GNU'],
                        install=['cp clover_leaf /usr/local/bin'],
                        repository='https://github.com/UK-MAC/CloverLeaf_Serial.git')

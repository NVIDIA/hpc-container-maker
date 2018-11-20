# pylint: disable=invalid-name, too-few-public-methods
# pylint: disable=too-many-instance-attributes

"""SCIF building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from hpccm.building_blocks.packages import packages
from hpccm.common import container_type
from hpccm.primitives.comment import comment
from hpccm.primitives.copy import copy
from hpccm.primitives.runscript import runscript
from hpccm.primitives.shell import shell

import hpccm
import logging
import os

class scif():
    """SCIF building block"""
    initialized = False

    def __init__(self, **kwargs):
        """Initialize building block"""
        self.name = kwargs.get('name', '')
        self.__layers = []
        self.__separator = kwargs.get('separator', '\n\n')

        self.__entrypoint = kwargs.get('entrypoint', False)
        self.instructions = [comment("SCIF app {0}".format(self.name))]
        if hpccm.config.g_ctype == container_type.DOCKER and scif.initialized == False:
            # Install the scif-tool on first scif app
            self.instructions.extend([
                comment("Begin SCI-F installtion"),
                packages(ospackages=['python-pip', 'python-setuptools']),
                shell(commands=[
                  'pip install wheel',
                  'pip install scif==0.0.76'
                ]),
                comment("End SCI-F installtion")
            ])
            scif.initialized = True

    def __iadd__(self, layer):
        """Add the scif layer.  Allows "+=" syntax."""
        if isinstance(layer, list):
            for l in layer:
                if hasattr(l, '_app'):
                    l._app = self.name
                else:
                    logging.error('You have to use a building block which '
                                  'supports the _app-parameter!')
            self.__layers.extend(layer)
        else:
            if hasattr(layer, '_app'):
                layer._app = self.name
            else:
                logging.error('You have to use a building block which '
                              'supports the _app-parameter!')
            self.__layers.append(layer)
        return self

    def __str__(self):
        # SCIF recipe is always in Singularity syntax
        ct = hpccm.config.g_ctype
        hpccm.config.g_ctype = container_type.SINGULARITY
        layers_string = self.__separator.join(str(x) for x in self.__layers)
        # change type back
        hpccm.config.g_ctype = ct

        if hpccm.config.g_ctype == container_type.DOCKER:
            if hpccm.config.g_output_directory:
                scif_path = os.path.join(hpccm.config.g_output_directory,
                                         '{}.scif'.format(self.name))
                scif_file = open(scif_path, "w")
                scif_file.write(layers_string)
                scif_file.close()

                self.instructions.extend([
                    copy(src=[scif_path], dest='/scif/recipes/',
                         _mkdir=True),
                    shell(commands=[
                        'scif install /scif/recipes/{}.scif'.format(self.name)
                    ])
                ])
                if self.__entrypoint:
                    self.instructions.append(runscript(commands=[
                        'scif run {} \"$@\"'.format(self.name)]))

                return '\n'.join(str(x) for x in self.instructions)
            else:
                logging.error('No output directory specified but is required '
                              'for using scif() with Docker! Specify with '
                            'hpccm --out argument.')
        else:
            """String representation of the scif apps"""
            return "\n".join(str(x) for x in self.instructions) + "\n" + layers_string

    def runtime(self, _from='0'):
        """Install the runtime from a full build in a previous stage.  In this
           case there is no difference between the runtime and the
           full build."""
        return str(self)

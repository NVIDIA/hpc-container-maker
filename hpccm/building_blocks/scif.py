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

import hpccm.config
import logging
import os

class scif(object):
    """SCIF building block"""
    initialized = False

    def __init__(self, **kwargs):
        """Initialize building block"""
        self.name = kwargs.get('name', '')
        self.scif_version = kwargs.get('scif_version', '0.0.76')
        self.__layers = []
        self.__separator = kwargs.get('separator', '\n\n')

        self.__entrypoint = kwargs.get('entrypoint', False)
        self.instructions = [comment("SCIF app {0}".format(self.name))]
        if hpccm.config.g_ctype == container_type.DOCKER and not scif.initialized:
            # Install the scif-tool on first scif app
            self.instructions.extend([
                comment("Begin SCI-F installation"),
                packages(ospackages=['python-pip', 'python-setuptools']),
                shell(commands=[
                  'pip install wheel',
                  'pip install scif=={0}'.format(self.scif_version)
                ]),
                comment("End SCI-F installation")
            ])
            scif.initialized = True

        allowed_primitives = ["comment", "copy", "environment", "help",
                              "label", "runscript", "shell", "test"]
        self.__primitive_status = {i: False for i in allowed_primitives}

    def __iadd__(self, layer):
        """Add the scif layer.  Allows "+=" syntax."""
        if isinstance(layer, list):
            for l in layer:
                self.check_layer(l)
            self.__layers.extend(layer)
        else:
            self.check_layer(layer)
            self.__layers.append(layer)
        return self

    def check_layer(self, layer):
        class_name = type(layer).__name__
        if class_name not in self.__primitive_status:
            logging.exception(
                'You cannot add `{0}` to a scif! Use primitives which support '
                'the _app-parameter! I.e.: {1}'.format(class_name,
                    str(self.__primitive_status.keys())))

        if self.__primitive_status[class_name]:
            logging.exception(
                'Duplicate `{0}` primitive given for scif app. '
                'Each primitive is allowed just once!'.format(class_name))
            raise()  # TODO: the logging exception is not raised?!

        layer._app = self.name
        self.__primitive_status[class_name] = True


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
                    copy(src=[scif_path], dest='/scif/recipes/'),
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
            return "\n".join(str(x) for x in self.instructions) + "\n"\
                + layers_string

    def runtime(self, _from='0'):
        """Install the runtime from a full build in a previous stage.  In this
           case there is no difference between the runtime and the
           full build."""
        # TODO: this is fine as is, but it be more efficient to pip install scif
        #       and copy the /scif directory?
        return str(self)

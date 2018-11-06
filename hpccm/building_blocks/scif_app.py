# pylint: disable=invalid-name, too-few-public-methods
# pylint: disable=too-many-instance-attributes

"""SCIF app building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import logging
import os

from hpccm.common import container_type
from hpccm.primitives.copy import copy
from hpccm.primitives.environment import environment
from hpccm.primitives.label import label
from hpccm.primitives.raw import raw
from hpccm.primitives.runscript import runscript
from hpccm.primitives.shell import shell
import hpccm.config


class scif_app():
    """SCIF app building block"""

    def __init__(self, **kwargs):
        """Initialize building block"""

        self.env = kwargs.get('env')
        self.help = kwargs.get('help')
        self.install = kwargs.get('install')
        self.labels = kwargs.get('labels')
        self.name = kwargs.get('name')
        self.run = kwargs.get('run')
        self.test = kwargs.get('test')
        self.__entrypoint = kwargs.get('entrypoint', False)

        if not self.name:
            logging.error('No `name` argument specified but is required for '
                          'using scif_app()!')

        # SCIF format is always in Singularity syntax
        ct = hpccm.config.g_ctype
        hpccm.config.g_ctype = container_type.SINGULARITY
        instructions = []
        if self.env:
            instructions.append(environment(variables=self.env,
                                            _app=self.name))
        if self.help:
            instructions.append(raw(singularity='%apphelp {}\n    {}'.format(
                self.name, self.help)))
        if self.install:
            instructions.append(shell(commands=self.install, _app=self.name))
        if self.run:
            instructions.append(runscript(commands=['{} \"$@\"'.format(
                self.run)], _app=self.name))
        if self.labels:
            instructions.append(label(metadata=self.labels, _app=self.name))
        if self.test:
            instructions.append(raw(singularity='%apptest {}\n    {}'.format(
                self.name, self.test)))
        instructions_string = '\n'.join(str(x) for x in instructions)
        hpccm.config.g_ctype = ct

        if hpccm.config.g_output_directory:
            self.__scif_path = os.path.join(hpccm.config.g_output_directory,
                                            '{}.scif'.format(self.name))
            scif_file = open(self.__scif_path, "w")
            scif_file.write(instructions_string)
            scif_file.close()
        else:
            logging.error('No output directory specified but is required '
                          'for using scif_app()! Specify with hpccm --out '
                          'argument.')

    def __str__(self):
        if hpccm.config.g_output_directory:
            instructions = [
                copy(src=[self.__scif_path], dest='/scif/recipes/',
                     _mkdir=True),
                shell(commands=[
                    'scif install /scif/recipes/{}.scif'.format(self.name)
                ])
            ]
            if self.__entrypoint and self.run:
                instructions.append(runscript(commands=[
                    'scif run {} \"$@\"'.format(self.name)]))
            return '\n'.join(str(x) for x in instructions)
        else:
            logging
        return ''

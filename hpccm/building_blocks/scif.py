

# pylint: disable=invalid-name, too-few-public-methods
# pylint: disable=too-many-instance-attributes

"""SCIF building block"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from hpccm.building_blocks.packages import packages
from hpccm.primitives.comment import comment
from hpccm.primitives.runscript import runscript
from hpccm.primitives.shell import shell


class scif():
    """SCIF building block"""

    def __init__(self, **kwargs):
        """Initialize building block"""

        # Trouble getting MRO with kwargs working correctly, so just call
        # the parent class constructors manually for now.
        # super(python, self).__init__(**kwargs)

        self.__entrypoint = kwargs.get('entrypoint', False)

        self.instructions = [
            comment(__doc__, reformat=False),
            packages(ospackages=['python-pip', 'python-setuptools']),
            shell(commands=[
              'pip install wheel',
              'pip install scif==0.0.76'
            ])
        ]

        if self.__entrypoint:
            self.instructions.append(runscript(commands=['scif']))

    def __str__(self):
        """String representation of the building block"""
        return '\n'.join(str(x) for x in self.instructions)

    def runtime(self, _from='0'):
        """Install the runtime from a full build in a previous stage.  In this
           case there is no difference between the runtime and the
           full build."""
        return str(self)

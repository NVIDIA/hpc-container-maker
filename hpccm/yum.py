from .shell import shell


class yum(object):

    def __init__(self, **kwargs):
        self.__commands = []
        self.ospackages = kwargs.get('ospackages', [])
        self.opts = kwargs.get('opts', '')
        self.__setup()

    def __setup(self):
        if not self.ospackages:
            return
        install_cmd = 'yum install -y {}'.format(self.opts)
        self.__commands.append(' \\\n'.join([install_cmd.strip()] + ["    {}".format(pkg) for pkg in self.ospackages]))
        self.__commands.append('yum clean all')

    def __str__(self):
        return str(shell(commands=self.__commands))

from .shell import shell


class zypper(object):

    def __init__(self, **kwargs):
        self.__commands = []
        self.ospackages = kwargs.get('ospackages', [])
        self.opts = kwargs.get('opts', '')
        self.__setup()

    def __setup(self):
        if not self.ospackages:
            return
        install_cmd = 'zypper install -y {}'.format(self.opts)
        self.__commands.append(' \\\n'.join([install_cmd.strip()] + ["    {}".format(pkg) for pkg in self.ospackages]))

    def __str__(self):
        return str(shell(commands=self.__commands))

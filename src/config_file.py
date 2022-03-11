import re


class ConfigFile:
    """
    This class is used to read and write the GRUB config file.
    """
    _path = ""
    _values = dict()
    
    def __init__(self, path="/etc/default/grub"):
        """
        Initialize the ConfigFile instance.
        :param path: string containing the path to the GRUB config file
        """
        self._path = path
        self.load_file()

    def __getitem__(self, item):
        return self._values[item]
    
    def __setitem__(self, item, value):
        self._values[item] = value

    def set_path(self, new_path, load=False):
        self._path = new_path
        if load:
            self.load_file()

    def save_file(self):
        """Save the GRUB config file."""
        # TODO: actually save the file
        print("Saving config to: " + self._path)

    def load_file(self):
        """Load the GRUB config file"""
        self._values = dict()
        try:
            f = open(self._path)
        except IOError as err:
            print(err)
            return self._values
        else:
            lines = f.readlines()
            vlines = []
            for line in lines:
                if not re.match(r"^\s*$",line) and not re.match(r"^#.*$",line):
                    vlines.append(line.strip('\n'))
            lines = []
            while len(vlines) > 0:
                i = vlines.pop(0)
                i = re.sub(r"\s*#.*$","",i)
                while i.endswith('\\'):
                    try:
                        o = vlines.pop(0)
                    except IndexError:
                        o = ""
                    i = i.rstrip('\\') + o.strip()
                lines.append(i)

            for opt in lines:
                [name,val] = opt.split("=",1)
                self._values[name] = val.strip('"')

        return self._values


import re


class ConfigFile:
    path = ""
    values = dict()
    
    def __init__(self, path="/etc/default/grub"):
        self.path = path
        self.load_file()

    def __getitem__(self, item):
        return self.values[item]
    
    def __setitem__(self, item, value):
        self.values[item] = value

    def save_file(self):
        # TODO: actually save the file
        print("Saving config to: " + self.path)

    def load_file(self):
        self.values = dict()
        try:
            f = open(self.path)
        except IOError as err:
            print(err)
            return self.values
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
                self.values[name] = val.strip('"')

        return self.values


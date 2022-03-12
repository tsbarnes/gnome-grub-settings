import re

from gi.repository import GLib, GObject, Gio


class ConfigFile:
    """
    This class is used to read and write the GRUB config file.
    """
    _path = ""
    _values = dict()
    
    def __init__(self, window, path: str = "/etc/default/grub"):
        """
        Initialize the ConfigFile instance.
        :param path: string containing the path to the GRUB config file
        """
        self._window = window
        self._path = path
        self.load_file()

    def __getitem__(self, item: str):
        return self._values[item]
    
    def __setitem__(self, item: str, value: str):
        self._values[item] = value

    def mount_cb(self, gio_file, res):
        gio_file.mount_enclosing_volume_finish(res)
        try:
            file = open(self._path)
        except IOError as err:
            print(err)
            return
        else:
            lines: list[str] = file.readlines()
            file.close()

            for option in self._values.keys():
                found: bool = False
                for index in range(0, len(lines)):
                    line_contents: list[str] = lines[index].split("=")
                    if line_contents[0] == option:
                        lines[index] = option + "=\"" + self._values[option] + "\""
                        found = True
                if not found:
                    lines.append(option + "=\"{0}\"".format(self._values[option]))

            for index in range(0, len(lines)):
                lines[index] = lines[index].strip('\n')

            contents: str = '\n'.join(lines)
            print(contents)
            cancellable: Gio.Cancellable = Gio.Cancellable()
            data = GLib.Bytes.new(contents.encode('utf-8'))
            gio_file.replace_contents_bytes_async(
                data,
                None,
                False,
                Gio.FileCreateFlags.REPLACE_DESTINATION,
                cancellable,
                self.save_cb
            )

    def save_cb(self, gio_file: Gio.File, res: object):
        try:
            gio_file.replace_contents_finish(res)
        except GObject.GError as err:
            print(err)
            self._window.save_failed()
        else:
            self._window.save_success()

    def set_path(self, new_path, load=False):
        self._path = new_path
        if load:
            self.load_file()

    def save_file(self):
        """Save the GRUB config file."""
        try:
            gio_file: Gio.File = Gio.File.new_for_uri("admin://" + self._path)
            gio_file.mount_enclosing_volume(Gio.MountMountFlags.NONE, None, None, self.mount_cb)
        except GObject.GError as err:
            print(err)
            return

    def load_file(self):
        """Load the GRUB config file"""
        self._values = dict()
        try:
            file = open(self._path)
        except IOError as err:
            print(err)
            return self._values
        else:
            lines = file.readlines()
            value_lines = []
            for line in lines:
                if not re.match(r"^\s*$", line) and not re.match(r"^#.*$", line):
                    value_lines.append(line.strip('\n'))
            lines = []
            while len(value_lines) > 0:
                input_line = value_lines.pop(0)
                input_line = re.sub(r"\s*#.*$", "", input_line)
                while input_line.endswith('\\'):
                    try:
                        output_line = value_lines.pop(0)
                    except IndexError:
                        output_line = ""
                    input_line = input_line.rstrip('\\') + output_line.strip()
                lines.append(input_line)

            for option in lines:
                [name, value] = option.split("=", 1)
                self._values[name] = value.strip('"')

        return self._values

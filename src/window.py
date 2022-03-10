# window.py
#
# Copyright 2022 Sky Barnes
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gettext
import locale
import os
import re

from gi.repository import Gtk


locale.setlocale(locale.LC_ALL, "")
locale.bindtextdomain("gnome-grub-settings", "locale/")
gettext.bindtextdomain("gnome-grub-settings", "locale/")
gettext.textdomain("gnome-grub-settings")
_ = gettext.gettext
gettext.install("gnome-grub-settings", "locale/")


def parse_file(file):
    values = dict()
    try:
        f = open(file)
    except IOError:
        return values
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
            values[name] = val.strip('"')

    return values


class GrubSettingsWindow(object):
    def __init__(self, app):
        self.Application = app

        if os.getenv("FLATPAK_ID"):
            self.isFlatpak = True
        
        self.GrubConfig = parse_file('/var/run/host/etc/default/grub')
        self.GrubThemeLocations = [
            "/usr/share/grub/themes/",
            "/boot/grub/themes/",
        ]

        gui_resource = "/com/tsbarnes/GrubSettings/window.ui"
        self.builder = Gtk.Builder().new_from_resource(gui_resource)
        self.builder.connect_signals(self)

        self.MainWindow = self.builder.get_object("MainWindow")
        self.MainWindow.set_application(self.Application)
        self.MainWindow.show()

        self.HeaderBar = self.builder.get_object("HeaderBar")
        self.ThemeList = self.builder.get_object("ThemeList")

        self.ThemeListStore = Gtk.ListStore(str, str)
        self.ThemeList.set_model(self.ThemeListStore)
        self.ThemeList.set_id_column(0)
        
        self.ThemeListStore.append(["", "None",])
        
        for location in self.GrubThemeLocations:
            if self.isFlatpak:
                path = "/var/run/host" + location
            else:
                path = location
            try:
                for theme in os.listdir(path):
                    self.ThemeListStore.append([
                        os.path.join(location, theme, "theme.txt"),
                        theme,
                    ])
            except IOError as err:
                print(err)
        if not self.GrubConfig["GRUB_THEME"]:
            self.GrubConfig["GRUB_THEME"] = ""

        self.ThemeList.set_active_id(self.GrubConfig["GRUB_THEME"])

        renderer = Gtk.CellRendererText()
        self.ThemeList.pack_start(renderer, True)
        self.ThemeList.add_attribute(renderer, "text", 1)


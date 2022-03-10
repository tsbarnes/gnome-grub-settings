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

from gi.repository import Gtk
from dotenv import dotenv_values

locale.setlocale(locale.LC_ALL, "")
locale.bindtextdomain("gnome-grub-settings", "locale/")
gettext.bindtextdomain("gnome-grub-settings", "locale/")
gettext.textdomain("gnome-grub-settings")
_ = gettext.gettext
gettext.install("gnome-grub-settings", "locale/")


class GrubSettingsWindow(object):
    def __init__(self, app):
        self.Application = app
        
        self.GrubConfig = dotenv_values("/var/run/host/etc/default/grub")

        gui_resource = "/com/tsbarnes/GrubSettings/window.ui"
        self.builder = Gtk.Builder().new_from_resource(gui_resource)
        self.builder.connect_signals(self)

        self.MainWindow = self.builder.get_object("MainWindow")
        self.MainWindow.set_application(self.Application)
        self.MainWindow.show()

        self.HeaderBar = self.builder.get_object("HeaderBar")
        self.ThemeList = self.builder.get_object("ThemeList")

        self.ThemeListStore = Gtk.ListStore(str)
        self.ThemeList.set_model(self.ThemeListStore)
        
        self.ThemeListStore.append(["None",])
        for theme in os.listdir("/var/run/host/usr/share/grub/themes"):
            self.ThemeListStore.append([theme,])
        
        if self.GrubConfig.has_key("GRUB_THEME"):
            self.ThemeList.set_active(self.GrubConfig["GRUB_THEME"])

        renderer = Gtk.CellRendererText()
        self.ThemeList.pack_start(renderer, True)
        self.ThemeList.add_attribute(renderer, "text", 0)


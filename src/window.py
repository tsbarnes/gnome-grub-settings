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

from .config_file import ConfigFile


locale.setlocale(locale.LC_ALL, "")
locale.bindtextdomain("gnome-grub-settings", "locale/")
gettext.bindtextdomain("gnome-grub-settings", "locale/")
gettext.textdomain("gnome-grub-settings")
_ = gettext.gettext
gettext.install("gnome-grub-settings", "locale/")


def sort_themes(theme):
    return theme[1].lower()


class GrubSettingsWindow(object):
    def apply_button_clicked(self, button):
        self.Config.save_file()

    def save_success(self):
        self.NotificationLabel.set_text("Saved successfully")
        self.NotificationRevealer.set_reveal_child(True)

    def save_failed(self):
        self.NotificationLabel.set_text("Failed to save")
        self.NotificationRevealer.set_reveal_child(True)
    
    def notification_close_button_clicked(self, button):
        self.NotificationRevealer.set_reveal_child(False)

    def theme_list_changed(self, user_data):
        self.Config["GRUB_THEME"] = self.ThemeList.get_active_id()

    def command_line_defaults_changed(self, user_data):
        self.Config["GRUB_CMDLINE_LINUX_DEFAULT"] = self.CommandLineDefaultsEntry.get_text()

    def __init__(self, app):
        self.Application = app

        if os.getenv("FLATPAK_ID"):
            self.isFlatpak = True
            self.ConfigPath = "/var/run/host/etc/default/grub"
        else:
            self.isFlatpak = False
            self.ConfigPath = "/etc/default/grub"

        self.Config = ConfigFile(self, self.ConfigPath)
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

        self.NotificationRevealer = self.builder.get_object("NotificationRevealer")
        self.NotificationLabel = self.builder.get_object("NotificationLabel")
        self.NotificationCloseButton = self.builder.get_object("NotificationCloseButton")
        self.NotificationCloseButton.connect("clicked", self.notification_close_button_clicked)

        self.HeaderBar = self.builder.get_object("HeaderBar")

        self.ApplyButton = self.builder.get_object("ApplyButton")
        self.ApplyButton.connect("clicked", self.apply_button_clicked)

        self.CommandLineDefaultsEntry = self.builder.get_object("CommandLineDefaultsEntry")
        self.CommandLineDefaultsEntry.set_text(self.Config["GRUB_CMDLINE_LINUX_DEFAULT"])
        self.CommandLineDefaultsEntry.connect("changed", self.command_line_defaults_changed)

        self.ThemeList = self.builder.get_object("ThemeList")
        self.ThemeList.connect("changed", self.theme_list_changed)

        self.ThemeListStore = Gtk.ListStore(str, str)
        self.ThemeList.set_model(self.ThemeListStore)
        self.ThemeList.set_id_column(0)
        
        self.ThemeListStore.append(["", "None",])
        theme_list = dict()
        
        for location in self.GrubThemeLocations:
            if self.isFlatpak:
                path = "/var/run/host" + location
            else:
                path = location
            try:
                for theme in os.listdir(path):
                    theme_list[os.path.join(location, theme, "theme.txt")] = theme
            except IOError as err:
                print(err)

        for theme in sorted(theme_list.items(), key=sort_themes):
            self.ThemeListStore.append(theme)
            print("Found theme: " + theme[1] + " at " + theme[0])
        
        if not self.Config["GRUB_THEME"]:
            self.Config["GRUB_THEME"] = ""

        print("Current theme: " + self.Config["GRUB_THEME"])

        self.ThemeList.set_active_id(self.Config["GRUB_THEME"])

        renderer = Gtk.CellRendererText()
        self.ThemeList.pack_start(renderer, True)
        self.ThemeList.add_attribute(renderer, "text", 1)


﻿# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE
import vars
import tkMessageBox
import getpass
import os
import shelve

class defaults:
    version = "2.0.0_alpha"
    cl_path = 'C:/Users/' + getpass.getuser() + "/Documents/Star Wars - The Old Republic/CombatLogs"
    auto_ident = False
    server = ("thrantasquadron.tk", 83)
    auto_upl = False
    overlay = True
    opacity = 0.7
    size = "big"
    pos = "TL"

class settings():
    def __init__(self, file_name = "settings.db"):
        self.file_name = file_name
        vars.install_path = os.getcwd()
        if self.file_name not in os.listdir(vars.install_path):
            print "[DEBUG] Settings file could not be found. Creating a new file with default settings"
            # self.write_def()
        self.read_set()

    def read_set(self):
        settings_dict = shelve.open(self.file_name)
        self.version = settings_dict["version"]
        self.cl_path = settings_dict["cl_path"]
        self.auto_ident = settings_dict["auto_ident"]
        self.server = settings_dict["server"]
        self.auto_upl = settings_dict["auto_upl"]
        self.overlay = settings_dict["overlay"]
        self.opacity = settings_dict["opacity"]
        self.size = settings_dict["size"]
        self.pos = settings_dict["pos"]
        settings_dict.sync()
        settings_dict.close()

    def write_def(self):
        settings_dict = shelve.open(self.file_name)
        settings_dict["version"] = defaults.version
        settings_dict["cl_path"] = defaults.cl_path
        settings_dict["auto_ident"] = defaults.auto_ident
        settings_dict["server"] = defaults.server
        settings_dict["auto_upl"] = defaults.auto_upl
        settings_dict["overlay"] = defaults.overlay
        settings_dict["opacity"] = defaults.opacity
        settings_dict["size"] = defaults.size
        settings_dict["pos"] = defaults.pos
        settings_dict.sync()
        settings_dict.close()

    def write_set(self, version=defaults.version, cl_path=defaults.cl_path, 
                  auto_ident=defaults.auto_ident, server=defaults.server, 
                  auto_upl=defaults.auto_upl, overlay=defaults.overlay, 
                  opacity=defaults.opacity, size=defaults.size, pos=defaults.pos):
        settings_dict = shelve.open(self.file_name)
        settings_dict["version"] = version
        settings_dict["cl_path"] = cl_path
        settings_dict["auto_ident"] = auto_ident
        settings_dict["server"] = server
        settings_dict["auto_upl"] = auto_upl
        settings_dict["overlay"] = overlay
        settings_dict["opacity"] = opacity
        settings_dict["size"] = size
        settings_dict["pos"] = pos
        print settings_dict
        settings_dict.sync()
        settings_dict.close()
        self.read_set()
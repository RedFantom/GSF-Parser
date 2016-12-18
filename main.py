﻿# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE
import vars
import os

def new_window():
    import gui
    main_window = gui.main_window()

def set_install_path():
    vars.install_path = os.getcwd()

set_install_path()
import sys
import os

if __name__ == "__main__":
    import tkMessageBox
    import gui
    set_install_path()
    if sys.platform == "win32":
        main_window = gui.main_window()
    else:
        tkMessageBox.showerror("Fatal error", "Unix is not supported")


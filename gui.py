# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

# UI imports
import mtTkinter as tk
import ttk
# General imports
import os
import sys
# Own modules
import vars
import client
import overlay
import main
import threading
import fframe
import rtframe
import seframe

# Class that contains all code to start the parser
# Creates various frames and gets all widgets into place
# Main loop is started at the end
class main_window(tk.Tk):
    def __init__(self):
        # Initialize window
        tk.Tk.__init__(self)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.finished = False
        self.style = ttk.Style()
        self.update_style(start = True)
        self.set_icon()
        # Get the screen properties
        vars.screen_w = self.winfo_screenwidth()
        vars.screen_h = self.winfo_screenheight()
        vars.path = vars.set_obj.cl_path
        # Get the default path for CombatLogs and the Installation path
        self.default_path = vars.set_obj.cl_path
        # Set window properties and create a splash screen from the splash_screen class
        self.resizable(width = False, height = False)
        self.wm_title("GSF Parser")
        self.withdraw()
        vars.client_obj = client.client_conn()
        self.splash = overlay.boot_splash(self)
        # TODO Enable connecting to the server in a later phase
        if vars.set_obj.auto_upl or vars.set_obj.auto_ident:
            vars.client_obj.init_conn()
            print "[DEBUG] Connection initialized"
        self.splash.update_progress()
        self.geometry("800x425")
        # Add a notebook widget with various tabs for the various functions
        self.notebook = ttk.Notebook(self, height = 400, width = 800)
        self.file_tab_frame = ttk.Frame(self.notebook)
        self.realtime_tab_frame = ttk.Frame(self.notebook)
        self.share_tab_frame = ttk.Frame(self.notebook)
        self.settings_tab_frame = ttk.Frame(self.notebook)
        self.file_select_frame = fframe.file_frame(self.file_tab_frame, self)
        self.realtime_frame = rtframe.realtime_frame(self.realtime_tab_frame, self)
        self.middle_frame = fframe.middle_frame(self.file_tab_frame, self)
        self.ship_containment_frame = ttk.Frame(self.file_tab_frame, width = 300, height = 400)
        self.ship_frame = fframe.ship_frame(self.ship_containment_frame)
        self.settings_frame = seframe.settings_frame(self.settings_tab_frame, self)
        # Pack the frames and put their widgets into place
        self.file_select_frame.grid(column = 1, row = 1, rowspan = 4, columnspan = 1, sticky=tk.N+tk.S+tk.W+tk.E)
        self.file_select_frame.grid_widgets()
        self.middle_frame.grid(column = 2, columnspan = 2, rowspan = 2, row = 1, sticky=tk.N+tk.S+tk.W+tk.E, padx = 5)
        self.middle_frame.grid_widgets()
        self.realtime_frame.pack()
        self.realtime_frame.grid_widgets()
        self.ship_containment_frame.grid(column =  4, columnspan = 1, row = 1, rowspan = 4, sticky=tk.N+tk.S+tk.W+tk.E)
        self.ship_frame.pack(side = tk.RIGHT)
        self.settings_frame.grid_widgets()
        # Add the frames to the Notebook
        self.notebook.add(self.file_tab_frame, text = "File parsing")
        self.notebook.add(self.realtime_tab_frame, text = "Real-time parsing")
        # TODO Finish Sharing and Leaderboards tab
        # self.notebook.add(self.share_tab_frame, text = "Sharing and Leaderboards")
        self.notebook.add(self.settings_tab_frame, text = "Settings")
        # Update the files in the file_select frame
        self.notebook.grid(column = 0, row = 0)
        self.file_select_frame.add_files(silent = True)
        self.settings_frame.update_settings()
        # Give focus to the main window
        self.deiconify()
        print "[DEBUG] Finished"
        self.finished = True
        self.splash.destroy()
        # Start the main loop
        vars.main_window = self
        self.mainloop()

    def on_close(self):
        for obj in vars.needs_closing:
            obj.close()
        self.realtime_frame.parsing = False
        try:
            self.realtime_frame.stalker_obj.FLAG = False
        except:
            pass
        self.destroy()
        sys.exit()
        return

    def update_style(self, start=False):
        if sys.platform == "win32":
            print self.tk.call('package', 'require', 'tile-themes')
            self.styles = list(self.tk.call("ttk::themes"))
            try:
                self.style.theme_use(vars.set_obj.style)
            except AttributeError:
                try:
                    self.style.theme_use("plastik")
                    print "[DEBUG] Attribute Error: style set to plastik"
                except:
                    print "[DEBUG] Theme plastik is not available. Using default."
                    self.style.theme_use("default")
            self.style.configure('.', font=("Calibri", 10))
            self.style.configure('.', foreground='#8B0000')
            if not start:
                self.destroy()
                main.new_window()

    def set_icon(self):
        try:
            self.iconbitmap(default=os.path.dirname(os.path.realpath(__file__))+"\\icon.ico")
        except:
            print "[DEBUG] No icon found, is this from the GitHub repo?"
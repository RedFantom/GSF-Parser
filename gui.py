# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
import tkinter as tk
import tkinter.ttk as ttk
import os
import variables
from tools import client
import main
from frames import fileframe, resourcesframe, sharingframe, graphsframe, toolsframe
from frames import settingsframe, realtimeframe, buildframe, charactersframe
from frames import shipframe, statsframe
from toplevels.splashscreens import BootSplash


# Class that contains all code to start the parser
# Creates various frames and gets all widgets into place
# Main loop is started at the end
class MainWindow(tk.Tk):
    """
    Child class of tk.Tk that creates the main windows of the parser. Creates all frames that are necessary for the
    various functions of the parser an
    """

    def __init__(self):
        # Initialize window
        tk.Tk.__init__(self)
        dpi_value = self.winfo_fpixels('1i')
        self.tk.call('tk', 'scaling', '-displayof', '.', dpi_value / 72.0)
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.finished = False
        variables.main_window = self
        self.style = ttk.Style()
        self.set_icon()
        variables.color_scheme.set_scheme(variables.settings_obj.event_scheme)
        # Get the screen properties
        variables.screen_w = self.winfo_screenwidth()
        variables.screen_h = self.winfo_screenheight()
        variables.path = variables.settings_obj.cl_path
        self.update_style(start=True)
        # Get the default path for CombatLogs and the Installation path
        self.default_path = variables.settings_obj.cl_path
        # Set window properties and create a splash screen from the splash_screen class
        self.resizable(width=False, height=False)
        self.wm_title("GSF Parser")
        self.withdraw()
        variables.client_obj = client.ClientConnection()
        self.splash = BootSplash(self)
        # TODO Enable connecting to the server in a later phase
        if variables.settings_obj.auto_upl or variables.settings_obj.auto_ident:
            variables.client_obj.init_conn()
            print("[DEBUG] Connection initialized")
        # self.splash.update_progress()
        self.geometry("800x425")
        # Add a notebook widget with various tabs for the various functions
        self.notebook = ttk.Notebook(self, height=420, width=800)
        self.file_tab_frame = ttk.Frame(self.notebook)
        self.realtime_tab_frame = ttk.Frame(self.notebook)
        self.share_tab_frame = sharingframe.SharingFrame(self.notebook)
        self.settings_tab_frame = ttk.Frame(self.notebook)
        self.file_select_frame = fileframe.FileFrame(self.file_tab_frame, self)
        self.realtime_frame = realtimeframe.RealtimeFrame(self.realtime_tab_frame, self)
        self.middle_frame = statsframe.StatsFrame(self.file_tab_frame, self)
        self.ship_frame = shipframe.ShipFrame(self.file_tab_frame)
        self.settings_frame = settingsframe.SettingsFrame(self.settings_tab_frame, self)
        self.graphs_frame = graphsframe.GraphsFrame(self.notebook, self)
        self.resources_frame = resourcesframe.ResourcesFrame(self.notebook, self)
        self.characters_frame = charactersframe.CharactersFrame(self.notebook)
        self.builds_frame = buildframe.BuildsFrame(self.notebook)
        self.toolsframe = toolsframe.ToolsFrame(self.notebook)
        # Pack the frames and put their widgets into place
        self.file_select_frame.grid(column=1, row=1, sticky="nswe")
        self.file_select_frame.grid_widgets()
        self.middle_frame.grid(column=2, row=1, sticky="nswe", padx=5, pady=5)
        self.middle_frame.grid_widgets()
        self.realtime_frame.pack()
        self.realtime_frame.grid_widgets()
        self.ship_frame.grid(column=3, row=1, sticky="nswe")
        self.ship_frame.grid_widgets()
        self.settings_frame.grid_widgets()
        self.graphs_frame.grid(column=0, row=0)
        self.graphs_frame.grid_widgets()
        self.resources_frame.grid()
        self.builds_frame.grid_widgets()
        self.builds_frame.grid()
        self.characters_frame.grid()
        self.characters_frame.grid_widgets()
        self.toolsframe.grid_widgets()
        # Add the frames to the Notebook
        self.notebook.add(self.file_tab_frame, text="File parsing")
        self.notebook.add(self.realtime_tab_frame, text="Real-time parsing")
        self.notebook.add(self.characters_frame, text="Characters")
        self.notebook.add(self.builds_frame, text="Builds")
        self.notebook.add(self.graphs_frame, text="Graphs")
        self.notebook.add(self.share_tab_frame, text="Sharing")
        self.notebook.add(self.resources_frame, text="Resources")
        self.notebook.add(self.toolsframe, text="Tools")
        self.notebook.add(self.settings_tab_frame, text="Settings")
        # Update the files in the file_select frame
        self.notebook.grid(column=0, row=0)
        self.file_select_frame.add_files(silent=True)
        self.settings_frame.update_settings()
        # Give focus to the main window
        self.deiconify()
        self.finished = True
        self.splash.destroy()
        # Start the main loop

    def update_style(self, start=False):
        old_dir = os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        try:
            self.tk.eval("source theme/arc.tcl")
        except tk.TclError:
            print("Error evaluating arc.tcl")
        os.chdir(old_dir)
        print((list(self.tk.call("ttk::themes"))))
        try:
            self.style.theme_use("arc")
        except tk.TclError as e:
            print("[DEBUG] Theme arc is not available. Using default.")
            print(e)
            self.style.theme_use("vista")
        self.style.configure('.', font=("Calibri", 10))
        self.style.configure('TButton', anchor="w")
        self.style.configure('Toolbutton', anchor="w")
        try:
            self.style.configure('.', foreground=variables.settings_obj.color)
        except AttributeError:
            self.style.configure('.', foreground='#8B0000')
        if not start:
            self.destroy()
            main.new_window()

    def set_icon(self):
        try:
            self.iconbitmap(default=os.path.dirname(os.path.realpath(__file__)) + "\\assets\\logos\\icon_" +
                                    variables.settings_obj.logo_color + ".ico")
        except:
            print("[DEBUG] No icon found, is this from the GitHub repo?")

    def exit(self):
        """
        Function to cancel any running tasks and call any funtions to save the data in use before actually closing the
        GSF Parser
        :return: SystemExit(0)
        """
        exit()

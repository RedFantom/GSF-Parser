﻿# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

# UI imports
try:
     import mtTkinter as tk
except ImportError:
     import Tkinter as tk
from PIL import ImageTk, Image
import ttk
import tkMessageBox
# General imports
import os
import sys
import tempfile
# Own modules
import vars
import statistics

class splash_screen(tk.Toplevel):
    def __init__(self, window, boot=False, max=None, title="GSF Parser"):
        tk.Toplevel.__init__(self, window)
        self.grab_set()
        self.title(title)
        self.label = ttk.Label(self, text = "Working...")
        self.label.pack()
        self.progress_bar = ttk.Progressbar(self, orient = "horizontal", length = 300, mode = "determinate")
        self.progress_bar.pack()
        try:
            list = os.listdir(vars.set_obj.cl_path)
        except WindowsError:
            print "[DEBUG] Error changing directory"
            tkMessageBox.showerror("Error", "The directory set in the settings cannot be accessed.")
            return
        except:
            print "[DEBUG] Running on UNIX, functionality disabled"
            return
        files = []
        for file in list:
            if file.endswith(".txt"):
                files.append(file)
        vars.files_done = 0
        if not max:
            self.amount_files = len(files)
        else:
            self.amount_files = max
        if(self.amount_files >= 50 and boot):
            tkMessageBox.showinfo("Notice", "You currently have more than 50 CombatLogs in your CombatLogs folder. "+\
                                  "You may want to archive some of your %s CombatLogs in order to speed up the parsing "+\
                                  "program and the startup times." % self.amount_files)
        self.progress_bar["maximum"] = self.amount_files
        self.progress_bar["value"] = 0
        self.update()

    def update_progress(self):
        self.progress_bar["value"] = vars.files_done
        self.update()

class overlay(tk.Toplevel):
    def __init__(self, window):
        tk.Toplevel.__init__(self, window)
        self.update_position()
        if sys.platform == "win32":
            try:
                with open(tempfile.gettempdir().replace("temp", "") + "/SWTOR/swtor/settings/client_settings.ini", "r") as swtor:
                    if "D3DFullScreen = true" in swtor:
                        tkMessageBox.showerror("Error", "The overlay cannot be shown with the current SWTOR settings. "+\
                                               "Please set SWTOR to Fullscreen (windowed) in the Graphics settings.")
            except IOError:
                tkMessageBox.showerror("Error", "The settings file for SWTOR cannot be found. Is SWTOR correctly installed?")
        print "[DEBUG] Setting overlay font to: ", (vars.set_obj.overlay_tx_font, vars.set_obj.overlay_tx_size)
        if vars.set_obj.size == "big":
            self.text_label = ttk.Label(self, text = "Damage done:\nDamage taken:\nHealing recv:\nSelfdamage:\nSpawns:",
                                        justify = tk.LEFT, font = (vars.set_obj.overlay_tx_font, int(vars.set_obj.overlay_tx_size)),
                                        foreground = vars.set_obj.overlay_tx_color, background = vars.set_obj.overlay_bg_color)
        elif vars.set_obj.size == "small":
            self.text_label = ttk.Label(self, text = "DD:\nDT:\nHR:\nSD:", justify = tk.LEFT,
                                        font = (vars.set_obj.overlay_tx_font, int(vars.set_obj.overlay_tx_size)),
                                        foreground = vars.set_obj.overlay_tx_color, background = vars.set_obj.overlay_bg_color)
        else:
            raise ValueError("Size setting not valid.")
        self.stats_var = tk.StringVar()
        self.stats_label = ttk.Label(self, textvariable = self.stats_var, justify = tk.RIGHT,
                                     font = (vars.set_obj.overlay_tx_font, int(vars.set_obj.overlay_tx_size)),
                                     foreground = vars.set_obj.overlay_tx_color, background = vars.set_obj.overlay_bg_color)
        self.text_label.pack(side=tk.LEFT)
        self.stats_label.pack(side=tk.RIGHT)
        self.configure(background = vars.set_obj.overlay_bg_color)
        self.wm_attributes("-transparentcolor", vars.set_obj.overlay_tr_color)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", vars.set_obj.opacity)

    def update_position(self):
        if vars.set_obj.size == "big":
            h_req = (int(vars.set_obj.overlay_tx_size) * 1.6) * 5
            w_req = ((int(vars.set_obj.overlay_tx_size) / 1.5) + 2 ) * (14 + 6)
        elif vars.set_obj.size == "small":
            h_req = (int(vars.set_obj.overlay_tx_size) * 1.6) * 4
            w_req = ((int(vars.set_obj.overlay_tx_size) / 1.5) + 2) * (4 + 6)
        else:
            raise
        if vars.set_obj.pos == "TL":
            pos_c = "+0+0"
        elif vars.set_obj.pos == "BL":
            pos_c = "+0+%s" % (int(vars.screen_h) - int(h_req))
        elif vars.set_obj.pos == "TR":
            pos_c = "+%s+0" % (int(vars.screen_w) - int(w_req))
        elif vars.set_obj.pos == "BR":
            pos_c = "+%s+%s" % (int(vars.screen_w) - int(w_req), int(vars.screen_h) - int(h_req))
        else:
            raise ValueError("vars.set_obj.pos not valid")
        self.wm_geometry("%sx%s" % (int(w_req), int(h_req))+ pos_c)
        print "[DEBUG] Overlay position set to: ", "%sx%s" % (int(w_req), int(h_req))+ pos_c

class privacy(tk.Toplevel):
    def __init__(self, window):
        tk.Toplevel.__init__(self, window)
        privacy = vars.client_obj.get_privacy()
        privacy_listbox = tk.Listbox(self, height = 10, width = 30)
        privacy_listbox.pack(side=tk.LEFT)
        privacy_scroll = ttk.Scrollbar(self, orient = tk.VERTICAL, command = privacy_listbox.yview)
        privacy_listbox.config(yscrollcommand=privacy_scroll.set)
        if privacy == -1:
            self.destroy()
            return
        try:
            privacy_list = list(privacy)
        except:
            tkMessageBox.showerror("Error", "Data in privacy statement received is not valid.")
            return
        index = 0
        for line in privacy_list:
            privacy_listbox.insert(0, line)
            index += 1

class boot_splash(tk.Toplevel):
    def __init__(self, window):
        tk.Toplevel.__init__(self, window)
        self.title("GSF Parser: Starting...")
        print vars.set_obj.logo_color
        try:
            self.logo = ImageTk.PhotoImage(Image.open(os.path.dirname(os.path.realpath(__file__)) + "\\assets\\logo_" + \
                                                      vars.set_obj.logo_color + ".png"))
            self.panel = ttk.Label(self, image = self.logo)
            self.panel.pack()
        except:
            print "[DEBUG] No logo.png found in the home folder."
        self.window = window
        self.label_var = tk.StringVar()
        self.label_var.set("Connecting to specified server...")
        self.label = ttk.Label(self, textvariable = self.label_var)
        self.label.pack()
        self.progress_bar = ttk.Progressbar(self, orient = "horizontal", length = 462, mode = "determinate")
        self.progress_bar.pack()
        try:
            directory = os.listdir(window.default_path)
        except WindowsError:
            tkMessageBox.showerror("Error", "Error accessing directory set in settings. Please check your settings.")
            directory = []
        files = []
        for file in directory:
            if file.endswith(".txt"):
                files.append(file)
        vars.files_done = 0
        self.amount_files = len(files)
        '''
        if self.amount_files >= 50:
            tkMessageBox.showinfo("Notice", "You currently have more than 50 CombatLogs in your CombadwLogs folder. "+\
            "You may want to archive some of your %s CombatLogs in order to speed up the parsing program and the "+\
            "startup times." % self.amount_files)
        '''
        self.progress_bar["maximum"] = self.amount_files
        self.progress_bar["value"] = 0
        self.update()
        self.done = False

    def update_progress(self):
        if vars.files_done != self.amount_files:
            self.label_var.set("Parsing the files...")
            self.progress_bar["value"] = vars.files_done
            self.update()
        else:
            return

class conn_splash(tk.Toplevel):
    def __init__(self, window=vars.main_window):
        tk.Toplevel.__init__(self, window)
        self.window = window
        self.FLAG = False
        self.title("GSF Parser: Connecting...")
        self.label = ttk.Label(self, text = "Connecting to specified server...")
        self.label.pack()
        self.conn_bar =  ttk.Progressbar(self, orient = "horizontal", length = 300, mode = "indeterminate")
        self.conn_bar.pack()
        self.window.after(500, self.connect)

    def connect(self):
        if not self.FLAG:
            self.update()
            self.window.after(500, self.connect)
        else:
            return


class events_view(tk.Toplevel):
    def __init__(self, window, spawn, player):
        tk.Toplevel.__init__(self, window)
        self.title("GSF Parser: Events for spawn on %s of match started at %s" % (vars.spawn_timing, vars.match_timing))
        self.listbox = tk.Listbox(self, width=105, height=15, font=("Consolas", 10))
        self.scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command =self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scroll.set)
        self.listbox.grid(column = 1, row = 0, sticky=tk.N+tk.S+tk.W+tk.E)
        self.scroll.grid(column = 2, row = 0, sticky=tk.N+tk.S+tk.W+tk.E)
        self.resizable(width = False, height = False)
        try:
            for line in spawn:
                event = statistics.print_event(line, vars.spawn_timing, player)
                if event is not None:
                    self.listbox.insert(tk.END, event)
        except TypeError:
            self.destroy()



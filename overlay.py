# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

# UI imports
import Tkinter as tk
import ttk
# General imports
import os
# Own modules
import vars
import frames

class splash_screen(tk.Toplevel):
    def __init__(self, window):
        tk.Toplevel.__init__(self, window)
        self.label = tk.Label(self, text = "Working...")
        self.label.pack()
        self.progress_bar = ttk.Progressbar(self, orient = "horizontal", length = 300, mode = "determinate")
        self.progress_bar.pack()
        list = os.listdir(window.default_path)
        files = []
        for file in list:
            if file.endswith(".txt"):
                files.append(file)               
        self.amount_files = len(files)
        self.progress_bar["maximum"] = self.amount_files
        self.progress_bar["value"] = 0
        self.update()

    def update_progress(self):
        self.progress_bar["value"] = vars.files_done
        self.update()

class overlay(tk.Toplevel):
    def __init__(self, window):
        tk.Toplevel.__init__(self, window)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.7)
        self.overrideredirect(True)
        self.wm_geometry("200x75+0+0")
        self.stats_var = tk.StringVar()
        self.stats_label = tk.Label(self, textvariable = self.stats_var, justify = tk.RIGHT)
        self.text_label = tk.Label(self, text = "Damage done:\nDamage taken:\nHealing recv:\nSelfdamage:\n", justify = tk.LEFT)
        # self.stats_label.config(font=("Courier", 44))
        self.text_label.pack(side=tk.LEFT)
        self.stats_label.pack(side=tk.RIGHT)
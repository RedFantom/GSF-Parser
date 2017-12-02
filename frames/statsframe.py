# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
import tkinter as tk
import tkinter.ttk as ttk
from widgets.time_view import TimeView
from widgets.timeline import TimeLine
from collections import OrderedDict


class StatsFrame(ttk.Frame):
    """
    A simple frame containing a notebook with three tabs to show statistics and information to the user
    Main frame:
    ----------------------------------
    |  _____ _____ _____             |
    | |_____|_____|_____|___________ |
    | | frame to display            ||
    | |_____________________________||
    ----------------------------------

    Statistics tab:
    ----------------------------------
    | list                           |
    | of                             |
    | stats                          |
    ----------------------------------

    Enemies tab:
    -----------------------------
    | Help string               |
    | ______ ______ ______ ____ |
    | |enem| |dmgd| |dmgt| |/\| |
    | |enem| |dmgd| |dmgt| |||| |
    | |enem| |dmgd| |dmgt| |\/| |
    | |____| |____| |____| |__| |
    -----------------------------

    Abilities tab:
    -----------------------------
    | ability              |/\| |
    | ability              |||| |
    | ability              |\/| |
    -----------------------------
    """

    def __init__(self, root_frame, main_window):
        """
        Set up all widgets and variables. StringVars can be manipulated by the file frame,
        so that frame can set the statistics to be shown in this frame. Strings for Tkinter
        cannot span multiple lines!
        :param root_frame:
        :param main_window:
        """
        ttk.Frame.__init__(self, root_frame)
        self.window = main_window
        self.notebook = ttk.Notebook(self, width=580, height=360)
        # Create parent frames
        self.stats_frame = ttk.Frame(self.notebook)
        self.events_frame = ttk.Frame(self.notebook)
        self.timeline_frame = ttk.Frame(self.notebook)
        self.abilities_frame = ttk.Frame(self.notebook)
        self.enemies_frame = ttk.Frame(self.notebook)
        self.screen_frame = ttk.Frame(self.notebook)
        # Add notebook frames
        self.notebook.add(self.stats_frame, text="Statistics")
        self.notebook.add(self.events_frame, text="Events")
        self.notebook.add(self.timeline_frame, text="TimeLine")
        self.notebook.add(self.abilities_frame, text="Abilities")
        self.notebook.add(self.enemies_frame, text="Enemies")
        # self.notebook.add(self.screen_frame, text="Screen parsing")
        # Create widgets for statistics frame
        self.statistics_label_var = tk.StringVar()
        string = "Character name:\nDamage dealt to\nDamage dealt:\nDamage taken:\nDamage ratio:\nSelfdamage:\n" \
                 "Healing received:\nHit count:\nCritical count:\nCritical Percentage:\nDeaths:\nDuration:\nDPS:"
        self.statistics_label_var.set(string)
        self.statistics_label = ttk.Label(self.stats_frame, textvariable=self.statistics_label_var, justify=tk.LEFT,
                                          wraplength=145)
        self.statistics_numbers_var = tk.StringVar()
        self.statistics_label.setvar()
        self.statistics_numbers = ttk.Label(self.stats_frame, textvariable=self.statistics_numbers_var,
                                            justify=tk.LEFT, wraplength=145)
        self.notice_label = ttk.Label(self.stats_frame, text="\n\n\n\nThe damage dealt for bombers can not be " +
                                                             "accurately calculated due to CombatLog limitations, "
                                                             "as damage dealt by bombs is not recorded.",
                                      justify=tk.LEFT, wraplength=290)
        # Create widgets for enemies frame
        self.enemies_treeview = ttk.Treeview(self.enemies_frame)
        self.enemies_scrollbar = ttk.Scrollbar(self.enemies_frame, command=self.enemies_treeview.yview)
        self.enemies_label = ttk.Label(
            self.enemies_frame, font=("default", 10),
            text="This Treeview contains a list of all enemy ID numbers that you encountered "
                 "during the selected game period, together with each of their damage taken "
                 "from you and damage dealt to you. This is calculated using the CombatLogs only.\n"
                 "Please note that Bombers do not have the damage dealt by bombs recorded, "
                 "due to CombatLog limitations.",
            justify=tk.LEFT, wraplength=200
        )
        self.setup_enemy_treeview()
        # Create widgets for abilities frame
        self.abilities_treeview = ttk.Treeview(self.abilities_frame)
        self.abilities_scrollbar = ttk.Scrollbar(self.abilities_frame, command=self.abilities_treeview.yview)
        self.setup_ability_treeview()
        self.abilities_label = ttk.Label(
            self.abilities_frame, font=("default", 10), justify=tk.LEFT, wraplength=200,
            text="In this Treeview you can see each ability that you used in the specified time period, together with "
                 "the amount of times it was activated. This list may include abilities triggered by the GSF system, "
                 "which you have no control over."
        )
        # Create widgets for screen parsing frame
        self.screen_label_var = tk.StringVar()
        self.screen_label = ttk.Label(self.screen_frame, textvariable=self.screen_label_var, justify=tk.LEFT,
                                      wraplength=295)
        # Create widgets for events frame
        self.time_view = TimeView(self.events_frame, height=9)
        self.time_scroll = ttk.Scrollbar(self.events_frame, command=self.time_view.yview)
        self.time_view.config(yscrollcommand=self.time_scroll.set)
        # Create widgets for timeline frame
        categories = OrderedDict()
        categories["primaries"] = {"text": "Primary Weapon", "foreground": "#ff6666", "font": ("default", 11)}
        categories["secondaries"] = {"text": "Secondary Weapon", "foreground": "#ff3333", "font": ("default", 11)}
        categories["shields_front"] = {"text": "Shields Front", "foreground": "green", "font": ("default", 11)}
        categories["shields_rear"] = {"text": "Shields Rear", "foreground": "green", "font": ("default", 11)}
        categories["hull"] = {"text": "Hull Health", "foreground": "brown", "font": ("default", 11)}
        categories["systems"] = {"text": "Systems", "foreground": "#668cff", "font": ("default", 11)}
        categories["engines"] = {"text": "Engines", "foreground": "#b380ff", "font": ("default", 11)}
        categories["shields"] = {"text": "Shields", "foreground": "#8cac20", "font": ("default", 11)}
        categories["copilot"] = {"text": "CoPilot", "foreground": "#17a3ff", "font": ("default", 11)}
        categories["tracking"] = {"text": "Tracking", "foreground": "#ffcc00", "font": ("default", 11)}
        categories["wpower"] = {"text": "Weapon Power", "foreground": "#ff9933", "font": ("default", 11)}
        categories["epower"] = {"text": "Engine Power", "foreground": "#751aff", "font": ("default", 11)}
        self.time_line = TimeLine(
            self.timeline_frame, marker_change_category=False, marker_allow_overlap=False, marker_move=False,
            marker_font=("default", 11), marker_background="white", marker_border=1, marker_outline="black",
            marker_snap_to_ticks=False, width=350, height=280, background="#f5f6f7", categories=categories,
            unit="m", start=0.0, finish=3.0, resolution=0.005
        )

    def setup_timeline(self):
        """
        Setup the TimeLine widget
        """
        self.time_line

    def setup_enemy_treeview(self):
        """
        Setup the enemies treeview
        """
        self.enemies_treeview.config(yscrollcommand=self.enemies_scrollbar.set)
        self.enemies_treeview.config(columns=("Damage dealt", "Damage taken"))
        self.enemies_treeview["show"] = ("tree", "headings")
        self.enemies_treeview.column("#0", width=120, anchor="w")
        self.enemies_treeview.column("Damage dealt", width=80, anchor="e")
        self.enemies_treeview.column("Damage taken", width=80, anchor="e")
        command = lambda: self.treeview_sort_column(self.enemies_treeview, "Enemy name/ID", False, "str")
        self.enemies_treeview.heading("#0", text="Enemy name/ID", command=command)
        command = lambda: self.treeview_sort_column(self.enemies_treeview, "Damage dealt", False, "int")
        self.enemies_treeview.heading("Damage dealt", text="Damage dealt", command=command)
        command = lambda: self.treeview_sort_column(self.enemies_treeview, "Damage taken", False, "int")
        self.enemies_treeview.heading("Damage taken", text="Damage taken", command=command)
        self.enemies_treeview.config(height=14)

    def setup_ability_treeview(self):
        """
        Setup the abilities treeview
        """
        self.abilities_treeview.config(yscrollcommand=self.abilities_scrollbar.set)
        self.abilities_treeview.config(columns=("Times used",))
        self.abilities_treeview["show"] = ("tree", "headings")
        self.abilities_treeview.column("#0", width=200)
        self.abilities_treeview.config(height=14)
        self.abilities_treeview.column("Times used", width=80, anchor=tk.E)
        command = lambda: self.treeview_sort_column(self.abilities_treeview, "Times used", False, "int")
        self.abilities_treeview.heading("Times used", text="Times used", command=command)
        command = lambda: self.treeview_sort_column(self.abilities_treeview, "#0", False, "str")
        self.abilities_treeview.heading("#0", text="Ability", command=command)

    def grid_widgets(self):
        """
        Put all widgets in the right place
        """
        self.abilities_treeview.grid(column=0, row=0, pady=5, padx=5)
        self.abilities_scrollbar.grid(column=1, row=0, sticky="ns", pady=5)
        self.abilities_label.grid(column=2, row=0, sticky="nwe", padx=5, pady=5)
        self.notebook.grid(column=0, row=0, columnspan=4, sticky="nwe")
        self.statistics_label.grid(column=0, row=2, columnspan=2, sticky="nswe", padx=(5, 0), pady=5)
        self.statistics_numbers.grid(column=2, row=2, columnspan=2, sticky="nwe", padx=(0, 5), pady=5)
        self.notice_label.grid(column=0, row=3, columnspan=4, sticky="swe", padx=5, pady=5)
        self.screen_label.grid(padx=5, pady=5)
        self.enemies_treeview.grid(column=0, row=0, sticky="nswe", pady=5, padx=5)
        self.enemies_scrollbar.grid(column=1, row=0, sticky="nswe", pady=5)
        self.enemies_label.grid(column=2, row=0, sticky="nwe", pady=5, padx=5)
        self.time_view.grid(column=0, row=0, sticky="nswe", pady=5, padx=5)
        self.time_scroll.grid(column=1, row=0, sticky="ns", pady=5)
        self.time_line.grid(column=1, row=1, sticky="nswe", padx=5, pady=5)

    def treeview_sort_column(self, treeview, column, reverse, type):
        if column == "Ability":
            column = "#0"
        l = [(treeview.set(k, column), k) for k in treeview.get_children('')]
        if type == "int":
            l.sort(key=lambda t: int(t[0]), reverse=reverse)
        elif type == "str":
            l.sort(key=lambda t: t[0], reverse=reverse)
        else:
            raise NotImplementedError
        for index, (val, k) in enumerate(l):
            treeview.move(k, '', index)
        treeview.heading(column, command=lambda: self.treeview_sort_column(treeview, column, not reverse, type))

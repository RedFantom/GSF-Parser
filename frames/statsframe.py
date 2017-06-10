# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
import tkinter as tk
import tkinter.ttk as ttk
import variables
from toplevels.eventsview import EventsView


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
        self.notebook = ttk.Notebook(self, width=300, height=327)
        self.stats_frame = ttk.Frame(self.notebook)
        self.enemies_frame = ttk.Frame(self.notebook)
        self.screen_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")
        self.notebook.add(self.enemies_frame, text="Enemies")
        self.events_frame = ttk.Frame(self, width=300)
        self.events_button = ttk.Button(self.events_frame, text="Show events for spawn", command=self.show_events,
                                        state=tk.DISABLED, width=43)
        self.statistics_label_var = tk.StringVar()
        string = "Damage dealt to\nDamage dealt:\nDamage taken:\nDamage ratio:\nSelfdamage:\nHealing received:\n" + \
                 "Hitcount:\nCriticalcount:\nCriticalluck:\nDeaths:\nDuration:\nDPS:"
        self.statistics_label_var.set(string)
        self.statistics_label = ttk.Label(self.stats_frame, textvariable=self.statistics_label_var, justify=tk.LEFT,
                                          wraplength=145)
        self.statistics_numbers_var = tk.StringVar()
        self.statistics_label.setvar()
        self.statistics_numbers = ttk.Label(self.stats_frame, textvariable=self.statistics_numbers_var,
                                            justify=tk.LEFT, wraplength=145)

        self.enemies_treeview = ttk.Treeview(self.enemies_frame)
        self.enemies_scrollbar = ttk.Scrollbar(self.enemies_frame, command=self.enemies_treeview.yview)
        self.enemies_treeview.config(yscrollcommand=self.enemies_scrollbar.set)
        self.enemies_treeview.config(columns=("Damage dealt", "Damage taken"))
        self.enemies_treeview["show"] = ("tree", "headings")
        self.enemies_treeview.column("#0", width=117, anchor="w")
        self.enemies_treeview.column("Damage dealt", width=74, anchor="e")
        self.enemies_treeview.column("Damage taken", width=74, anchor="e")
        self.enemies_treeview.heading("#0", text="Enemy name/ID",
                                      command=lambda: self.treeview_sort_column(self.enemies_treeview,
                                                                                "Enemy name/ID", False, "str"))
        self.enemies_treeview.heading("Damage dealt", text="Damage dealt",
                                      command=lambda: self.treeview_sort_column(self.enemies_treeview,
                                                                                "Damage dealt", False, "int"))
        self.enemies_treeview.heading("Damage taken", text="Damage taken",
                                      command=lambda: self.treeview_sort_column(self.enemies_treeview,
                                                                                "Damage taken", False, "int"))
        self.enemies_treeview.config(height=13)

        self.abilities_frame = ttk.Frame(self.notebook, width=300)

        self.notebook.add(self.abilities_frame, text="Abilities")
        self.abilities_treeview = ttk.Treeview(self.abilities_frame)
        self.abilities_scrollbar = ttk.Scrollbar(self.abilities_frame, command=self.abilities_treeview.yview)
        self.abilities_treeview.config(yscrollcommand=self.abilities_scrollbar.set)
        self.abilities_treeview.config(columns=("Times used",))
        self.abilities_treeview["show"] = ("tree", "headings")
        self.abilities_treeview.column("#0", width=180)
        self.abilities_treeview.config(height=13)
        self.abilities_treeview.column("Times used", width=85)
        self.abilities_treeview.heading("Times used", text="Times used",
                                        command=lambda: self.treeview_sort_column(self.abilities_treeview,
                                                                                  "Times used", False, "int"))
        self.abilities_treeview.heading("#0", text="Ability",
                                        command=lambda: self.treeview_sort_column(self.abilities_treeview,
                                                                                  "Ability", False, "str"))
        self.notice_label = ttk.Label(self.stats_frame, text="\n\n\n\nThe damage dealt for bombers can not be " +
                                                             "accurately calculated due to CombatLog limitations, "
                                                             "as damage dealt by bombs is not recorded.",
                                      justify=tk.LEFT, wraplength=290)
        self.screen_label_var = tk.StringVar()
        self.screen_label = ttk.Label(self.screen_frame, textvariable=self.screen_label_var, justify=tk.LEFT)
        self.notebook.add(self.screen_frame, text="Screen parsing")

    def show_events(self):
        """
        Open a TopLevel of the overlay module to show the lines of a Combatlog in a human-readable manner
        :return:
        """
        spawn, player_numbers, spawn_timing, match_timing = self.window.file_select_frame.get_spawn()
        EventsView(self.window, spawn, player_numbers, spawn_timing, match_timing)

    def grid_widgets(self):
        """
        Put all widgets in the right place
        :return:
        """
        self.abilities_treeview.grid(column=0, row=0, pady=5, padx=5)
        self.abilities_scrollbar.grid(column=1, row=0, sticky="ns", pady=5)
        self.notebook.grid(column=0, row=0, columnspan=4, sticky="nwe")
        self.events_frame.grid(column=0, row=1, columnspan=4, sticky="nswe")
        self.events_button.grid(column=0, row=1, sticky="nswe", columnspan=4, pady=5)
        self.statistics_label.grid(column=0, row=2, columnspan=2, sticky="nswe", padx=(5, 0), pady=5)
        self.statistics_numbers.grid(column=2, row=2, columnspan=2, sticky="nwe", padx=(0, 5), pady=5)
        self.notice_label.grid(column=0, row=3, columnspan=4, sticky="swe", padx=5, pady=5)
        self.screen_label.grid()
        self.enemies_treeview.grid(column=0, row=0, sticky="nswe", pady=5, padx=5)
        self.enemies_scrollbar.grid(column=1, row=0, sticky="nswe", pady=5)
    
    def treeview_sort_column(self, treeview, column, reverse, type):
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
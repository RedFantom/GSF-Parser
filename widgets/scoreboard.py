"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from datetime import datetime
# UI Libraries
import tkinter as tk
from tkinter import ttk
# Project Modules
from parsing.scoreboards import ScoreboardDatabase


class Scoreboard(ttk.Frame):
    """Frame containing a Treeview showing Scoreboard data"""

    HEADINGS = {
        "#0": "Name",
        "kills": "Kills",
        "assists": "Assists",
        "deaths": "Deaths",
        "damage": "Damage",
        "hit": "Hit",
        "objectives": "Objectives"
    }

    def __init__(self, parent: tk.Widget):
        """Initialize the Frame and child widgets"""
        ttk.Frame.__init__(self, parent)

        self.score_label = ttk.Label(self, text="No match selected or scoreboard not available")
        self.l_label, self.r_label = ttk.Label(self), ttk.Label(self)
        self.tree = ttk.Treeview(
            self, columns=("kills", "assists", "deaths", "damage", "hit", "objectives"),
            show=("headings", "tree"))

        self.setup_treeview()
        self.grid_widgets()

    def grid_widgets(self):
        """Configured child widgets in grid geometry manager"""
        self.score_label.grid(row=0, column=0, sticky="nsw", padx=5, pady=(5, 0))
        self.l_label.grid(row=0, column=1, sticky="nsw", padx=(0, 5), pady=(5, 0))
        self.r_label.grid(row=0, column=2, sticky="nsw", padx=(0, 5), pady=(5, 0))
        self.tree.grid(row=1, column=0, sticky="nswe", padx=5, pady=5, columnspan=5)

    def setup_treeview(self):
        """Setup the Treeview columns and headings"""
        self.tree.column("#0", width=150, anchor=tk.W)
        self.tree.column("kills", width=50, anchor=tk.E)
        self.tree.column("assists", width=60, anchor=tk.E)
        self.tree.column("deaths", width=60, anchor=tk.E)
        self.tree.column("damage", width=80, anchor=tk.E)
        self.tree.column("hit", width=40, anchor=tk.E)
        self.tree.column("objectives", width=100, anchor=tk.E)

        for c, t in Scoreboard.HEADINGS.items():
            self.tree.heading(c, text=t)

        self.tree.configure(height=13)
        self.tree.tag_configure("ally", background="#8eff75", foreground="black")
        self.tree.tag_configure("enemy", background="#ff8570", foreground="black")

    def update_match(self, match: datetime):
        """Update the Widget with the scoreboard of a match"""
        scoreboard = ScoreboardDatabase.get_scoreboard(match)
        if scoreboard is None:
            self.reset()
            return
        self.update_scoreboard(scoreboard)

    def update_scoreboard(self, scoreboard):
        """Update Widget with data from scoreboard"""
        l, r, i = scoreboard["score"]
        labels = [self.l_label, self.r_label]
        self.score_label.config(text="End score:")
        self.l_label.config(text=str(l))
        self.r_label.config(text=str(r))
        labels[i].config(foreground="green")
        labels[int(not bool(i))].config(foreground="red")
        for ally in scoreboard["allies"]:
            self.tree.insert("", tk.END, values=tuple(ally), tags=("ally",))
        for enemy in scoreboard["enemies"]:
            self.tree.insert("", tk.END, values=tuple(enemy), tags=("enemy",))

    def reset(self):
        """Delete all the data from the widget"""
        self.tree.delete(*self.tree.get_children(""))
        self.score_label.config(text="No match selected or scoreboard not available")
        map(lambda l: l.config(text=""), (self.l_label, self.r_label))

# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
import tkinter.ttk as ttk
from os import path
import pickle as pickle
from PIL import Image as img
from PIL.ImageTk import PhotoImage as photo
from widgets import ToggledFrame, VerticalScrollFrame
import variables


class ShipSelectFrame(ttk.Frame):
    def __init__(self, parent, callback, faction_callback):
        ttk.Frame.__init__(self, parent)
        self.window = variables.main_window
        self.faction = "Imperial"
        self.ship = "Bloodmark"
        self.component = "Light Laser Cannon"
        self.scroll_frame = VerticalScrollFrame(self, canvaswidth=240, canvasheight=315, width=240, height=315)
        self.frame = self.scroll_frame.interior
        self.icons_path = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "icons"))
        with open(path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "assets", "categories.db")),
                  "rb") as db:
            self.data = pickle.load(db)
        self.callback = callback
        self.faction_callback = faction_callback
        self.faction_frames = {}
        self.faction_buttons = {}
        self.ship_frames = {}
        self.ship_photos = {}
        self.ship_buttons = {}
        self.category_frames = {faction: {} for faction in self.data}
        self.faction_photos = {}
        self.ships = None

        toggled = False

        self.server = tk.StringVar()
        self.server_dropdown = ttk.OptionMenu(self, self.server, *("Choose server",), command=self.update_characters)
        self.character = tk.StringVar()
        self.character_dropdown = ttk.OptionMenu(self, self.character, *("Choose character",),
                                                 command=self.load_character)
        # self.character_update_button = ttk.Button(self, text="Load character", command=self.load_character)

        for faction in self.data:
            self.faction_frames[faction] = ttk.Frame(self.frame)
            for category in self.data[faction]:
                if category["CategoryName"] == "Infiltrator":
                    continue  # pass
                self.category_frames[faction][category["CategoryName"]] = ToggledFrame(self.frame,
                                                                                       text=category["CategoryName"],
                                                                                       labelwidth=27)
                if category["CategoryName"] == "Scout" and not toggled:
                    self.category_frames[faction][category["CategoryName"]].toggle()
                    toggled = True
                for ship_dict in category["Ships"]:
                    try:
                        image = img.open(path.join(self.icons_path, ship_dict["Icon"] + ".jpg"))
                        image = image.resize((52, 52))
                        self.ship_photos[ship_dict["Name"]] = photo(image)
                    except IOError:
                        self.ship_photos[ship_dict["Name"]] = photo(img.open(path.join(self.icons_path,
                                                                                       faction.lower() + "_l.png")))
                    self.ship_buttons[ship_dict["Name"]] = \
                        ttk.Button(self.category_frames[faction][category["CategoryName"]].sub_frame,
                                   text=ship_dict["Name"],
                                   image=self.ship_photos[ship_dict["Name"]], compound=tk.LEFT,
                                   command=lambda faction=faction, category=category, ship_dict=ship_dict:
                                   self.set_ship(faction, category["CategoryName"], ship_dict["Name"]),
                                   width=18)
        self.update_servers()

    def grid_widgets(self):
        self.server_dropdown.grid(row=0, column=0, columnspan=2, sticky="nswe", pady=(5, 0))
        self.character_dropdown.grid(row=1, column=0, columnspan=2, sticky="nswe", pady=(5, 5))
        # self.character_update_button.grid(row=2, column=0, columnspan=2, sticky="nswe", pady=5)
        self.scroll_frame.grid(row=3, rowspan=2, columnspan=2, sticky=tk.N + tk.S + tk.W + tk.E, pady=2)
        set_row = 20
        for faction in self.category_frames:
            if faction == self.faction:
                for category, frame in self.category_frames[faction].items():
                    frame.grid(row=set_row, column=0, sticky=tk.N + tk.S + tk.W + tk.E, columnspan=2)
                    set_row += 1
            else:
                for frame in self.category_frames[faction].values():
                    frame.grid_forget()
        set_row = 40
        for button in self.ship_buttons.values():
            button.grid(row=set_row, column=0, sticky=tk.N + tk.S + tk.W + tk.E)
            set_row += 1

    def set_ship(self, faction, category, shipname):
        print("Faction: %s\nCategory: %s\nShipname: %s" % (faction, category, shipname))
        self.callback(faction, category, shipname)

    def set_faction(self, faction):
        self.faction = faction
        self.faction_callback(faction)
        self.grid_widgets()

    def update_servers(self):
        self.server_dropdown["menu"].delete(0, tk.END)
        self.character_dropdown["menu"].delete(0, tk.END)
        servers = ["Choose server"]
        for data in self.window.characters_frame.characters:
            server = self.window.characters_frame.servers[data[0]]
            if server in servers:
                continue
            servers.append(server)
        for server in servers:
            self.server_dropdown["menu"].add_command(label=server, command=lambda var=self.server, val=server:
                                                     self.set_server(var, val))

    def update_characters(self):
        self.character_dropdown["menu"].delete(0, tk.END)
        characters = ["Choose character"]
        for data in self.window.characters_frame.characters:
            server = self.window.characters_frame.servers[data[0]]
            if server != self.server.get():
                continue
            characters.append(data[1])
        for character in characters:
            self.character_dropdown["menu"].add_command(label=character,
                                                        command=lambda var=self.character, val=character:
                                                        self.set_character(var, val))
        return

    def load_character(self):
        print("Loading character {0}".format((self.server.get(), self.character.get())))
        server = self.window.characters_frame.reverse_servers[self.server.get()]
        self.ships = self.window.characters_frame.characters[(server, self.character.get())]["Ship Objects"]

    def set_server(self, variable, value):
        variable.set(value)
        self.update_characters()

    def set_character(self, variable, value):
        variable.set(value)
        self.load_character()

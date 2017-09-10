# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# Own modules
from parsing.guiparsing import GSFInterface
from tools.utilities import write_debug_log, get_temp_directory, get_cursor_position
from . import vision
from .keys import keys
from toplevels.screenoverlay import HitChanceOverlay
import variables
# General imports
import threading
import pickle as pickle
import os
from datetime import datetime
from queue import Queue
import time
import pynput
import mss
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
from shutil import copyfile
import operator
from PIL import Image

"""
These classes use data in a dictionary structure, dumped to a file in the temporary directory of the GSF Parser. This
dictionary contains all the data acquired by screen parsing and is stored with the following structure:

Dictionary structure:
data_dictionary[filename] = file_dictionary
file_dictionary[datetime_obj] = match_dictionary
match_dictionary[datetime_obj] = spawn_dictionary
spawn_dictionary["power_mgmt"] = power_mgmt_dict
    power_mgmt_dict[datetime_obj] = integer
spawn_dictionary["cursor_pos"] = cursor_pos_dict
    cursor_pos_dict[datetime_obj] = (x, y)
spawn_dictionary["tracking"] = tracking_dict
    tracking_dict[datetime_obj] = percentage
spawn_dictionary["clicks"] = clicks_dict
    clicks_dict[datetime_obj] = (left, right)
spawn_dictionary["keys"] = keys_dict
    keys_dict[datetime_obj] = keyname
spawn_dictionary["health"] = health_dict
    health_dict[datetime_obj] = (hull, shieldsf, shieldsr), all ints
spawn_dictionary["distance"] = distance_dict
    distance_dict[datetime_obj] = distance, int
spawn_dictionary["target"] = target_dict
    target_dict[datetime_obj] = (type, name)


The realtime screen parsing uses Queue objects to communicate with other parts of the program. This is required because
the screen parsing takes place in a separate process for performance optimization and itself runs several threads to
monitor mouse and keyboard activity. This only gets recorded if the user is in a match, for otherwise it might be
possible to extract keylogs of different periods, and this would impose an extremely dangerous security issue. The Queue
objects used by the ScreenParser object are the following:

data_queue:         This Queue object receives any data from the realtime file parsing that is relevant for the
                    Screen Parser object. This includes data about the file watched, the match detected, the spawn
                    detected and other information. A list of expected data:
                    - ("file", str new_file_name)           new CombatLog watched
                    - ("match", True, datetime)             new match started
                    - ("match", False, datetime)            match ended
                    - ("spawn", datetime)                   new spawn
exit_queue:         This Queue object is checked to see if the ScreenParser should stop running or not. Because this
                    is running in a separate process, one cannot just simply call __exit__, all pending operations
                    must first be completed. A list of expected data:
                    - True                                  keep running
                    - False                                 exit ASAP
query_queue         This Queue object is for communication between the process and the realtime parsing thread in the
                    main process so the main process can receive data and display it in the overlay. A list of
                    expected data:
                    - "power_mgmt"                          return int power_mgmt
                    - "tracking"                            return int tracking degrees
                    - "health"                              return (hull, shieldsf, shieldsr), all ints
return_queue        The Queue in which the data requested from the query_queue is returned.
_internal_queue:    This Queue object is for internal communication between the various Thread objects running in this
                    Process object. A list of expected data:
                    - ("keypress", *args)                   key pressed
                    - ("mousepress", *args)                 mouse button pressed
                    - ("mouserelease", *args)               mouse button released
                    This is not yet a complete list.
"""


class FileHandler(object):
    """
    Reads the files generated by ScreenParser for file parsing
    """

    @staticmethod
    def get_dictionary_key(dictionary, timing, value=False):
        if not isinstance(dictionary, dict):
            raise ValueError()
        if not isinstance(timing, datetime):
            raise ValueError()
        for key, val in dictionary.items():
            if not isinstance(key, datetime):
                continue
            if key == timing:
                if value:
                    return val
                return key
        return None

    @staticmethod
    def get_dictionary_key_secondsless(dictionary, timing):
        # The match_dt as received is not found in the dictionary, so further searching is required
        # First, searching starts by removing the seconds from the match_dt
        timing_secondsless = timing.replace(second=0, microsecond=0)
        # Now we build a dictionary that also has secondsless keys
        dictionary_secondsless_keys = \
            {key.replace(second=0, microsecond=0): value for key, value in dictionary.items()}
        # Now we attempt to match the secondsless key in the secondsless file_dict
        correct_key = FileHandler.get_dictionary_key(dictionary_secondsless_keys, timing_secondsless)
        if correct_key:
            # We have found the correct key for the match
            return correct_key
        return None

    @staticmethod
    def get_spawn_dictionary(data, file_name, match_dt, spawn_dt):
        """
        Function to get the data dictionary for a spawn based on a file name, match datetime and spawn datetime. Uses
        a lot of code to make the searching as reliable as possible.
        """
        print("Spawn data requested for:\n{}\n{}\n{}".format(file_name, match_dt, spawn_dt))
        # First check if the file_name is available
        if file_name not in data:
            return "Not available for this file.\n\nScreen parsing results are only available for spawns in files " \
                   "which were spawned while screen parsing was enabled and real-time parsing was running."
        try:
            file_dt = datetime.strptime(file_name[:-10], "combat_%Y-%m-%d_%H_%M_%S_")
        except ValueError:
            return "Not available for this file.\n\nScreen parsing results are not supported for file names which do " \
                   "not match the original Star Wars - The Old Republic CombatLog file name format."
        file_dict = data[file_name]
        # Next up comes the checking of datetimes, which is slightly more complicated due to the fact that even equal
        # datetime objects with the == operators, are not equal with the 'is' operator
        # Also, for backwards compatibility, different datetimes must be supported in this searching process
        # Datetimes always have a correct time, but the date is not always the same as the filename date
        # If this is the case, the date is actually set to January 1 1900, the datetime default
        # Otherwise the file name of the CombatLog must have been altered
        match_dict = None
        for key, value in file_dict.items():
            if key.hour == match_dt.hour and key.minute == match_dt.minute:
                match_dict = value
        if match_dict is None:
            return "Not available for this match\n\nScreen parsing results are only available for spawns " \
                   "in matches which were spawned while screen parsing was enabled and real-time parsing " \
                   "was running"
        # Now a similar process starts for the spawns, except that seconds matter here.
        spawn_dict = None
        for key, value in match_dict.items():
            if key is None:
                # If the key is None, something weird is going on, but we do not want to throw any data away
                # This may be caused by a bug in the ScreenParser
                # For now, we reset key to a sensible value, specifically the first moment the data was recorded, if
                # that's possible. If not, we'll skip it.
                try:
                    key = list(value[list(value.keys())[0]].keys())[0]
                except (KeyError, ValueError, IndexError):
                    continue
            if key.hour == spawn_dt.hour and key.minute == spawn_dt.minute and key.second == spawn_dt.second:
                spawn_dict = value
        if spawn_dict is None:
            return "Not available for this spawn\n\nScreen parsing results are not available for spawns which " \
                   "were not  spawned while screen parsing was enabled and real-time parsing were running."
        print("Retrieved data: {}".format(spawn_dict))
        return spawn_dict

    @staticmethod
    def get_data_dictionary(name="realtime.db"):
        with open(os.path.join(get_temp_directory(), name), "rb") as fi:
            data = pickle.load(fi)
        return data

    @staticmethod
    def get_spawn_stats(file_name, match_dt, spawn_dt):
        """
        Function to return the spawn statistics
        :param file_name:
        :param match_dt:
        :param spawn_dt:
        :return:
        """
        data = FileHandler.get_data_dictionary()
        value = FileHandler.get_spawn_dictionary(data, file_name, match_dt, spawn_dt)
        if isinstance(value, str):
            return value
        elif isinstance(value, dict):
            spawn_dicts = value
        else:
            raise ValueError("Returned value from get_spawn_dictionary is neither str nor dict")
        # Start calculations on this spawn data
        power_mgmt = {1: 0, 2: 0, 3: 0, 4: 0}
        for key, value in spawn_dicts["power_mgmt"].items():
            if not value:
                continue
            power_mgmt[value] += 1
        power_mgmt_max = max(power_mgmt.items(), key=operator.itemgetter(1))[0]
        tracking = 0
        amount = 0
        for key, value in spawn_dicts["tracking"].items():
            if not value:
                continue
            tracking += value
            amount += 1
        if amount == 0:
            tracking = "Not available for this spawn"
        else:
            tracking = tracking / amount
        total = (0, 0, 0)
        for key, value in spawn_dicts["health"].items():
            if not value:
                break
            total += value
        try:
            average_health = tuple(key / len(spawn_dicts["health"]) for key in total)
        except (ZeroDivisionError, TypeError):
            average_health = "Not available for this spawn"
        return FileHandler.get_formatted_stats_string(*(power_mgmt_max, tracking, average_health))

    @staticmethod
    def get_formatted_stats_string(*values):
        return """
        Most used power management: \t{0}
        Average tracking degrees: \t\t{1:.2f}
        Average ship health: \t\t{2}
        """.format(*values)


class ScreenParser(threading.Thread):
    def __init__(self, data_queue, exit_queue, query_queue, return_queue, character_data, rgb=False, cooldowns=None,
                 powermgmt=True, health=True, name=True, ttk=True, tracking=True, ammo=True, distance=True,
                 cursor=True):
        threading.Thread.__init__(self)
        if rgb and not cooldowns:
            write_debug_log("ScreenParser encountered the following error during initialization: "
                            "rgb requested but cooldowns not specified")
            raise ValueError("rgb requested but cooldowns not specified")
        interface = character_data["GUI"]
        if not isinstance(interface, GSFInterface):
            interface = GSFInterface(interface)
        self.interface = interface
        self.rgb = rgb
        self.cooldowns = cooldowns
        self.query_queue = query_queue
        self.data_queue = data_queue
        self.exit_queue = exit_queue
        self._internal_queue = Queue()
        self.return_queue = return_queue
        self.pickle_name = os.path.join(get_temp_directory(), "realtime.db")
        self.features = {
            "powermgmt": powermgmt,
            "health": health,
            "name": name,
            "ttk": ttk,
            "tracking": tracking,
            "ammo": ammo,
            "distance": distance,
            "cursor": cursor
        }
        self.character = character_data
        self.features_list = [key for key, value in self.features.items() if value]
        write_debug_log("ScreenParser is opening the following database: %s" % self.pickle_name)
        self.screenoverlay = HitChanceOverlay(variables.main_window) if \
            variables.settings_obj["realtime"]["screenparsing_overlay"] else None
        self.moving_overlay = True if \
            variables.settings_obj["realtime"]["screenparsing_overlay_geometry"] else False

        try:
            with open(self.pickle_name, "rb") as fi:
                self.data_dictionary = pickle.load(fi)
        except IOError:
            self.data_dictionary = {}
        except EOFError as e:
            messagebox.showerror("Error", "The realtime data database did not open correctly. The data in the file may "
                                          "be corrupted. You will now have the chance to dump the data to a separate "
                                          "location together with a debug log. After this, the data will be "
                                          "overwritten and all data in the file, including all data on tracking, "
                                          "health, maps, scores and other data will be lost.")
            if messagebox.askyesno("Debug dump", "Would you like to backup your old file with a debug log for the "
                                                 "developers?"):
                directory = filedialog.askdirectory(parent=variables.main_window, title="Choose directory...",
                                                    mustexist=True)
                copyfile(self.pickle_name, directory)
                with open(os.path.join(directory, "debug.txt"), "w") as f:
                    f.writelines(str(e))
            self.data_dictionary = {}
        write_debug_log("ScreenParser is creating all required data variables")
        # String of filename
        self._file = ""
        # Datetime objects of start timings
        self._match = None
        self._spawn = None
        # Dictionaries to store temporary data
        self._file_dict = {}
        self._match_dict = {}
        self._spawn_dict = {}
        # More dictionaries to store temporary data
        self._power_mgmt_dict = {}
        self._cursor_pos_dict = {}
        self._tracking_dict = {}
        self._clicks_dict = {}
        self._keys_dict = {}
        self._health_dict = {}
        self._distance_dict = {}
        self._target_dict = {}
        self._ammo_dict = {}

        # Listeners for keyboard and mouse input
        self._kb_listener = pynput.keyboard.Listener(on_press=self.on_press_kb)
        self._ms_listener = pynput.mouse.Listener(on_click=self.on_click)
        self._current_match = None
        self._current_spawn = None
        self.file = None
        self.match = None
        self.is_match = None
        self.is_match = None

    def run(self):
        # Start the listeners for keyboard and mouse input
        write_debug_log("ScreenParser starting main functions")
        write_debug_log("Threads active: %s" % str(threading.enumerate()))
        # self._kb_listener.start()
        # self._ms_listener.start()
        # Start the loop to parse the screen data
        sct = mss.mss()
        
        power_mgmt_cds = self.interface.get_ship_powermgmt_coordinates()
        health_cds = self.interface.get_ship_health_coordinates()
        name_cds = self.interface.get_target_name_coordinates()
        ship_type_cds = self.interface.get_target_shiptype_coordinates()
        player_buff_cds = self.interface.get_ship_buffs_coordinates()
        target_buff_cds = self.interface.get_target_buffs_coordinates()
        score_cds = self.interface.get_score_coordinates()
        spawn_timer_cds = self.interface.get_spawn_timer_coordinates()
        match_timer_cds = self.interface.get_match_timer_coordinates()
        ammo_cds = self.interface.get_ammo_coordinates()
        distance_cds = self.interface.get_distance_coordinates()

        while True:
            # If the exit_queue is not empty, get the value. If the value is False, exit the loop and start preparations
            # for terminating the process entirely by saving all the data collected.
            if not self.exit_queue.empty():
                print("ScreenParser exit_queue is not empty")
                if not self.exit_queue.get():
                    print("ScreenParser loop break")
                    break
            write_debug_log("ScreenParser started a cycle")
            # While data_queue is not empty, process the data in it
            if not self.data_queue.empty():
                data = self.data_queue.get()
                write_debug_log("ScreenParser received the following data from Parser: %s" % str(data))
                # (data[0], data[1], data[2])
                if not isinstance(data, tuple):
                    write_debug_log("ScreenParser encountered the following error: "
                                    "Unexpected data received: " + str(data))
                    raise ValueError("Unexpected data received: ", str(data))
                # ("file", filename)
                if data[0] == "file" and self.file is not data[1]:
                    self.data_dictionary[self.file] = self._file_dict
                    self.file = data[1]
                    self._file_dict.clear()
                # ("match", False, datetime)
                elif data[0] == "match" and not data[1] and self.is_match:
                    if not len(self._match_dict) == 0 or not len(self._spawn_dict) == 0:
                        self.set_new_match()
                    self._file_dict[self._match] = self._match_dict
                    self._match_dict.clear()
                    self.is_match = False
                    self.match = None
                    self.screenoverlay.running = False
                    time.sleep(0.05)
                # ("match", True, datetime)
                elif data[0] == "match" and data[1] and not self.is_match:
                    self._match = data[2]
                    if not len(self._match_dict) == 0 or not len(self._spawn_dict) == 0:
                        self.set_new_match()
                    self.is_match = True
                # ("spawn", datetime)
                elif data[0] == "spawn":
                    self.set_new_spawn()
                    self._spawn = data[1]
                else:
                    write_debug_log("ScreenParser encountered the following error: "
                                    "Unexpected data received: " + str(data))
                    raise ValueError("Unexpected data received: ", str(data))
            if not self.is_match:
                write_debug_log("No match is active, so ScreenParser ends cycle")
                time.sleep(1)
                continue
            write_debug_log("Start pulling vision functions data")
            image = sct.grab(sct.monitors[0])
            pil_screen = Image.frombytes("RGB", image.size, image.rgb)
            screen = vision.pillow_to_numpy(pil_screen)
            pointer_cds = get_cursor_position(screen)
            current_time = datetime.now()
            if "powermgmt" in self.features_list:
                power_mgmt = vision.get_power_management(screen, *power_mgmt_cds)
            else:
                power_mgmt = None
            self._power_mgmt_dict[current_time] = power_mgmt
            if "healh" in self.features_list:
                health_hull = vision.get_ship_health_hull(screen)
                (health_shields_f, health_shields_r) = vision.get_ship_health_shields(screen, health_cds)
            else:
                health_hull = None
                health_shields_f, health_shields_r = None, None
            self._health_dict[current_time] = (health_hull, health_shields_f, health_shields_r)
            if "ttk" in self.features_list:
                # Calculate TTK
                pass
            else:
                # Assign None value
                pass
            if "name" in self.features_list:
                name = vision.perform_ocr(pil_screen, name_cds)
                type = vision.perform_ocr(pil_screen, ship_type_cds)
                self._target_dict[current_time] = (type, name)
            else:
                pass
            if "tracking" in self.features_list:
                distance = vision.get_distance_from_center(pointer_cds)
                tracking_degrees = vision.get_tracking_degrees(distance)
            else:
                tracking_degrees = None
            self._tracking_dict[current_time] = tracking_degrees
            if "distance" in self.features_list:
                try:
                    distance = int(vision.perform_ocr(pil_screen, distance_cds))
                except ValueError as e:
                    print(e)
                    distance = None
            else:
                distance = None
            self._distance_dict[current_time] = distance
            if "ammo" in self.features_list:
                try:
                    ammo = int(vision.perform_ocr(pil_screen, ammo_cds))
                except ValueError as e:
                    print(e)
                    ammo = None
            else:
                ammo = None
            self._ammo_dict[current_time] = ammo
            self._cursor_pos_dict[current_time] = pointer_cds
            if not self.exit_queue.empty():
                print("ScreenParser exit_queue is not empty")
                if not self.exit_queue.get():
                    print("ScreenParser loop break")
                    break
            if self.screenoverlay:
                self.screenoverlay.set_percentage(str(tracking_degrees) + "°")
            write_debug_log("Start logging and saving vision functions data")
            self._tracking_dict[current_time] = tracking_degrees * 1
            if not self._internal_queue.empty():
                data = self._internal_queue.get()
                write_debug_log("ScreenParser received the following data in the internal_queue: %s" % str(data))
                if "mouse" in data[0]:
                    self._clicks_dict[data[2]] = (data[0], data[1])
                else:
                    self._keys_dict[data[2]] = (data[0], data[1])
            if not self.query_queue.empty():
                command = self.query_queue.get()
                write_debug_log("ScreenParser received the following command: %s" % command)
                if not isinstance(command, str):
                    write_debug_log("ScreenParser encountered the following error: "
                                    "Command received was not of str type")
                    raise ValueError("Command received was not of str type")
                if command == "power_mgmt":
                    self.return_queue.put(power_mgmt)
                elif command == "health":
                    self.return_queue.put((health_hull, health_shields_f, health_shields_r))
                elif command == "tracking":
                    self.return_queue.put(tracking_degrees)
                else:
                    raise ValueError("Command not supported: {0}".format(command))
                write_debug_log("Requested data returned to in the return_queue")
            self._spawn_dict["power_mgmt"] = self._power_mgmt_dict
            self._spawn_dict["cursor_pos"] = self._cursor_pos_dict
            self._spawn_dict["clicks"] = self._clicks_dict
            self._spawn_dict["keys"] = self._keys_dict
            self._spawn_dict["health"] = self._health_dict
            self._spawn_dict["distance"] = self._distance_dict
            self._spawn_dict["target"] = self._target_dict
            self._spawn_dict["ammo"] = self._ammo_dict
            self._spawn_dict["tracking"] = self._tracking_dict
            self._match_dict[self._spawn] = self._spawn_dict
            self._file_dict[self._match] = self._match_dict
            self.data_dictionary[self._file] = self._file_dict
            self.save_data_dictionary()
            write_debug_log("Finished a screen parsing cycle")
            time.sleep(0.05)
        print("ScreenParser stopping activities")
        write_debug_log("ScreenParser stopping activities")
        try:
            self.screenoverlay.running = False
        except AttributeError:
            pass
        time.sleep(0.05)
        print("Calling self.close()")
        self.data_dictionary[self.file] = self._file_dict
        print("Saving data dictionary")
        self.save_data_dictionary()
        print("ScreenParser exit")

    def on_press_kb(self, key):
        if key in keys:
            key = keys[key]
        write_debug_log("A keypress was inserted in the internal_queue: %s" % str(key))
        self._internal_queue.put(("keypress", key, datetime.now()))

    def on_press_ms(self, key):
        if key in keys:
            key = keys[key]
        write_debug_log("A mousepress was inserted in the internal queue: %s" % str(key))
        self._internal_queue.put("mousepress", key, datetime.now())

    def on_release_ms(self, key):
        if key in keys:
            key = keys[key]
        write_debug_log("A mouserelease was inserted in the internal queue: %s" % str(key))
        self._internal_queue.put("mouserelease", key, datetime.now())

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.on_press_ms(button)
        else:
            self.on_press_ms(button)

    def close(self):
        self.__exit__()

    def __exit__(self):
        self.data_dictionary[self.file] = self._file_dict
        print("Saving data dictionary")
        self.save_data_dictionary()
        print("ScreenParser exit")

    def save_data_dictionary(self):
        write_debug_log("ScreenParser saving data dictionary")
        with open(self.pickle_name, "wb") as fo:
            pickle.dump(self.data_dictionary, fo)
        write_debug_log("ScreenParser successfully saved data dictionary")

    def set_new_spawn(self):
        write_debug_log("ScreenParser getting ready for a new spawn")
        self._match_dict[self._spawn] = self._spawn_dict
        self._spawn_dict.clear()
        self.clear_feature_dicts()

    def clear_feature_dicts(self):
        self._power_mgmt_dict.clear()
        self._cursor_pos_dict.clear()
        self._clicks_dict.clear()
        self._keys_dict.clear()
        self._health_dict.clear()
        self._distance_dict.clear()
        self._target_dict.clear()
        self._tracking_dict.clear()
        self._ammo_dict.clear()

    def set_new_match(self):
        write_debug_log("ScreenParser getting ready for a new match")
        self._match_dict[self._spawn] = self._spawn_dict
        self.data_dictionary[self._file][self._match] = self._match_dict
        self._match_dict.clear()
        self._spawn_dict.clear()
        self.clear_feature_dicts()

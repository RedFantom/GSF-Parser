# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import threading as mp
import vision
import threading
import settings
import cPickle as pickle
import tempfile
from datetime import datetime
import pynput
from Queue import Queue
from keys import keys

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
    pass


class ScreenParser(mp.Thread):
    def __init__(self, data_queue, exit_queue, query_queue, return_queue, rgb=False, cooldowns=None):
        mp.Thread.__init__(self)
        if rgb and not cooldowns:
            raise ValueError("rgb requested but cooldowns not specified")
        self.rgb = rgb
        self.cooldowns = cooldowns
        self.query_queue = query_queue
        self.data_queue = data_queue
        self.exit_queue = exit_queue
        self._internal_queue = Queue()
        self.return_queue = return_queue
        directory = tempfile.gettempdir()
        self.pickle_name = directory.replace("\\temp", "") + "\\GSF Parser\\rltdata.db"
        try:
            with open(self.pickle_name, "r") as fi:
                self.data_dictionary = pickle.load(fi)
        except IOError:
            self.data_dictionary = {}
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
        self._kb_listener.start()
        self._ms_listener.start()
        # Start the loop to parse the screen data
        while True:
            # If the exit_queue is not empty, get the value. If the value is False, exit the loop and start preparations
            # for terminating the process entirely by saving all the data collected.
            if not self.exit_queue.empty():
                if not self.exit_queue.get():
                    break
            # While data_queue is not empty, process the data in it
            while not self.data_queue.empty():
                data = self.data_queue.get()
                # (data[0], data[1], data[2])
                if not isinstance(data, tuple) or not len(data) is 2 or not len(data) is 3:
                    raise ValueError("Unexpected data received: ", str(data))
                # ("file", filename)
                elif data[0] == "file" and self.file is not data[1]:
                    self.data_dictionary[self.file] = self._file_dict
                    self.file = data[1]
                    self._file_dict.clear()
                # ("match", False, datetime)
                elif data[0] == "match" and not data[1] and not self.is_match:
                    if not len(self._match_dict) == 0 or not len(self._spawn_dict) == 0:
                        self.set_new_match()
                    self._file_dict[self._match] = self._match_dict
                    self._match_dict.clear()
                    self.is_match = False
                    self.match = None
                # ("match", True, datetime)
                elif data[0] == "match" and data[1] and not self.is_match:
                    if not self._match:
                        raise ValueError("Expected self._match to have value")
                    self._match = data[2]
                    if not len(self._match_dict) == 0 or not len(self._spawn_dict) == 0:
                        self.set_new_match()
                # ("spawn", datetime)
                elif data[0] == "spawn":
                    self.set_new_spawn()
                    self._spawn = data[1]
                else:
                    raise ValueError("Unexpected data received: ", str(data))
            screen = vision.get_cv2_screen()
            pointer_cds = vision.get_pointer_position_win32()
            power_mgmt = vision.get_power_management(screen)
            health_hull = vision.get_ship_health_hull(screen)
            (health_shields_f, health_shields_r) = vision.get_ship_health_shields(screen)
            current_time = datetime.now()
            # TODO: get_tracking_degrees(*args)
            distance = vision.get_distance_from_center(pointer_cds)
            tracking_degrees = vision.get_tracking_degrees(distance)
            self._cursor_pos_dict[current_time] = pointer_cds
            self._power_mgmt_dict[current_time] = power_mgmt
            self._health_dict[current_time] = (health_hull, health_shields_f, health_shields_r)
            self._tracking_dict[current_time] = tracking_degrees
            while not self._internal_queue.empty():
                data = self._internal_queue.get()
                if "mouse" in data[0]:
                    self._clicks_dict[data[2]] = (data[0], data[1])
                else:
                    self._keys_dict[data[2]] = (data[0], data[1])
            while not self.query_queue.empty():
                command = self.query_queue.get()
                if command == "power_mgmt":
                    self.return_queue.put(power_mgmt)
                elif command == "health":
                    self.return_queue.put((health_hull, health_shields_f, health_shields_r))
                elif command == "tracking":
                    self.return_queue.put(tracking_degrees)
            self._spawn_dict["power_mgmt"] = self._power_mgmt_dict
            self._spawn_dict["cursor_pos"] = self._cursor_pos_dict
            self._spawn_dict["clicks"] = self._clicks_dict
            self._spawn_dict["keys"] = self._keys_dict
            self._spawn_dict["health"] = self._health_dict
            self._match_dict[self._spawn] = self._spawn_dict
            self._file_dict[self._match] = self._match_dict
            self.data_dictionary[self._file] = self._file_dict
            self.save_data_dictionary()
        self.close()

    # TODO: Add RGB capabilities
    # TODO: Add security measures (key filters)
    def on_press_kb(self, key):
        if key in keys:
            key = keys[key]
        self._internal_queue.put(("keypress", key, datetime.now()))

    def on_press_ms(self, key):
        if key in keys:
            key = keys[key]
        self._internal_queue.put("mousepress", key, datetime.now())

    def on_release_ms(self, key):
        if key in keys:
            key = keys[key]
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
        self.save_data_dictionary()

    def save_data_dictionary(self):
        with open(self.pickle_name, "w") as fo:
            pickle.dump(self.data_dictionary, fo)

    def set_new_spawn(self):
        self._match_dict[self._spawn] = self._spawn_dict
        self._spawn_dict.clear()
        self._power_mgmt_dict.clear()
        self._cursor_pos_dict.clear()
        self._clicks_dict.clear()
        self._keys_dict.clear()
        self._health_dict.clear()

    def set_new_match(self):
        self._match_dict[self._spawn] = self._spawn_dict
        self.data_dictionary[self._file][self._match] = self._match_dict
        self._match_dict.clear()
        self._spawn_dict.clear()
        self._power_mgmt_dict.clear()
        self._cursor_pos_dict.clear()
        self._clicks_dict.clear()
        self._keys_dict.clear()
        self._health_dict.clear()


class MouseCounter(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.gathered_date = {}

    def run(self):
        pass

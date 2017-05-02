﻿# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# Written by Daethyra, edited by RedFantom

from decimal import Decimal
import datetime
import re
from parsing.stalking import LogStalker
import variables
from tkMessageBox import showerror
from screen import ScreenParser
from Queue import Queue
from frames.screenoverlay import HitChanceOverlay


class Parser(object):
    """Parse a SWTOR combat log file. Each instance is a different
    file. The parser is designed for GSF battles

    For each statistic (damage done, taken and self damage, healing
    recieved, abilities used, critical luck) there is a list where
    each element is the respective amount done per match.
    (=> length of list = # of matches)

    The element of this lists are themself a list where the elemnts represent
    the spawns. The only elements not to be a list are abilites and crit luck,
    which are a tuple and a dictionary respectivly.
    (=> length of list = # of spawns)

    The abilities dictionary has as key the name of the ability and
    as value a ?list/dictionary? containig the respective amount for each statistic.
    This dictionary is then stored in the list abilities for each match.

    The crit luck tuple contains the absolute amount of critical hit,
    and the relative amount #critcal hit / #hit.
    There is no specific crit luck information per spawn. This is
    calculated only per match.

    To clarify which list is what, here is a short reference:
    :var: spawn_* is the list updated live
    :var: tmp_* is the list of the live match, containig infos per spawn
    :var: * is the list of the parse, containing infos per match

    Usage Example:

    >>> # put the path in config.ini
    >>> config = read_config()
    >>> stalker = LogStalker(config['path'], callback=callback)
    >>> stalker.loop()

    To access the parse data you need to modify the callback function under the 'HERE' comment
    Example:

    >>> def callback(...):
    ...     [...]
    ...     for line in lines:
    ...         process = line_to_dictionary(line)
    ...         parser.parse(process)
    ...         # HERE
    ...         damage_done = parser.tmp_dmg_done
    """

    DEBUG = False

    def __init__(self, spawn_callback, match_callback, new_match_callback, insert, screen=False, screenoverlay=False,
                 ship=None):
        if not screen and screenoverlay:
            showerror("Error", "Screen parsing disabled but screen parsing overlay enabled.")
            raise ValueError("screenoverlay True but screen False")
        if screen and not ship:
            showerror("Error", "Screen parsing enabled but no ship object acquired.")
            # raise ValueError("screen True but ship None")

        if screen:
            self.data_queue = Queue()
            self.exit_queue = Queue()
            self.query_queue = Queue()
            self.return_queue = Queue()
            self.screenparser = ScreenParser(data_queue=self.data_queue, exit_queue=self.exit_queue,
                                             query_queue=self.query_queue, return_queue=self.return_queue)
            self.screenparser.start()
        else:
            self.screenparser = None

        if screenoverlay:
            self.screenoverlay = HitChanceOverlay(variables.main_window)
            self.screenoverlay.withdraw()
        else:
            self.screenoverlay = None

        self.player_name = ''
        self.crit_nr = 0
        self.is_match = False

        self.spawn_callback = spawn_callback  # Function to call when a new spawn is detected
        self.match_callback = match_callback  # Function to call when the end of a match is detected
        self.new_match_callback = new_match_callback  # Function to call when a new match is detected
        self.insert = insert  # Function to call when a new line is parsed to insert it into the events box of the UI

        self.abilities, self.dmg_done, self.dmg_taken = [], [], []
        self.healing_rcvd, self.self_dmg, self.crit_luck = [], [], []
        self.recent_enemies = {}

        self.tmp_dmg_done, self.tmp_dmg_taken, self.tmp_healing_rcvd = [], [], []
        self.tmp_selfdmg = []
        self.tmp_abilities = {}

        self.spawn_dmg_done, self.spawn_dmg_taken = [], []
        self.spawn_healing_rcvd, self.spawn_selfdmg = [], []

        self.active_id = ''
        self.active_ids = []

        self.hold = 0
        self.hold_list = []

        self.spawns = 0  # The amount of spawns so far

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        self.close()

    def parse(self, line, recursion=False):
        if self.screenparser and self.screenoverlay:
            self.query_queue.put("tracking")
            degrees = self.return_queue.get()
            self.screenoverlay.set_geometry()
            self.screenoverlay.set_percentage(str(degrees) + "%")

        print "Called."
        self.dprint("[DEBUG] line", line)
        if not line:
            print "[DEBUG] Line is of NoneType"
            # Should be return for #20?
            return

        if "SetLevel" in line:
            return

        # This block is for keeping track of recent enemies, but it causes RuntimeErrors
        # time_now = datetime.datetime.now()
        # for enemy, time in self.recent_enemies.iteritems():
        #    # Remove enemies that weren't registered in last ten seconds
        #    if (time_now - time).seconds >= 10:
        #        del self.recent_enemies[enemy]

        # If first line of the file, save the player name
        if self.player_name == '' and '@' in line['source']:
            self.player_name = line['source'][1:]
            variables.rt_name = self.player_name
            print self.player_name
        # Sometimes multiple log-ins are stored in one log
        # Then the player_name must be changed if it is a self-targeted ability
        if line['source'] == line['destination'] and "@" not in line['source'] and ":" not in line['source'] and \
                not bool(re.search(r'\d', line['source'])):
            if line['source'][1:] != self.player_name:
                self.player_name = line['source'][1:]
                variables.rt_name = self.player_name
                print self.player_name

        if not self.is_match and ('@' in line['source'] or '@' in line['destination']):
            self.dprint("[DEBUG] out of match, skip")
            return

        # if the active id is neither source nor destination, the player id has changed
        # meaning a new spawn.
        if self.active_id not in line['source'] and self.active_id not in line['destination']:
            print("[NEW SPAWN]", sum(self.spawn_dmg_done), sum(self.spawn_dmg_taken), sum(self.spawn_healing_rcvd),
                  sum(self.spawn_selfdmg))
            # Call the new spawn callback
            self.spawn_callback(self.spawn_dmg_done, self.spawn_dmg_taken, self.spawn_healing_rcvd, self.spawn_selfdmg)
            self.spawns += 1
            self.active_id = ''
            self.dprint("[DEBUG] resetting active id")
            self.dprint("[DEBUG] updating tmp_* and resetting spawn_*", self.spawn_dmg_done, sum(self.spawn_dmg_done))
            self.tmp_dmg_done.append(sum(self.spawn_dmg_done))
            self.tmp_dmg_taken.append(sum(self.spawn_dmg_taken))
            self.tmp_healing_rcvd.append(sum(self.spawn_healing_rcvd))
            self.tmp_selfdmg.append(sum(self.spawn_selfdmg))
            self.spawn_dmg_done, self.spawn_dmg_taken = [], []
            self.spawn_healing_rcvd, self.spawn_selfdmg = [], []
            self.dprint("[DEBUG] tmp_* updated", self.tmp_dmg_done)

        # if a self targeted ability update the active player id
        if line['source'] == line['destination']:
            self.dprint("[DEBUG] setting active id")
            self.active_id = line['source']
            if self.active_id not in self.active_ids:
                self.active_ids.append(self.active_id)

        self.dprint("[DEBUG] active id \'", self.active_id, "\'")

        # Insert the line (or the pretty version of it) into the events box of real-time parsing
        self.insert(line, variables.rt_timing, self.active_id)

        # if the active player id is emtpy, it is impossible to determine if
        # player is target or source, thus put this line on hold and return.
        # elif there is and active id and lines on hold, parse them again.
        if self.active_id is '':
            self.hold += 1
            self.hold_list.append(line)
            self.dprint("[DEBUG] hold", self.hold, self.hold_list)
            return
        elif self.active_id is not '' and self.hold > 0 and not recursion:
            self.dprint("[DEBUG] catching up")
            for elem in self.hold_list:
                self.parse(elem, recursion=True)
                self.hold_list = self.hold_list[1:]
            self.hold = 0
            self.dprint("[DEBUG] caught up")
            return

        self.dprint("[DEBUG] hold", self.hold)

        # start of a match
        if not self.is_match:
            if '@' not in line['source']:
                self.is_match = True
                # Call the callback for a new match
                self.new_match_callback()
                variables.rt_timing = datetime.datetime.strptime(line['time'][:-4], "%H:%M:%S")
                if self.screenoverlay:
                    self.screenoverlay.deiconify()

        if self.is_match:
            if '@' in line['source']:
                if "Safe Login" not in line['ability']:
                    self.dprint("[DEBUG] Line with '@' but no end of match detected")
                    return
                self.dprint("[DEBUG] end of match, resetting")
                # Call the end of match callback
                self.match_callback(self.tmp_dmg_done, self.tmp_dmg_taken, self.tmp_healing_rcvd, self.tmp_selfdmg)
                self.dprint("[DEBUG]", self.tmp_dmg_done, self.tmp_dmg_taken, self.tmp_healing_rcvd, self.tmp_selfdmg)
                print("[END OF MATCH]", sum(self.tmp_dmg_done), sum(self.tmp_dmg_taken), sum(self.tmp_healing_rcvd),
                      sum(self.tmp_selfdmg))
                self.is_match = False
                self.dmg_done.append(self.tmp_dmg_done)
                self.dmg_taken.append(self.tmp_dmg_taken)
                self.healing_rcvd.append(self.tmp_healing_rcvd)
                self.self_dmg.append(self.tmp_selfdmg)
                self.abilities.append(self.tmp_abilities)

                try:
                    crits = Decimal(float(self.crit_nr) / len(self.tmp_dmg_done))
                except ZeroDivisionError:
                    crits = 0
                crits = round(crits * 100, 1)
                self.crit_luck.append((self.crit_nr, crits))

                self.crit_nr = 0
                self.tmp_dmg_done, self.tmp_dmg_taken, self.tmp_healing_rcvd = [], [], []
                self.tmp_selfdmg = []
                self.tmp_abilities = {}
                self.active_id = ''
                self.spawns = 1
                self.active_ids = []
                # self.recent_enemies.clear()
                if self.screenoverlay:
                    self.screenoverlay.withdraw()
                return

            # Start parsing
            if 'Heal' in line['effect']:
                self.spawn_healing_rcvd.append(int(line['amount'].replace('*', '')))
                self.dprint("[DEBUG] heal", self.spawn_healing_rcvd)

            elif 'Damage' in line['effect']:
                if not line['amount'] is '':
                    if 'Selfdamage' in line['ability']:
                        self.spawn_selfdmg.append(int(line['amount'].replace('*', '')))
                        self.dprint("[DEBUG] self damage", self.spawn_selfdmg)

                    elif line['source'] in self.active_id:
                        if '*' in line['amount']:
                            self.crit_nr += 1

                        if line['amount'] is not '0':
                            self.spawn_dmg_done.append(int(line['amount'].replace('*', '')))
                            self.dprint("[DEBUG] damage done", self.spawn_dmg_done)
                    else:
                        self.spawn_dmg_taken.append(int(line['amount'].replace('*', '')))
                        self.dprint("[DEBUG] damage taken", self.spawn_dmg_taken)
                        # self.recent_enemies[line['destination']] = \
                        #    datetime.datetime.strptime(line['time'][:-4], "%H:%M:%S")

            if line['ability'] in self.tmp_abilities:
                self.tmp_abilities[line['ability']] += 1
            else:
                self.tmp_abilities[line['ability']] = 1
        print "Done"

    def close(self):
        pass

    def dprint(self, *args):
        if self.DEBUG:
            print(args)


# ===================================================================
# --- Utility Tools
# ===================================================================

def line_to_dictionary(line):
    logpaths = r'\[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \((.*?)\)'
    logpath = re.compile(logpaths)

    group = logpath.match(line) if isinstance(line, str) else logpath.match(line.decode('cp1252'))
    try:
        tuple_ = group.groups()
    except AttributeError as err:
        print("[DEBUG] line_to_dictionary(): arg:", line, "'tuple = group.groups()' error raised, with group: ", group)
        print(err)
        return

    colnames = ('time', 'source', 'destination', 'ability', 'effect', 'amount')
    log = dict(zip(colnames, tuple_))

    """
    if not log['ability'] is '':
        log['ability'] = log['ability'].rsplit(None, 1)[1][1:-1]
    """

    if not log['amount'] is '':
        log['amount'] = log['amount'].split(None, 1)[0]

    return log


def read_config():
    """
    Reads the config file and determines all the configuration
    variables.

    :return: dictionary containing all the needed information
    """
    values = {}
    with open('config.ini', 'r') as config:
        for line in config:
            if line is '' or line.startswith(';'):
                continue
            elif 'PATH' in line:
                elements = re.split("=", line)
                path = elements[1]
                # path = line.split(None, 2)[2]
                values['path'] = path
        return values

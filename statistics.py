﻿# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
import tkMessageBox
# General imports
import os
import decimal
import datetime
# Own modules
import variables
import abilities
import parse
import realtime
import toplevels


# Function that returns True if a file contains any GSF events
def check_gsf(file_name):
    with open(file_name, "r") as file_obj:
        for line in file_obj:
            if "@" not in line:
                file_obj.close()
                return True
            else:
                continue
    if not file_obj.closed:
        raise
    return False


# Class to calculate various statistics from files, and even folders
class statistics:
    # Calculate the statistics for a whole folder
    # TODO Finish folder statistics
    def folder_statistics(self):
        # Add a CombatLogs in a folder with GSF matches to a list of names
        self.file_list = []
        for file_name in os.listdir(os.getcwd()):
            if file_name.endswith(".txt") and check_gsf(file_name):
                self.file_list.append(file_name)

        # Define all variables needed to store the statistics
        total_ddealt = 0
        total_dtaken = 0
        total_hrecvd = 0
        total_selfdmg = 0
        total_timeplayed = 0
        avg_criticalluck = None
        avg_matchtime = None
        mostplayedship = None
        match_count = 0
        match_timings = None

        razor_count = 0
        legion_count = 0
        decimus_count = 0
        bloodmark_count = 0
        sting_count = 0
        blackbolt_count = 0
        mangler_count = 0
        dustmaker_count = 0
        jurgoran_count = 0
        imperium_count = 0
        quell_count = 0
        rycer_count = 0

        criticalnumber = 0
        criticaltotal = 0

        player_names = []
        splash = toplevels.splash_screen(variables.main_window, max=len(self.file_list))
        # Start looping through the files
        variables.files_done = 0
        for name in self.file_list:
            variables.files_done += 1
            splash.update_progress()
            with open(name, "r") as file_object:
                lines = file_object.readlines()
            name = parse.determinePlayerName(lines)
            if name not in player_names:
                player_names.append(name)
            player_numbers = parse.determinePlayer(lines)
            file_cube, match_timings, spawn_timings = parse.splitter(lines, player_numbers)
            for matrix in file_cube:
                match_count += 1
                for spawn in matrix:
                    ships_possible = parse.determineShip(spawn)
                    if len(ships_possible) == 1:
                        if ships_possible[0] == "Razorwire":
                            razor_count += 1
                        elif ships_possible[0] == "Legion":
                            legion_count += 1
                        elif ships_possible[0] == "Decimus":
                            decimus_count += 1
                        elif ships_possible[0] == "Bloodmark":
                            bloodmark_count += 1
                        elif ships_possible[0] == "Sting":
                            sting_count += 1
                        elif ships_possible[0] == "Blackbolt":
                            blackbolt_count += 1
                        elif ships_possible[0] == "Mangler":
                            mangler_count += 1
                        elif ships_possible[0] == "Dustmaker":
                            dustmaker_count += 1
                        elif ships_possible[0] == "Jurgoran":
                            jurgoran_count += 1
                        elif ships_possible[0] == "Imperium":
                            imperium_count += 1
                        elif ships_possible[0] == "Quell":
                            quell_count += 1
                        elif ships_possible[0] == "Rycer":
                            rycer_count += 1
            # Then get the useful information out of the matches
            (abilitiesdict, damagetaken, damagedealt, selfdamage, healingreceived, enemies,
             criticalcount, criticalluck, hitcount, enemydamaged, enemydamaget, match_timings,
             spawn_timings) = parse.parse_file(file_cube, player_numbers, match_timings, spawn_timings)
            for list in damagetaken:
                for number in list:
                    total_ddealt += number
            for list in damagedealt:
                for number in list:
                    total_dtaken += number
            for list in healingreceived:
                for number in list:
                    total_hrecvd += number
            for list in selfdamage:
                for number in list:
                    total_selfdmg += number
            for list in criticalluck:
                for number in list:
                    criticalnumber += 1
                    criticaltotal += number
            file_object.close()
        start_time = False
        previous_time = None
        for datetime in match_timings:
            if not start_time:
                previous_time = datetime
                continue
            else:
                total_timeplayed += datetime - previous_time
                previous_time = datetime
                continue
        (total_timeplayed_minutes, total_timeplayed_seconds) = divmod(total_timeplayed, 60)
        splash.destroy()
        try:
            damage_ratio_string = str(str(round(float(total_ddealt) / float(total_dtaken), 1)) + " : 1") + "\n"
        except ZeroDivisionError:
            damage_ratio_string = "0.0 : 1\n"
        # Return all statistics calculated
        statistics_string = (
        "- enemies" + "\n" + str(total_ddealt) + "\n" + str(total_dtaken) + "\n" + damage_ratio_string +
        str(total_selfdmg) + "\n" + str(total_hrecvd) + """\n-\n-\n-\n-\n-\n-""")
        return statistics_string

    @staticmethod
    def file_statistics(file_cube):
        player_list = []
        for match in file_cube:
            for spawn in match:
                player = parse.determinePlayer(spawn)
                for id in player:
                    player_list.append(id)

        (abs, damagetaken, damagedealt, selfdamage, healingreceived, enemies, criticalcount, criticalluck,
         hitcount, enemydamaged, enemydamaget, match_timings, spawn_timings) = \
            parse.parse_file(file_cube, player_list, variables.match_timings, variables.spawn_timings)
        total_abilities = {}
        total_damagetaken = 0
        total_damagedealt = 0
        total_selfdamage = 0
        total_healingrecv = 0
        total_enemies = []
        total_criticalcount = 0
        total_criticalluck = 0
        total_hitcount = 0
        total_enemydamaged = {}
        total_enemydamaget = {}
        total_match_timings = None
        total_spawn_timings = None

        for mat in abs:
            for dic in mat:
                for (key, value) in dic.iteritems():
                    if key not in total_abilities:
                        total_abilities[key] = value
                    else:
                        total_abilities[key] += value
        for lst in damagetaken:
            for amount in lst:
                total_damagetaken += amount
        for lst in damagedealt:
            for amount in lst:
                total_damagedealt += amount
        for lst in selfdamage:
            for amount in lst:
                total_selfdamage += amount
        for lst in healingreceived:
            for amount in lst:
                total_healingrecv += amount
        for matrix in enemies:
            for lst in matrix:
                for enemy in lst:
                    if enemy not in total_enemies:
                        total_enemies.append(enemy)
        for lst in criticalcount:
            for amount in lst:
                total_criticalcount += amount
        for lst in hitcount:
            for amount in lst:
                total_hitcount += amount
        try:
            total_criticalluck = decimal.Decimal(float(total_criticalcount / total_hitcount))
        except:
            total_criticalluck = 0
        total_enemydamaged = enemydamaged
        total_enemydamaget = enemydamaget

        abilities_string = "Ability\t\t\tTimes used\n\n"
        statistics_string = ""
        total_shipsdict = {}
        uncounted = 0
        for ship in abilities.ships:
            total_shipsdict[ship] = 0
        for match in file_cube:
            for spawn in match:
                ships_possible = parse.parse_spawn(spawn, player_list)[9]
                if len(ships_possible) == 1:
                    if ships_possible[0] == "Razorwire":
                        total_shipsdict["Razorwire"] += 1
                    elif ships_possible[0] == "Legion":
                        total_shipsdict["Legion"] += 1
                    elif ships_possible[0] == "Decimus":
                        total_shipsdict["Decimus"] += 1
                    elif ships_possible[0] == "Bloodmark":
                        total_shipsdict["Bloodmark"] += 1
                    elif ships_possible[0] == "Sting":
                        total_shipsdict["Sting"] += 1
                    elif ships_possible[0] == "Blackbolt":
                        total_shipsdict["Blackbolt"] += 1
                    elif ships_possible[0] == "Mangler":
                        total_shipsdict["Mangler"] += 1
                    elif ships_possible[0] == "Dustmaker":
                        total_shipsdict["Dustmaker"] += 1
                    elif ships_possible[0] == "Jurgoran":
                        total_shipsdict["Jurgoran"] += 1
                    elif ships_possible[0] == "Imperium":
                        total_shipsdict["Imperium"] += 1
                    elif ships_possible[0] == "Quell":
                        total_shipsdict["Quell"] += 1
                    elif ships_possible[0] == "Rycer":
                        total_shipsdict["Rycer"] += 1
                else:
                    uncounted += 1
        total_killsassists = 0
        for (key, value) in total_abilities.iteritems():
            if (len(key.strip()) >= 8 and len(key.strip()) <= 18):
                abilities_string = abilities_string + key.strip() + "\t\t%02d\n" % value
            elif (len(key.strip()) < 8):
                abilities_string = abilities_string + key.strip() + "\t\t\t%02d\n" % value
            elif (len(key.strip()) > 18):
                abilities_string = abilities_string + key.strip() + "\t%02d\n" % value
        for enemy in total_enemies:
            if total_enemydamaget[enemy] > 0:
                total_killsassists += 1
        total_criticalluck = round(total_criticalluck * 100, 2)
        deaths = 0
        for match in file_cube:
            deaths += len(match)
        try:
            damage_ratio_string = str(
                str(round(float(total_damagedealt) / float(total_damagetaken), 1)) + " : 1") + "\n"
        except ZeroDivisionError:
            damage_ratio_string = "0.0 : 1\n"
        statistics_string = (
        str(total_killsassists) + " enemies" + "\n" + str(total_damagedealt) + "\n" + str(total_damagetaken) + "\n" +
        damage_ratio_string +
        str(total_selfdamage) + "\n" + str(total_healingrecv) + "\n" +
        str(total_hitcount) + "\n" + str(total_criticalcount) + "\n" +
        str(total_criticalluck) + "%" + "\n" + str(deaths) + "\n-\n-")

        return abilities_string, statistics_string, total_shipsdict, total_enemies, total_enemydamaged, total_enemydamaget, uncounted

    @staticmethod
    def match_statistics(match):
        total_abilitiesdict = {}
        total_damagetaken = 0
        total_damagedealt = 0
        total_healingrecv = 0
        total_selfdamage = 0
        total_enemies = []
        total_criticalcount = 0
        total_hitcount = 0
        total_shipsdict = {}
        total_enemydamaged = {}
        total_enemydamaget = {}
        total_killsassists = 0
        ships_uncounted = 0
        abilities_string = "Ability\t\t\tTimes used\n\n"
        for spawn in match:
            (abilitiesdict, damagetaken, damagedealt, healingreceived, selfdamage, enemies, criticalcount,
             criticalluck, hitcount, ships_list, enemydamaged, enemydamaget) = parse.parse_spawn(spawn,
                                                                                                 variables.player_numbers)
            total_abilitiesdict.update(abilitiesdict)
            total_damagetaken += damagetaken
            total_damagedealt += damagedealt
            total_healingrecv += healingreceived
            total_selfdamage += selfdamage
            for enemy in enemies:
                if enemy not in total_enemies:
                    total_enemies.append(enemy)
            total_criticalcount += criticalcount
            total_hitcount += hitcount
            for key, value in enemydamaged.iteritems():
                if key in total_enemydamaged:
                    total_enemydamaged[key] += value
                else:
                    total_enemydamaged[key] = value
            for key, value in enemydamaget.iteritems():
                if key in total_enemydamaget:
                    total_enemydamaget[key] += value
                else:
                    total_enemydamaget[key] = value
            if len(ships_list) != 1:
                ships_uncounted += 1
                ships_list = []
            for ship in ships_list:
                if ship in total_shipsdict:
                    total_shipsdict[ship] += 1
                else:
                    total_shipsdict[ship] = 1
        for (key, value) in total_abilitiesdict.iteritems():
            if (len(key.strip()) >= 8 and len(key.strip()) <= 18):
                abilities_string = abilities_string + key.strip() + "\t\t%02d\n" % value
            elif (len(key.strip()) < 8):
                abilities_string = abilities_string + key.strip() + "\t\t\t%02d\n" % value
            elif (len(key.strip()) > 18):
                abilities_string = abilities_string + key.strip() + "\t%02d\n" % value
        for enemy in total_enemies:
            if total_enemydamaget[enemy] > 0:
                total_killsassists += 1
        try:
            total_criticalluck = decimal.Decimal(float(total_criticalcount) / float(total_hitcount))
            total_criticalluck = round(total_criticalluck * 100, 2)
        except ZeroDivisionError:
            total_criticalluck = 0
        total_shipsdict["Uncounted"] = ships_uncounted
        delta = datetime.datetime.strptime(
            realtime.line_to_dictionary(match[len(match) - 1][len(match[len(match) - 1]) - 1]) \
                ['time'][:-4].strip(), "%H:%M:%S") - \
                datetime.datetime.strptime(variables.match_timing.strip(), "%H:%M:%S")
        elapsed = divmod(delta.total_seconds(), 60)
        string = "%02d:%02d" % (int(round(elapsed[0], 0)), int(round(elapsed[1], 0)))
        try:
            dps = round(total_damagedealt / delta.total_seconds(), 1)
        except ZeroDivisionError:
            dps = 0
        try:
            damage_ratio_string = str(
                str(round(float(total_damagedealt) / float(total_damagetaken), 1)) + " : 1") + "\n"
        except ZeroDivisionError:
            damage_ratio_string = "0.0 : 1\n"
        statistics_string = (str(total_killsassists) + " enemies" + "\n" + str(total_damagedealt) + "\n" +
                             str(total_damagetaken) + "\n" + damage_ratio_string +
                             str(total_selfdamage) + "\n" + str(total_healingrecv) + "\n" +
                             str(total_hitcount) + "\n" + str(total_criticalcount) + "\n" +
                             str(total_criticalluck) + "%" + "\n" + str(len(match) - 1) + "\n" + string + "\n" + str(
            dps))
        return abilities_string, statistics_string, total_shipsdict, total_enemies, total_enemydamaged, total_enemydamaget

    @staticmethod
    def spawn_statistics(spawn):
        (abilitiesdict, damagetaken, damagedealt, healingreceived, selfdamage, enemies, criticalcount,
         criticalluck, hitcount, ships_list, enemydamaged, enemydamaget) = parse.parse_spawn(spawn,
                                                                                             variables.player_numbers)
        killsassists = 0
        for enemy in enemies:
            if enemydamaget[enemy] > 0:
                killsassists += 1
        abilities_string = "Ability\t\t\tTimes used\n\n"
        ship_components = []
        for key in abilitiesdict:
            if key in abilities.components:
                ship_components.append(key)
        comps = ["Primary", "Secondary", "Engine", "Shield", "System"]
        for (key, value) in abilitiesdict.iteritems():
            if (len(key.strip()) >= 8 and len(key.strip()) <= 18):
                abilities_string = abilities_string + key.strip() + "\t\t%02d\n" % value
            elif (len(key.strip()) < 8):
                abilities_string = abilities_string + key.strip() + "\t\t\t%02d\n" % value
            elif (len(key.strip()) > 18):
                abilities_string = abilities_string + key.strip() + "\t%02d\n" % value
        for component in ship_components:
            if component in abilities.primaries:
                if "Rycer" in ships_list:
                    if comps[0] == "Primary":
                        comps[0] = component
                    else:
                        comps[0] += "/" + component
                else:
                    comps[0] = component
            elif component in abilities.secondaries:
                if "Quell" in ships_list:
                    if comps[1] == "Secondary":
                        comps[1] = component
                    else:
                        comps[1] += "/" + component
                else:
                    comps[1] = component
            elif component in abilities.engines:
                comps[2] = component
            elif component in abilities.shields:
                comps[3] = component
            elif component in abilities.systems:
                comps[4] = component
            else:
                tkMessageBox.showinfo("WHAT?!", "DID GSF GET AN UPDATE?!")
        if "Primary" in comps:
            del comps[comps.index("Primary")]
        if "Secondary" in comps:
            del comps[comps.index("Secondary")]
        if "Engine" in comps:
            del comps[comps.index("Engine")]
        if "Shield" in comps:
            del comps[comps.index("Shield")]
        if "System" in comps:
            del comps[comps.index("System")]
        last_line_dict = realtime.line_to_dictionary(spawn[len(spawn) - 1])
        timing = datetime.datetime.strptime(last_line_dict['time'][:-4], "%H:%M:%S")
        delta = timing - datetime.datetime.strptime(variables.spawn_timing.strip(), "%H:%M:%S")
        elapsed = divmod(delta.total_seconds(), 60)
        string = "%02d:%02d" % (int(round(elapsed[0], 0)), int(round(elapsed[1], 0)))
        try:
            dps = round(damagedealt / delta.total_seconds(), 1)
        except ZeroDivisionError:
            dps = 0
        try:
            damage_ratio_string = str(str(round(float(damagedealt) / float(damagetaken), 1)) + " : 1") + "\n"
        except ZeroDivisionError:
            damage_ratio_string = "0.0 : 1\n"
        statistics_string = (str(killsassists) + " enemies" + "\n" + str(damagedealt) + "\n" + str(damagetaken) + "\n" +
                             damage_ratio_string +
                             str(selfdamage) + "\n" + str(healingreceived) + "\n" +
                             str(hitcount) + "\n" + str(criticalcount) + "\n" +
                             str(criticalluck) + "%" + "\n" + "-\n" + string + "\n" + str(dps))
        return abilities_string, statistics_string, ships_list, comps, enemies, enemydamaged, enemydamaget


colnames = ('time', 'source', 'destination', 'ability', 'effect', 'amount')


def pretty_event(line_dict, start_of_match, active_id):
    timing = datetime.datetime.strptime(line_dict['time'][:-4], "%H:%M:%S")
    bg_color = None
    fg_color = None
    try:
        delta = timing - start_of_match
        elapsed = divmod(delta.total_seconds(), 60)
        string = "%02d:%02d    " % (int(round(elapsed[0], 0)), int(round(elapsed[1], 0)))
    except TypeError:
        string = "00:00" + 4 * " "
    except:
        print "[DEBUG] An unknown error occurred while doing the delta thing"
        return
    # If the player name is too long, shorten it
    if variables.rt_name:
        if len(variables.rt_name) > 14:
            variables.rt_name = variables.rt_name[:14]
    if line_dict['source'] == active_id:
        if variables.rt_name:
            string += variables.rt_name + (14 - len(variables.rt_name) + 4) * " "
        else:
            string += "You" + " " * (11 + 4)
    elif line_dict['source'] == "":
        string += "System" + (8 + 4) * " "
    else:
        string += line_dict["source"] + (4 + 14 - len(line_dict['source'])) * " "
    if line_dict['destination'] == active_id:
        if variables.rt_name:
            string += variables.rt_name + (14 - len(variables.rt_name) + 4) * " "
        else:
            string += "You" + " " * (11 + 4)
    elif line_dict['destination'] == "":
        string += "System" + (8 + 4) * " "
    else:
        string += line_dict["destination"] + (4 + 14 - len(line_dict['destination'])) * " "
    ability = line_dict['ability'].split(' {', 1)[0].strip()
    if ability == "":
        return
    string += ability + (26 - len(ability)) * " "
    if "Damage" in line_dict['effect']:
        string += "Damage  " + line_dict['amount'].replace("\n", "")
        if line_dict['destination'] == active_id:
            if variables.settings_obj.event_colors == "basic":
                if line_dict['source'] == active_id:
                    bg_color = variables.color_scheme['selfdmg'][0]
                    fg_color = variables.color_scheme['selfdmg'][1]
                else:
                    bg_color = variables.color_scheme['dmgt_pri'][0]
                    fg_color = variables.color_scheme['dmgt_pri'][1]
            else:
                if line_dict['source'] == active_id:
                    bg_color = variables.color_scheme['selfdmg'][0]
                    fg_color = variables.color_scheme['selfdmg'][1]
                else:
                    if ability in abilities.primaries:
                        bg_color = variables.color_scheme['dmgt_pri'][0]
                        fg_color = variables.color_scheme['dmgt_pri'][1]
                    elif ability in abilities.secondaries:
                        bg_color = variables.color_scheme['dmgt_sec'][0]
                        fg_color = variables.color_scheme['dmgt_sec'][1]
                    else:
                        bg_color = variables.color_scheme['dmgt_pri'][0]
                        fg_color = variables.color_scheme['dmgt_pri'][1]
        else:
            if ability in abilities.primaries:
                bg_color = variables.color_scheme['dmgd_pri'][0]
                fg_color = variables.color_scheme['dmgd_pri'][1]
            elif ability in abilities.secondaries:
                bg_color = variables.color_scheme['dmgd_sec'][0]
                fg_color = variables.color_scheme['dmgd_sec'][1]
            else:
                bg_color = variables.color_scheme['dmgd_pri'][0]
                fg_color = variables.color_scheme['dmgd_pri'][1]
    elif "Heal" in line_dict['effect']:
        string += "Heal    " + line_dict['amount'].replace("\n", "")
        if line_dict['source'] == active_id:
            bg_color = variables.color_scheme['selfheal'][0]
            fg_color = variables.color_scheme['selfheal'][1]
        else:
            bg_color = variables.color_scheme['healing'][0]
            fg_color = variables.color_scheme['healing'][1]
    elif "AbilityActivate" in line_dict['effect']:
        string += "AbilityActivate"
        if variables.settings_obj.event_colors == "advanced":
            for engine in abilities.engines:
                if engine in string:
                    bg_color = variables.color_scheme['engine'][0]
                    fg_color = variables.color_scheme['engine'][1]
                    break
            for shield in abilities.shields:
                if shield in string:
                    bg_color = variables.color_scheme['shield'][0]
                    fg_color = variables.color_scheme['shield'][1]
                    break
            for system in abilities.systems:
                if system in string:
                    bg_color = variables.color_scheme['system'][0]
                    fg_color = variables.color_scheme['system'][1]
                    break
            if not bg_color:
                bg_color = variables.color_scheme['other'][0]
                fg_color = variables.color_scheme['other'][1]
        elif variables.settings_obj.event_colors == "basic":
            bg_color = variables.color_scheme['other'][0]
            fg_color = variables.color_scheme['other'][1]
    else:
        return
    if not bg_color:
        bg_color = variables.color_scheme['default'][0]
        fg_color = variables.color_scheme['default'][1]
    variables.insert_queue.put((string, bg_color, fg_color))


def print_event(line_dict, start_of_match, player):
    line_dict_new = None
    try:
        line_dict_new = realtime.line_to_dictionary(line_dict)
    except TypeError:
        pass
    if not line_dict_new:
        pass
    else:
        line_dict = line_dict_new
    timing = datetime.datetime.strptime(line_dict['time'][:-4], "%H:%M:%S")
    start_of_match = datetime.datetime.strptime(start_of_match, "%H:%M:%S")
    bg_color = None
    fg_color = None
    try:
        delta = timing - start_of_match
        elapsed = divmod(delta.total_seconds(), 60)
        string = "%02d:%02d    " % (int(round(elapsed[0], 0)), int(round(elapsed[1], 0)))
    except TypeError:
        string = "00:00" + 4 * " "
    except:
        print "[DEBUG] An unknown error occurred while doing the delta thing"
        return
    # If the player name is too long, shorten it
    if variables.rt_name:
        if len(variables.rt_name) > 14:
            variables.rt_name = variables.rt_name[:14]
    if line_dict['source'] in player:
        if variables.rt_name:
            string += variables.rt_name + (14 - len(variables.rt_name) + 4) * " "
        else:
            string += "You" + " " * (11 + 4)
    elif line_dict['source'] == "":
        string += "System" + (8 + 4) * " "
    else:
        string += line_dict["source"] + (4 + 14 - len(line_dict['source'])) * " "
    if line_dict['destination'] in player:
        if variables.rt_name:
            string += variables.rt_name + (14 - len(variables.rt_name) + 4) * " "
        else:
            string += "You" + " " * (11 + 4)
    elif line_dict['destination'] == "":
        string += "System" + (8 + 4) * " "
    else:
        string += line_dict["destination"] + (4 + 14 - len(line_dict['destination'])) * " "
    ability = line_dict['ability'].split(' {', 1)[0].strip()
    if ability == "":
        return
    string += ability + (26 - len(ability)) * " "
    if "Damage" in line_dict['effect']:
        string += "Damage  " + line_dict['amount'].replace("\n", "")
        if line_dict['destination'] in player:
            if variables.settings_obj.event_colors == "basic":
                if line_dict['source'] in player:
                    bg_color = variables.color_scheme['selfdmg'][0]
                    fg_color = variables.color_scheme['selfdmg'][1]
                else:
                    bg_color = variables.color_scheme['dmgt_pri'][0]
                    fg_color = variables.color_scheme['dmgt_pri'][1]
            else:
                if line_dict['source'] in player:
                    bg_color = variables.color_scheme['selfdmg'][0]
                    fg_color = variables.color_scheme['selfdmg'][1]
                else:
                    if ability in abilities.primaries:
                        bg_color = variables.color_scheme['dmgt_pri'][0]
                        fg_color = variables.color_scheme['dmgt_pri'][1]
                    elif ability in abilities.secondaries:
                        bg_color = variables.color_scheme['dmgt_sec'][0]
                        fg_color = variables.color_scheme['dmgt_sec'][1]
                    else:
                        bg_color = variables.color_scheme['dmgt_pri'][0]
                        fg_color = variables.color_scheme['dmgt_pri'][1]
        else:
            if ability in abilities.primaries:
                bg_color = variables.color_scheme['dmgd_pri'][0]
                fg_color = variables.color_scheme['dmgd_pri'][1]
            elif ability in abilities.secondaries:
                bg_color = variables.color_scheme['dmgd_sec'][0]
                fg_color = variables.color_scheme['dmgd_sec'][1]
            else:
                bg_color = variables.color_scheme['dmgd_pri'][0]
                fg_color = variables.color_scheme['dmgd_pri'][1]
    elif "Heal" in line_dict['effect']:
        string += "Heal    " + line_dict['amount'].replace("\n", "")
        if line_dict['source'] in player:
            bg_color = variables.color_scheme['selfheal'][0]
            fg_color = variables.color_scheme['selfheal'][1]
        else:
            bg_color = variables.color_scheme['healing'][0]
            fg_color = variables.color_scheme['healing'][1]
    elif "AbilityActivate" in line_dict['effect']:
        string += "AbilityActivate"
        if variables.settings_obj.event_colors == "advanced":
            for engine in abilities.engines:
                if engine in string:
                    bg_color = variables.color_scheme['engine'][0]
                    fg_color = variables.color_scheme['engine'][1]
                    break
            for shield in abilities.shields:
                if shield in string:
                    bg_color = variables.color_scheme['shield'][0]
                    fg_color = variables.color_scheme['shield'][1]
                    break
            for system in abilities.systems:
                if system in string:
                    bg_color = variables.color_scheme['system'][0]
                    fg_color = variables.color_scheme['system'][1]
                    break
            if not bg_color:
                bg_color = variables.color_scheme['other'][0]
                fg_color = variables.color_scheme['other'][1]
        elif variables.settings_obj.event_colors == "basic":
            bg_color = variables.color_scheme['other'][0]
            fg_color = variables.color_scheme['other'][1]
    else:
        return
    if not bg_color:
        bg_color = variables.color_scheme['default'][0]
        fg_color = variables.color_scheme['default'][1]
    return string, bg_color, fg_color

﻿# Written by RedFantom, Wing Commander of Thranta Squadron and Daethyra, Squadron Leader of Thranta Squadron
# For license see LICENSE

import re
import os
import vars
from datetime import datetime
from decimal import Decimal

# Function that splits the lines it gets into new lists of lines according
# to the matches and returns the timings of these matches along with them
def splitter(lines, playerList):
    # Create empty lists for appending
    file = []
    match = []
    spawn = []
    spawnTimingsMatrix = []
    spawnTimingsList = []
    matchTimingsList = []
    matchStarted = False
    currentPlayer = None
    # Start looping through the lines
    for line in lines:
        # Split the line into elements
        elements = re.split(r"[\[\]]", line)
        # Take the relevant information from these elements
        timestring = elements[1]
        source = elements[3]
        target = elements[5]
        # If "@" is not in source, then the ability is an in-match ability
        if "@" not in source:
            # If the match hadn't started, it has now started and the the spawn
            # must be saved. The time of the spawn and the time the match has
            # started are also saved.
            if matchStarted == False:
                matchStarted = True
                # Set the currentPlayer to be either the source or the target,
                # if the player is in the list of player ID numbers
                if source in playerList:
                    currentPlayer = source
                elif target in playerList:
                    currentPlayer = target
                # Add the line to the current spawn listdir
                spawn.append(line)
                # Add the spawntime and the matchtime to the lists
                spawnTimingsList.append(timestring)
                matchTimingsList.append(timestring)
            # If the match had started, then the match continues
            else:
                # If the source is in the playerlist, but the source is not the
                # same as the current player, then the player has respawned and
                # the currentPlayer must change to the new value. The current
                # spawn list must be appended to the match matrix and emptied to
                # hold a new spawn.
                if source in playerList:
                    # If currentPlayer != source, the player has respawned
                    if currentPlayer != source:
                        # Add the spawn list to the match matrix
                        match.append(spawn)
                        # Empty the spawn list
                        spawn = []
                        # Add the current line to the now empty list
                        spawn.append(line)
                        # Add the time of the spawn to the list
                        spawnTimingsList.append(timestring)
                        # Set the new currentPlayer to the new ID number
                        currentPlayer = source
                    # Else, the match and spawn continue
                    else:
                        # Add the line to the list and continue
                        spawn.append(line)
                # If the target is in the playerList, but the target is not the
                # same as the current player, then the player has respawned and
                # the currentPlayer must change to the new value. The current
                # spawn list must be appended to the match matrix and emptied to
                # hold a new spawn.
                elif target in playerList:
                    # If currentPlayer != target, the player has respawned
                    if currentPlayer != target:
                        # Add the spawn list to the match matrix
                        match.append(spawn)
                        # Empty the spawn list
                        spawn = []
                        # Add the current line to the now empty list
                        spawn.append(line)
                        # Add the time of the spawn to the list
                        spawnTimingsList.append(timestring)
                        # Set the new currentPlayer to the new ID number
                        currentPlayer = target
                    # Else, the match and spawn continue
                    else:
                        # Add the line to the list and continue
                        spawn.append(line)
        # "@" is in the line, then it is a normal ability
        else:
            # If a match had started, then now it has ended
            if matchStarted == True:
                # End of the match
                matchStarted = False
                # Add the match matrix to the file Cube
                file.append(match)
                # Add the endtime of the match to the list
                matchTimingsList.append(timestring)
                # Add the spawnTimingsList to the matrix with [match][spawn]
                spawnTimingsMatrix.append(spawnTimingsList)
                # Clear the lists
                spawnTimingsList = []
                spawn = []
                match = []
                # Clear the currentPlayer
                currentPlayer = None
    # Return a 3D-matrix/cube of the lines of the file with [match][spawn][line]
    # and a timingslist for the matches and a timings matrix for the spawns with
    # [match][spawn]. For the spawns, only the start times are recorded.
    return file, matchTimingsList, spawnTimingsMatrix


# Function that reads the file supplied by the user and parses them accordingly
def parseFile(file, matchTimingsList, spawnTimingsMatrix, player):
    # Declare the values that are needed for parsing
    abilitiesOccurrences = []
    copilotCooldown = 60
    damageTaken = [0 for match in matches]
    damageDealt = [0 for match in matches]
    selfdamage = [0 for match in matches]
    healingReceived = [0 for match in matches]
    abilities = {}
    enemyMatrix = []
    enemies = []
    enemyDamageDealt = {}
    enemyDamageTaken = {}
    criticalLuck = []
    criticals, hits = 0, 0

    abilitiesOccurrencesMatrix = []
    damageTakenMatrix = []
    damageDealtMatrix = []
    selfdamageMatrix = []
    healingReceivedMatrix = []
    enemyCube = []
    enemyDamageDealtList = []
    enemyDamageTakenList = []
    criticalLuckMatrix = []

    # For all the cooldowns the maximum (default) cooldown is used. These variables are for future features.
    engineCooldowns = {'Retro Thrusters': 20, 'Koiogran Turn': 20, 'Snap Turn': 20, 'Power Dive': 15,
                       'Barrel Roll': 30, 'Shield Power Converter': 9, 'Weapon Power Converter': 9,
                       'Interdiction Drive': 60, 'Rotational Thrusters': 10, 'Hyperspace Beacon': 180}
    shieldCooldowns = {'Charged Plating': 30, 'Overcharged Shield': 60, 'Shield Projector': 30,
                       'Directional Shield': 0, 'Distortion Field': 30, 'Feedback Shield': 30, 'Repair Drone': 90,
                       'Fortress Shield': 30}
    systemCooldowns = {'Combat Command': 90, 'Repair Probes': 90, 'Remote Slicing': 60, 'Interdiction Mine': 20,
                       'Concussion Mine': 20, 'Ion Mine': 20, 'Booster Recharge': 60, 'Targeting Telemetry': 45,
                       'Blaster Overcharge': 60, 'EMP Field': 60}

    # Create a list of datetime variables from the timings list returned by the splitter()
    matchTimings = []
    for time in matchTimingsList:
        # The last part of each item of the list contains .xxx, with the x's meaning
        # thousands of a second. These can not be stored in datetime variables.
        time = time[:-4]
        matchTimings.append(datetime.strptime(time, '%H:%M:%S'))
    spawnTimings = []
    spawnTimingsTemp = []
    for list in spawnTimingsMatrix:
        for time in list:
            time = time[:-4]
            spawnTimingsTemp.append(datetime.strptime(time, '%H:%M:%S'))
        spawnTimings.append(spawnTimingsTemp)
        spawnTimingsTemp = []


    # Here parsing starts, loop through the matches. Individual matchDamage must be possible by using more lists.
    # For now, all matches in a file are parsed.
    currentMatch = 0

    # Start looping through the matches to be able to return separate results for each match
    # matches is a matrix, match becomes a list
    for match in file:
        # match is a list, event becomes a string
        for spawn in match:
            for event in spawn:
                # Split the event string into smaller strings containing the information we want.
                elements = re.split(r"[\[\]]", event)
                # sign those elements to individual variables to keep things clear.
                timestring = elements[1]
                source = elements[3]
                target = elements[5]
                ability = elements[7]
                effect = elements[9]
                damagestring = elements[10]

                # The ability always has an ID number behind it between {}, it must be removed
                # This ID number is for recognition between languages. The ID number is always the same,
                # even where the ability name is not. Only English is supported at this time.
                ability = ability.split(' {', 1)[0]


                # Put the ability in the dictionary if it was used by the player and is not in it.
                # Otherwise, add one to the abilities count.
                # The abilities count is not accurate, because different abilities have periodic
                # effects and appear multiple times after activation.
                # Ion Railgun effect Reactor Disruption is activated by the player
                if source in player:

                    if "Ion Railgun" in ability:
                        if source != target:
                            if ability not in abilities:
                                abilities[ability] = 1
                            else:
                                abilities[ability] += 1
                    else:
                        if ability not in abilities:
                            abilities[ability] = 1
                        else:
                            abilities[ability] += 1

                # If Damage is in the effect string, damage was dealt
                if "kinetic" in event:
                    # Takes damagestring and split after the pattern (stuff in here) and take the second element
                    # containing the "stuff in here"
                    # example: (436 kinetic {836045448940873}) => ['', '436 kinetic {836045448940873}', '']
                    damagestring = re.split(r"\((.*?)\)", damagestring)[1]
                    # now split it and take only the number
                    damagestring = damagestring.split(None, 1)[0]

                    # Sometimes the string is empty, even while there is "Damage" in the line. Then 0 damage is added.
                    if damagestring == "":
                        damagestring = "0"

                    # If the source is in the player list, which contains all the player's ID numbers, the damage is
                    # inflicted BY the player
                    if source in player:
                        # If "*" is in the damgegestring, then the hit was a critical hit
                        if '*' in damagestring:
                            criticals += 1
                        # Remove the "*" from the damagestring, as it has no use anymore and will generate an error
                        # when using int() and then add the damage to the total
                        damageDealt[currentMatch] += int(damagestring.replace('*', ''))
                        hits += 1
                        # If the target was not yet in the enemies list, and the target is not in the player list,
                        # which would mean the damage is selfdamage, then add the target to the list
                        if(target not in enemies and target not in player):
                            enemies.append(target)
                        # The same goes here, but here the damage is also assigned to the enemy in the dictionary
                        if(target not in enemyDamageTaken and target not in player):
                            enemyDamageTaken[target] = int(damagestring.replace('*', ''))
                        # If the target was already in the dictionary, then it should still be added,
                        # and the damage must be added to its total, but again only if the ID number was not in
                        # the player list
                        else:
                            if target not in player:
                                enemyDamageTaken[target] += int(damagestring.replace('*', ''))
                        # If the target was not yet in the damage dealt dictionary, then it should be added anyway,
                        # so as not to produce errors when looping through it for display.
                        if(target not in enemyDamageDealt and target not in player):
                            enemyDamageDealt[target] = 0
                    # If this is not the case, the damage is inflicted to the player
                    else:
                        # The damage must be added to the total of damage taken during the match
                        damageTaken[currentMatch] += int(damagestring.replace('*', ''))
                        # If the source of the damage was not yet in enemies, then the ID number must be added
                        # to the list. No checking for whether the ID is an ID in the player list is necessary,
                        # because it can't be selfdamage because the else statement concludes that source is not
                        # in the player list anyway.
                        if source not in enemies:
                            enemies.append(source)
                        # If the source ID was not yet in enemyDamageDealt, it must be added with the damage
                        if source not in enemyDamageDealt:
                            enemyDamageDealt[source] = int(damagestring.replace('*', ''))
                        # If it was, then the damage must be added to the total
                        else:
                            enemyDamageDealt[source] += int(damagestring.replace('*', ''))
                        # If the source ID was not yet in enemyDamageTaken, then it must be added to prevent anyway
                        # errors while looping through the variables when displaying the results.
                        if source not in enemyDamageTaken:
                            enemyDamageTaken[source] = 0
                # If Heal is in the event, then the player is healed for a certain amount. This number is plainly between
                # brackets: (35) for Hydro Spanner
                elif "Heal" in event:
                    # Turn it into an integer and add it to the total
                    damagestring = re.split(r"\((.*?)\)", damagestring)[1]
                    damagestring = damagestring.split(None, 1)[0]
                    healingReceived[currentMatch] += int(damagestring.replace('*', ''))
                # Selfdamage occurs when a player crashes into something, or self-destructs.
                elif "Selfdamage" in event:
                    damagestring = re.split(r"\((.*?)\)", damagestring)[1]
                    damagestring = damagestring.split(None, 1)[0]
                    selfdamage[currentMatch] += int(damagestring.replace('*', ''))

            # Up the index by one to get to the next match
            currentMatch += 1
            # Append the abilities-dictionary to the list of dictionaries
            abilitiesOccurrences.append(abilities)

            # Calculate the percentage of the hits that was a critical hit
            try:
                criticalPercentage = Decimal(float(criticals) / hits)
            # If hits = 0, then there is an error. If hits = 0, crits = 0 too.
            except ZeroDivisionError:
                criticalPercentage = 0

            # Round the critical percentage of to one decimal
            criticalPercentage = round(criticalPercentage * 100, 1)
            # Add both the absolute amount of criticals and the percentage to the list as a tuple
            criticalLuck.append((criticals, criticalPercentage))
            # Make the abilities-dictionary empty
            abilities = {}
            # Clear the criticals and the thits
            criticals, hits = 0, 0
            # Add the enemies list to the enemies matrix
            enemyMatrix.append(enemies)
            # And then clear the list of enemies
            enemies = []

            # The enemyDamageDealt and enemyDamageTaken dictionaries contain all the ID numbers of all the CombatLog,
            # instead of having them in separate dictionaries contained in a list. This is because the player ID
            # numbers are at least unique within a CombatLog.

        abilitiesOccurrencesMatrix.append(abilitiesOccurrences)
        damageDealtMatrix.append(damageDealt)
        damageTakenMatrix.append(damageTaken)
        selfdamageMatrix.append(selfdamage)
        healingReceivedMatrix.append(healingReceived)
        enemyCube.append(enemyMatrix)
        enemyDamageDealtList.append(enemyDamageDealt)
        enemyDamageTakenList.append(enemyDamageTaken)
        criticalLuckMatrix.append(criticalLuck)

        abilitiesOccurrences = []
        damageDealt = []
        damageTaken = []
        selfdamage = []
        healingReceived = []
        enemyMatrix = []
        enemyDamageDealt = {}
        enemyDamageTaken = {}
        criticalLuck = []

    # Matrix with [match][spawn]
    vars.damageDealt = damageDealtMatrix
    vars.damageTaken = damageTakenMatrix
    vars.healingReceived = healingReceivedMatrix
    vars.selfdamage = selfdamageMatrix
    vars.criticalLuck = criticalLuckMatrix
    # Lists of dictionaries with [match]['ID number']
    vars.enemyDamageDealt = enemyDamageDealtList
    vars.enemyDamageTaken = enemyDamageTakenList
    # Cube with [match][spawn][enemy]
    vars.enemyCube = enemyCube
    # Matrix of dictionaries with [match][spawn]['Ability']
    vars.abilities = abilitiesOccurrencesMatrix

    return

# Function to determine the ship of the player with a dictionary from the
# abilitiesOccurrencesMatrix from parseFile()
def determineShip(abilitiesDictionary):
    # These lists were made with the help of Yellowbird
    legionAbilities = ["Heavy Laser Cannon", "Laser Cannon", "Light Laser Cannon",
                       "Proton Torpedoe", "Concussion Missile", "Seeker Mine",
                       "Shield Power Converter", "Interdiction Drive",
                       "Railgun Sentry Drone", "Interdiction Sentry Drone", "Missile Sentry Drone",
                       "Shield Projector", "Repair Drone", "Overcharged Shield"]
    razorwireAbilities = ["Heavy Laser Cannon", "Laser Cannon", "Light Laser Cannon",
                          "Seismic Mine", "Proton Torpedoe", "Seeker Mine",
                          "Shield Power Converter", "Interdiction Drive", "Hyperspace Beacon",
                          "Interdiction Mine", "Concussion Mine", "Ion Mine",
                          "Charged Plating", "Overcharged Shield", "Shield Projector"]
    decimusAbilities = ["Heavy Laser Cannon", "Laser Cannon", "Light Laser Cannon", "Quad Laser Cannon",
                        "Cluster Missile", "Concussion Missile", "Proton Torpedoe"
                        "Shield Power Converter", "Power Dive", "Interdiction Drive",
                        "Ion Mine", "Concussion Mine", "Interdiction Sentry Drone"]
    jurgoranAbilities = ["Burst Laser Cannon", "Light Laser Cannon", "Laser Cannon",
                         "Cluster Missile", "Slug Railgun", "Interdiction Missile", "EMP Missile"
                         "Koiogran Turn", "Retro Thrusters", "Power Dive", "Interdiction Drive",
                         "Directional Shield", "Feedback Shield", "Distortion Field", "Fortress Shield"]
    dustmakerAbilities = ["Laser Cannon", "Heavy Laser Cannon",
                          "Proton Torpedoe", "Thermite Torpedoe", "Plasma Railgun", "Slug Railgun",
                          "Weapon Power Converter", "Rotational Thrusters", "Interdiction Drive", "Barrel Roll",
                          "Fortress Shield", "Directional Shield", "Feedback Shield"]
    manglerAbilities = ["Light Laser Cannon", "Burst Laser Cannon",
                        "Plasma Railgun", "Slug Railgun", "Ion Railgun",
                        "Rotational Thrusters", "Barrel Roll", "Interdiction Drive", "Weapon Power Converter",
                        "Feedback Shield", "Fortress Shield", "Distortion Field"]
    bloodmarkAbilities = ["Light Laser Cannon", "Laser Cannon", "Rapid-fire Laser Cannon",
                          "Ion Missile", "EMP Missile", "Thermite Torpedoe",
                          "Snap Turn", "Power Dive", "Interdiction Drive", "Koiogran Turn"
                          "Combat Command", "Tensor Field", "Sensor Beacon", "Targeting Telemetry",
                          "Shield Projector", "Repair Drone", "Distortion Field"]
    blackboltAbilities = ["Rapid-fire Laser Cannon", "Light Laser Cannon", "Laser Cannon",
                          "Rocket Pod", "Thermite Torpedoe", "Sabotage Probe",
                          "Power Dive", "Snap Turn", "Barrel Roll", "Koiogran Turn",
                          "Targeting Telemetry", "EMP Field", "Booster Recharge", "Sensor Beacon",
                          "Distortion Field", "Quick-charge Shield", "Engine Power Converter"]
    stingAbilities = ["Burst Laser Cannon", "Light Laser Cannon", "Quad Laser Cannon", "Rapid-fire Laser Cannon",
                      "Rocket Pod", "Cluster Missile", "Sabotage Probe"
                      "Koiogran Turn", "Retro Thrusters", "Power Dive", "Barrel Roll",
                      "Targeting Telemetry", "Blaster Overcharge", "Booster Recharge",
                      "Distortion Field", "Quick-charge Shield", "Directional Shield"]
    imperiumAbilities = ["Quad Laser Cannon", "Rapid-fire Laser Cannon", "Light Laser Cannon",
                         "Thermite Torpedoe", "EMP Missile", "Proton Torpedoe", "Ion Missile",
                         "Koiogran Turn", "Shield Power Converter", "Power Dive", "Interdiction Drive",
                         "Combat Command", "Remote Slicing", "Repair Probes",\
                         "Charged Plating", "Directional Shield", "Shield Projector"]
    rycerAbilities = ["Quad Laser Cannon", "Ion Cannon", "Rapid-fire Laser Cannon", "Heavy Laser Cannon",
                      "Concussion Missile", "Cluster Missile", "Proton Torpedoe",
                      "Weapon Power Converter", "Retro Thrusters", "Barrel Roll", "Koiogran Turn"
                      "Charged Plating", "Quick-charge Shield", "Directional Shield"]
    quellAbilities = ["Heavy Laser Cannon", "Quad Laser Cannon", "Light Laser Cannon",
                      "Cluster Missile", "Ion Missile", "Proton Torpedoe", "Concussion Missile", "EMP Missile",
                      "Weapon Power Converter", "Shield Power Converter", "Koiogran Turn", "Barrel Roll",
                      "Quick-charge Shield", "Directional Shield", "Charged Plating"]
    shipsList = ["Legion", "Razorwire", "Decimus",
                 "Mangler", "Dustmaker", "Jurgoran",
                 "Bloodmark", "Blackbolt", "Sting",
                 "Imperium", "Quell", "Rycer"]
    for key, value in abilitiesDictionary:
        if "Legion" in shipsList:
            if key not in legionAbilities:
                shipsList.remove("Legion")
        if "Razorwire" in shipsList:
            if key not in razorwireAbilities:
                shipsList.remove("Razorwire")
        if "Decimus" in shipsList:
            if key not in decimusAbilities:
                shipsList.remove("Decimus")
        if "Mangler" in shipsList:
            if key not in manglerAbilities:
                shipsList.remove("Mangler")
        if "Jurgoran" in shipsList:
            if key not in jurgoranAbilities:
                shipsList.remove("Jurgoran")
        if "Dustmaker" in shipsList:
            if key not in dustmakerAbilities:
                shipsList.remove("Dustmaker")
        if "Bloodmark" in shipsList:
            if key not in bloodmarkAbilities:
                shipsList.remove("Bloodmark")
        if "Blackbolt" in shipsList:
            if key not in blackboltAbilities:
                shipsList.remove("Blackbolt")
        if "Sting" in shipsList:
            if key not in stingAbilities:
                shipsList.remove("Sting")
        if "Imperium" in shipsList:
            if key not in imperiumAbilities:
                shipsList.remove("Imperium")
        if "Quell" in shipsList:
            if key not in quellAbilities:
                shipsList.remove("Quell")
        if "Rycer" in shipsList:
            if key not in rycerAbilities:
                shipsList.remove("Rycer")
    amountOfShips = 0
    shipFlown = None
    for ship in shipsList:
        shipFlown = ship
        amountOfShips += 1
    if amountOfShips != 1:
        return None
    else:
        return shipFlown

# Returns the player's ID numbers
def determinePlayer(lines):
    """
    Takes a list of strings (lines of a combat log) and extract all player engaged into battle. Save those in a
    dictionary with player ID as key and its occurrence as value.

    :param lines: lines of a combat log, as a list of string
    :return: dictionary of player ID and its occurrence
    """
    # Create dictionary to store the players in
    playerOccurrences = {}
    # Start a for loop to loop through the lines
    for action in lines:
        # Split the elements, just as in ReadFile()
        elements = re.split(r"[\[\]]", action)
        # Only source and target are important here
        source = elements[3]
        target = elements[5]
        # If the target is also the source, then it's a self-targeted ability
        if target == source:
            # Only if @ is not in the source it is a GSF ability
            if "@" not in source:
                # If the ID is not yet in the dictionary, add it and set the amount of occurrences to 1
                if source not in playerOccurrences:
                    playerOccurrences[source] = 1
                # If the ID is already in the dictionary, add 1 to the amount of occurrences for this ID
                else:
                    playerOccurrences[source] += 1
    # Return the playerOccurrences dictionary with the ID's and their respective occurrences
    return playerOccurrences

def determineDeaths(matches):
    playerIDs = []
    deaths = []
    for match in matches:
        for event in match:
            elements = re.split(r"[\[\]]", event)
            source = elements[3]
            target = elements[5]
            if target == source:
                if "@" not in source:
                    if source not in playerIDs:
                        playerIDs.append(source)
        tempDeaths = len(playerIDs) - 1
        playerIDs = []
        deaths.append(tempDeaths)
        tempDeaths = []
    return deaths

# Returns the player name
def determinePlayerName(lines):
    """
    Takes the first line of the combat log, which always contains the safe-login ability, which is a self-targeted
    ability. The 4th element of the line is the player name with the form: '@Name'. Return the name without '@'

    :param lines: List of strings, each elements are a line of the combat log
    :return: Player name, string
    """
    # In an unmodified file, lines[0] will always have this format
    elements = re.split(r"[\[\]]", lines[0])  # Split line
    return elements[3][1:]

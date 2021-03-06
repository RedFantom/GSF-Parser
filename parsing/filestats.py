"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
from parsing.parser import Parser


def file_statistics(file_name, sharing_db=None):
    """
    Puts the statistics found in a file_cube from
    Parser.split_combatlog() into a format that is usable by the
    FileFrame to display them to the user
    """
    lines = Parser.read_file(file_name)
    player_list = Parser.get_player_id_list(lines)
    file_cube, match_timings, spawn_timings = Parser.split_combatlog(lines, player_list)
    # Read sharing_db
    lines = Parser.read_file(file_name, sharing_db)
    name = Parser.get_player_name(lines)
    (abilities_dict, dmg_d, dmg_t, dmg_s, healing, hitcount, critcount,
     crit_luck, enemies, enemy_dmg_d, enemy_dmg_t, ships, uncounted) = \
        Parser.parse_file(file_cube, player_list)
    total = 0
    start = None
    for timing in match_timings:
        if start is not None:
            total += (timing - start).total_seconds()
            start = None
            continue
        start = timing
    minutes, seconds = divmod(total, 60)

    stat_string = "{name}\n{enemies} enemies\n{dmg_d}\n{dmg_t}\n{dmg_r:.1f} : 1.0\n" \
                  "{dmg_s}\n{healing}\n{hitcount}\n{critcount}\n{crit_luck:.2f}\n" \
                  "{deaths}\n{minutes}:{seconds:.0f}\n{dps:.1f}"
    stat_string = stat_string.format(
        name=name,
        enemies=len([enemy for enemy in enemies if enemy in enemy_dmg_t and enemy_dmg_t[enemy] > 0]),
        dmg_d=dmg_d,
        dmg_t=dmg_t,
        dmg_r=dmg_d / dmg_t if dmg_t != 0 else 0,
        dmg_s=dmg_s,
        healing=healing,
        hitcount=hitcount,
        critcount=critcount,
        crit_luck=critcount / hitcount if hitcount != 0 else 0,
        deaths=sum(len(match) for match in file_cube),
        minutes=minutes,
        seconds=seconds,
        dps=dmg_d / total,
    )
    return abilities_dict, stat_string, ships, enemies, enemy_dmg_d, enemy_dmg_t, uncounted

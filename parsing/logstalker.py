﻿"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
import variables
from parsing.parser import Parser
import os


class LogStalker(object):
    """
    LogStalker class that does *not* run in a Thread, but can instead
    be called upon in cycles to read from the log file and return the
    lines that are newly found in the most recent CombatLog. Not
    interchangeable with earlier implementations.
    """
    def __init__(self, folder=variables.settings["parsing"]["path"], watching_callback=None):
        """
        :param folder: Folder to watch CombatLogs in
        :param watching_callback: Callback to be called when the watched file changes
        """
        self._folder = folder
        self._watching_callback = watching_callback
        self.file = None
        self._read_so_far = 0

    def update_file(self):
        """
        Update the currently watched file to the newest file available.
        Does not change anything if the file is already the most recent
        available.
        """
        files = os.listdir(self._folder)
        if len(files) == 0:
            raise ValueError("No files found in this folder.")
        recent = sorted(files, key=Parser.parse_filename)[-1]
        if self.file is not None and recent == self.file:
            return
        self.file = recent
        self._read_so_far = 0
        self._watching_callback(self.file)

    def get_new_lines(self):
        """Read the new lines in the file and return them as a list"""
        self.update_file()
        with open(os.path.join(self._folder, self.file), "rb") as fi:
            lines = fi.readlines()[self._read_so_far:]
        self._read_so_far += len(lines)
        dictionaries = []
        for line in lines:
            try:
                line = line.decode()
            except UnicodeDecodeError:
                continue
            line = Parser.line_to_dictionary(line)
            if line is None:
                continue
            dictionaries.append(line)
        if None in dictionaries:
            raise ValueError()
        return dictionaries
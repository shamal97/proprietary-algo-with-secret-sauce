from pybaseball import playerid_lookup, statcast_pitcher
from datetime import datetime, date, timedelta

class Team:
    """Pulls probable starter info from espn.com

    It retuns the probably starts over a defined date range.

    :param state_date: Starting date range
    :type start_date: datetime.date
    :param end_date: Ending date range
    :type end_date: datetime.date
    """
    def __init__(self, name):
        self.name = name
        self.raw_cache = {}   # Raw cache.  The key is the date
        self.cache = None
        self.pitchers = set()
        self.batters = set()

    def __str__(self):
        return "Team: {}".format(self.name)

    def printRoster(self):
        for pitcher in self.pitchers:
            print(pitcher)
        for batter in self.batters:
            print(batter)

    def addPitcher(self, pitcher):
        self.pitchers.add(pitcher)

    def addBatter(self, batter):
        self.batters.add(batter)

    
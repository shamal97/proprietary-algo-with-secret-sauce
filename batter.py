from pybaseball import playerid_lookup, statcast_batter
from datetime import datetime, date, timedelta

STATS_START_DATE = '2023-03-30'

class Batter:
    """Pulls probable batter info from espn.com

    It takes in a name, calculates the batter score and sets
    the value on the Batter object

    :param batter_name: Name of batter we'll do the rest :)
    :value batter_name: str
    """
    def __init__(self, batter_name):
        self.last_name = batter_name.split(" ")[1]
        self.first_name = batter_name.split(" ")[0]
        self.name = batter_name
        self.raw_cache = {}   # Raw cache.  The key is the date
        self.cache = None
        self.score = 0
        self.set_name()
        self.set_pitcher_score()

    def __str__(self):
        return "Batter Name: {} Score: {}".format(self.name, self.score)

    def set_name(self):
        if self.first_name == 'Matthew':
            self.first_name = 'Matt'
        if self.first_name == 'Jose':
            self.first_name = 'José'
        if self.last_name == 'Urena':
            self.last_name = 'Ureña'
        if self.name == 'Martin Perez':
            self.first_name = 'Martín'
            self.last_name = 'Pérez'

    def set_stats(self):
        b_lookup = playerid_lookup(self.last_name, self.first_name)['key_mlbam']

        if len(b_lookup) == 0:
            b_lookup = playerid_lookup(self.last_name, self.first_name)['key_mlbam']

        if len(b_lookup) == 0:
            print('ERROR: Cannot find fangraphs data for ' + self.name)
            return 0
        b_stats = statcast_batter(STATS_START_DATE, str(date.today()), b_lookup)
        self.score = self.batter_score_hits(b_stats)
        return None
    
    # higher is better
    def batter_score_hits(self, b_stats):
        p_count = 0
        h_count = 0
        for pitch in b_stats.iterrows():
            pitch_event = pitch[1]['events']
            if pitch_event == 'home_run':
                h_count += 4
            elif pitch_event == 'triple':
                h_count += 3
            elif pitch_event == 'double':
                h_count += 2
            elif pitch_event == 'single':
                h_count += 1
            p_count += 1
        print("Pitcher: " + self.name + " P: " + str(p_count) + " H: " + str(h_count))
        if p_count == 0:
            return 999
        return (h_count / p_count) * 100
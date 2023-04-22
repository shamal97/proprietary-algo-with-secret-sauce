from pybaseball import playerid_lookup, statcast_pitcher
from datetime import datetime, date, timedelta

STATS_START_DATE = '2023-03-30'

class Pitcher:
    """Pulls probable starter info from espn.com

    It takes in a name, calculates the pitcher score and sets
    the value on the Pitcher object

    :param pitcher_name: Name of pitcher we'll do the rest :)
    :value pitcher_name: str
    """
    def __init__(self, pitcher_name):
        self.last_name = pitcher_name.split(" ")[1]
        self.first_name = pitcher_name.split(" ")[0]
        self.name = pitcher_name
        self.raw_cache = {}   # Raw cache.  The key is the date
        self.cache = None
        self.score = 0
        self.set_name()
        self.set_pitcher_score()

    def __str__(self):
        return "Pitcher Name: {} Score: {}".format(self.name, self.score)

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

    def set_pitcher_score(self):
        p_lookup = playerid_lookup(self.last_name, self.first_name)['key_mlbam']

        if len(p_lookup) == 0:
            p_lookup = playerid_lookup(self.last_name, self.first_name)['key_mlbam']

        if len(p_lookup) == 0:
            print('ERROR: Cannot find fangraphs data for ' + self.name)
            return 0
        
        p_lookup = p_lookup[0]

        p_stats = statcast_pitcher(STATS_START_DATE, str(date.today()), p_lookup)

        self.score = self.pitcher_score_hits(p_stats)
        return

        # lower is better
    def pitcher_score_hits(self, p_stats):
        p_count = 0
        h_count = 0
        for pitch in p_stats.iterrows():
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

    def get_pitcher_score(self):
        return self.score
    
    def get_pitcher_score_value(self, opp_pitcher_score):
        if self.score == 0:
            return 99
        return  opp_pitcher_score / self.score
import requests
from datetime import timedelta
import pandas as pd
from bs4 import BeautifulSoup

class ProbableLineupScraper:
    """Pulls probable lineup info from espn.com

    It retuns the probably lineup for the current day; anything
    in the future seems to not be filled out

    lineups seem to be set an hour to 3 hours before the start of the game;
    may be longer or shorter

    :param state_date: Starting date range
    :type start_date: datetime.date
    :param end_date: Ending date range
    :type end_date: datetime.date
    """

    def __init__(self, date):
        self.start_date = date
        self.url = self.set_url()
        print(self.url)

    def set_url(self):
        dt_fmt = date.strftime("%Y%m%d")
        return "https://www.mlb.com/starting-lineups/{}".format(dt_fmt)


class ProbableStartersScraper:
    """Pulls probable starter info from espn.com

    It retuns the probably starts over a defined date range.

    :param state_date: Starting date range
    :type start_date: datetime.date
    :param end_date: Ending date range
    :type end_date: datetime.date
    """
    def __init__(self, start_date, end_date):
        if start_date > end_date:
            raise ValueError("Start date must be before or equal to end date")
        self.start_date = start_date
        self.end_date = end_date
        self.raw_cache = {}   # Raw cache.  The key is the date
        self.cache = None

    def __getstate__(self):
        return (self.start_date, self.end_date, self.cache)

    def __setstate__(self, state):
        (self.start_date, self.end_date, self.cache) = state
        self.raw_cache = {}

    def scrape(self):
        """Scrape the site and return a DataFrame of the results

        :return: DataFrame listing every starting pitcher.  It leaves out any
        undecided starter.
        :rtype: pandas.DataFrame
        """
        self._cache_source()
        return self.cache

    def save_raw_cache(self, day, fn):
        uri = self._get_uri(day)
        s = requests.get(uri).content
        with open(fn, "wb") as f:
            f.write(s)

    def set_source(self, day, f):
        assert(day not in self.raw_cache)
        self.raw_cache[day] = f

    def _get_uri(self, day):
        dt_fmt = day.strftime("%Y%m%d")
        return "https://www.espn.com/mlb/schedule/_/date/{}".format(dt_fmt)

    def _cache_source(self):
        if self.cache is None:
            cur_date = self.start_date
            res = pd.DataFrame()
            while cur_date <= self.end_date:
                self._cache_raw_source(cur_date)
                # res = res.append(self._parse_day(cur_date))
                res = pd.concat([res, self._parse_day(cur_date)])
                cur_date = cur_date + timedelta(1)
            res = res.reset_index()
            res = res.drop(['index'], axis=1)
            self.cache = res

    def _cache_raw_source(self, day):
        if day not in self.raw_cache:
            s = requests.get(self._get_uri(day)).content
            self.raw_cache[day] = BeautifulSoup(s, "lxml")

    def _parse_day(self, day):
        table = self._get_table(day)
        headings = [th.get_text() for th in table.find("tr").find_all("th")]
        if 'pitching matchup' in headings:
            p_matchup_inx = headings.index('pitching matchup')
            p_matchup_inx +=1
        else:
            p_matchup_inx = None
        away_matchup_inx = headings.index('MATCHUP')
        home_matchup_inx = away_matchup_inx + 1
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        df = pd.DataFrame()
        for row in rows:
            cols = row.find_all('td')
            if p_matchup_inx is not None:
                p_matchup_txt = cols[p_matchup_inx].text
                p_anchors = cols[p_matchup_inx].find_all('a')
            home_anchors = cols[home_matchup_inx].find_all('a')
            away_anchors = cols[away_matchup_inx].find_all('a')
            if p_matchup_inx is None:
                pass
            elif p_matchup_txt.find("Undecided") != -1:
                if p_matchup_txt.find("Undecided vs") != -1:
                    df = pd.concat([df, self._produce_df_row(day, p_anchors[0],
                                                        away_anchors, home_anchors)])
                    # df = df.append(self._produce_df_row(day, p_anchors[0],
                                                        # away_anchors))
                else:
                    df = pd.concat([df, self._produce_df_row(day, p_anchors[0],
                                                        home_anchors, away_anchors)])
                    # df = df.append(self._produce_df_row(day, p_anchors[0],
                                                        # home_anchors))
            elif len(p_anchors) == 2:
                df = pd.concat([df, self._produce_df_row(day, p_anchors[0],
                                                    home_anchors, away_anchors)])
                # df = df.append(self._produce_df_row(day, p_anchors[0],
                                                    # home_anchors))
                df = pd.concat([df, self._produce_df_row(day, p_anchors[1],
                                                    away_anchors, home_anchors)])
                # df = df.append(self._produce_df_row(day, p_anchors[1],
                                                    # away_anchors))
        return df
    
    def determine_city_team(self, t_anchor_text, city):
        # find which team it is if there are multiple teams per city
        if city == "Chicago":
            if "-white-sox" in t_anchor_text:
                return "Chicago White Sox"
            elif "-cubs" in t_anchor_text:
                return "Chicago Cubs"
        if city == "New York":
            if "-yankees" in t_anchor_text:
                return "New York Yankees"
            if "-mets" in t_anchor_text:
                return "New York Mets"
        if city == "Los Angeles":
            if "-angels":
                return "Los Angeles Angles"
            elif "-dodgers":
                return "Los Angeles Dodgers"

    def _produce_df_row(self, day, p_anchor, t_anchor, mt_anchor):
        opponent = t_anchor[1].text
        team = mt_anchor[1].text
        print(t_anchor[1].text)
        print(mt_anchor)
        print(t_anchor)
        for a in t_anchor:
            print('scott')
            print(a)
            for abbr in a.find_all('tr'):
                #opponent = abbr.text
                print(abbr.text)
        player_name = p_anchor.text
        link = p_anchor['href']
        id_loc = link.find("/id/")
        if id_loc == -1:
            print("ERROR NONONONONON")
            raise ValueError("Could not extract espn ID from link: " + link)
        espn_id = int(link[id_loc+4:])
        print("here jake")
        print(day, player_name, espn_id, team, opponent)
        return pd.DataFrame(data=[[day, player_name, espn_id, team, opponent]],
                            columns=["Date", "Name", "espn_id", "team", "opponent"])

    def _get_table(self, day):
        try:
            return self.raw_cache[day].find_all('table')[0]
        except IndexError:
            raise ValueError("Pitcher probables cannot be retrieved for " +
                             "this day ({}).".format(day))

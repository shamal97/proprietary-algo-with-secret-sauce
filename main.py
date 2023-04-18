from pybaseball import playerid_lookup, statcast_pitcher
from pysbr import *
from datetime import datetime, date, timedelta
from espn import ProbableStartersScraper

def get_participant_ids(e):
    ret = {}
    for event in e.list():
        ret[event['participants'][0].get('source').get('name')] = event['participants'][0].get('participant id')
        ret[event['participants'][1].get('source').get('name')] = event['participants'][1].get('participant id')
    return ret

def pitcher_score_hits(p_stats, name):
    p_count = 0
    h_count = 0
    for pitch in p_stats.iterrows():
        if pitch[1]['events'] in ['home_run', 'triple', 'double', 'single']:
            h_count += 1
        p_count += 1
    print("Pitcher: " + name + " P: " + str(p_count) + " H: " + str(h_count))
    return (h_count / p_count) * 100

def get_pitcher_score(pitcher_name):
    last = pitcher_name.split(" ")[1]
    first = pitcher_name.split(" ")[0]
    p_lookup = playerid_lookup(last, first)['key_mlbam'][0]
    p_stats = statcast_pitcher('2023-03-30', str(date.today()), p_lookup)

    return pitcher_score_hits(p_stats, pitcher_name)

def main():
    es = ProbableStartersScraper(date.today(), date.today())
    df = es.scrape()

    mlb = MLB()
    sb = Sportsbook()
    dt = datetime.strptime(str(date.today()), '%Y-%m-%d')
    e = EventsByDate(mlb.league_id, dt)
    cl = CurrentLines(e.ids(), mlb.market_ids(['moneyline']), sb.ids(['bovada']))

    odds_col = []
    pitcher_score_col = []
    batters_score_col = []
    value = []
    p_ids = get_participant_ids(e)
    #["Date", "Name", "espn_id", "team", "opponent"]
    for i in df.iterrows():
        team = i[1]['team']
        odds = 0
        # TODO handle chicago, ny, la multiple teams per city
        if team not in ['Los Angeles', 'Chicago', 'New York']:
            participant_id = p_ids.get(team)
            for odds_data in cl.list():
                if odds_data.get('participant id') == participant_id:
                    odds = odds_data.get('decimal odds')
        
        odds_col.append(odds)

        pitcher_score_col.append(get_pitcher_score(i[1]["Name"]))
    
    df['odds'] = odds_col
    df['p_score'] = pitcher_score_col

    print(df)

if __name__ == "__main__":
    main()
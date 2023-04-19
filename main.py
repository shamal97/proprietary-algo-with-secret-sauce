from pybaseball import playerid_lookup, statcast_pitcher
from pysbr import *
from datetime import datetime, date, timedelta
from espn import ProbableStartersScraper
# from pitcher import 

def get_participant_ids(e):
    ret = {}
    for event in e.list():
        ret[event['participants'][0].get('source').get('name')] = event['participants'][0].get('participant id')
        ret[event['participants'][1].get('source').get('name')] = event['participants'][1].get('participant id')
    return ret

# lower is better
def pitcher_score_hits(p_stats, name):
    p_count = 0
    h_count = 0
    for pitch in p_stats.iterrows():
        if pitch[1]['events'] in ['home_run', 'triple', 'double', 'single']:
            h_count += 1
        p_count += 1
    print("Pitcher: " + name + " P: " + str(p_count) + " H: " + str(h_count))
    if p_count == 0:
        return 999
    return (h_count / p_count) * 100

def get_pitcher_score(pitcher_name):
    last = pitcher_name.split(" ")[1]
    first = pitcher_name.split(" ")[0]
    print(pitcher_name)
    p_lookup = playerid_lookup(last, first)['key_mlbam']
    if len(p_lookup) == 0:
        if first == 'Matthew':
            first = 'Matt'
        if first == 'Jose':
            first = 'José'
        if last == 'Urena':
            last = 'Ureña'
        if pitcher_name == 'Martin Perez':
            first = 'Martín'
            last = 'Pérez'
        p_lookup = playerid_lookup(last, first)['key_mlbam']

    if len(p_lookup) == 0:
        print('ERROR: Cannot find fangraphs data for ' + pitcher_name)
        return 0
    
    p_lookup = p_lookup[0]

    p_stats = statcast_pitcher('2023-03-30', str(date.today()), p_lookup)

    return pitcher_score_hits(p_stats, pitcher_name)

def get_pitcher_score_value(pitcher_score, opp_pitcher_score):
    if pitcher_score == 0:
        return 99
    return  opp_pitcher_score / pitcher_score

def is_it_a_bet(p_score_value, odds):
    if p_score_value > 1 and odds > 2:
        return "YES"
    return "NO"

def value_with_odds(p_score_value, odds):
    return p_score_value * odds

def main():
    # es = ProbableStartersScraper(date.today() + timedelta(1), date.today() + timedelta(1))
    es = ProbableStartersScraper(date.today(), date.today())

    df = es.scrape()

    mlb = MLB()
    sb = Sportsbook()
    dt = datetime.strptime(str(date.today() + timedelta(1)), '%Y-%m-%d')
    e = EventsByDate(mlb.league_id, dt)
    cl = CurrentLines(e.ids(), mlb.market_ids(['moneyline']), sb.ids(['bovada']))

    odds_col = []
    pitcher_score_col = []
    pitcher_score_value_col = []
    batters_score_col = []
    value = []
    is_bet = []
    value_with_odds_col = []
    pitcher_scores = {}
    p_ids = get_participant_ids(e)
    print(cl.list())
    #["Date", "Name", "espn_id", "team", "opponent"]
    for i in df.iterrows():
        team = i[1]['team']
        odds = 0
        # TODO handle chicago, ny, la multiple teams per city
        if team not in ['Los Angeles', 'Chicago', 'New York']:
            participant_id = p_ids.get(team)
            print('partip id:')
            print(participant_id)
            for odds_data in cl.list():
                if odds_data.get('participant id') == participant_id:
                    odds = odds_data.get('decimal odds')
        
        odds_col.append(odds)
        pitcher_score = get_pitcher_score(i[1]["Name"])

        pitcher_scores[team] = pitcher_score

        pitcher_score_col.append(pitcher_score)
    
    df['odds'] = odds_col
    df['p_score'] = pitcher_score_col

    for i in df.iterrows():
        p_score_value = get_pitcher_score_value(i[1]['p_score'], pitcher_scores[i[1]['opponent']])
        pitcher_score_value_col.append(p_score_value)
        do_i_bet = is_it_a_bet(p_score_value, i[1]['odds'])
        value_with_odds_col.append(value_with_odds(p_score_value, i[1]['odds']))
        is_bet.append(do_i_bet)

    df['pitcher_score_value'] = pitcher_score_value_col
    df['is_bet'] = is_bet
    df['value_w_odds'] = value_with_odds_col

    print(df)

if __name__ == "__main__":
    main()
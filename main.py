from pybaseball import playerid_lookup, statcast_pitcher
from pysbr import *
from datetime import datetime, date, timedelta
from espn import ProbableStartersScraper
from pitcher import Pitcher


def get_participant_ids(e):
    ret = {}
    for event in e.list():
        ret[event['participants'][0].get('source').get('name')] = event['participants'][0].get('participant id')
        ret[event['participants'][1].get('source').get('name')] = event['participants'][1].get('participant id')
    return ret

def is_it_a_bet(p_score_value, odds):
    if p_score_value > 1 and odds > 2:
        return "YES"
    return "NO"

def value_with_odds(p_score_value, odds):
    return p_score_value * odds

def main():
    es = ProbableStartersScraper(date.today() + timedelta(1), date.today() + timedelta(1))
    #es = ProbableStartersScraper(date.today(), date.today())

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
    team_pitchers = dict()
    p_ids = get_participant_ids(e)
    print(cl.list())
    #["Date", "Name", "espn_id", "team", "opponent"]
    for dfRow in df.iterrows():
        teamName = dfRow[1]['team']
        odds = 0
        # TODO handle chicago, ny, la multiple teams per city
        if teamName not in ['Los Angeles', 'Chicago', 'New York']:
            participant_id = p_ids.get(teamName)
            print('partip id:')
            print(participant_id)
            for odds_data in cl.list():
                if odds_data.get('participant id') == participant_id:
                    odds = odds_data.get('decimal odds')
        
        odds_col.append(odds)
        team_pitcher = Pitcher(dfRow[1]["Name"])
        team_pitchers[teamName] = team_pitcher
        pitcher_score_col.append(team_pitcher.get_pitcher_score())
    
    df['odds'] = odds_col
    df['p_score'] = pitcher_score_col

    for dfRow in df.iterrows():
        teamName, oppName = dfRow[1]['team'], dfRow[1]['opponent']
        pitcher = team_pitchers[teamName]
        opp_pitcher = team_pitchers[oppName]
        print("Pitchers looking at: \n", pitcher, opp_pitcher)

        p_score_value = pitcher.get_pitcher_score_value(opp_pitcher.get_pitcher_score())
        #p_score_value = get_pitcher_score_value(dfRow[1]['p_score'], pitcher_scores[dfRow[1]['opponent']])
        pitcher_score_value_col.append(p_score_value)
        do_i_bet = is_it_a_bet(p_score_value, dfRow[1]['odds'])
        value_with_odds_col.append(value_with_odds(p_score_value, dfRow[1]['odds']))
        is_bet.append(do_i_bet)

    df['pitcher_score_value'] = pitcher_score_value_col
    df['is_bet'] = is_bet
    df['value_w_odds'] = value_with_odds_col

    print(df)

if __name__ == "__main__":
    main()
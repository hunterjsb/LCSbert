import json
from datetime import datetime
from requests import get

# constants
main_slugs = {'LCS': 'league-of-legends-lcs', 'LEC': 'league-of-legends-lec'}
LEC_ID = 4197
LCS_START = datetime(2021, 2, 5)
with open(f'./secrets.json', 'r') as f:
    PANDASCORE_TOKEN = json.load(f)['PANDASCORE_TOKEN']

# GET NA WEEK - DECLARE END OF WEEKS AS wX_e
now = datetime.now()
w3_e = datetime(2021, 2, 22)
w4_e = datetime(2021, 3, 1)
w5_e = datetime(2021, 3, 8)
w6_e = datetime(2021, 3, 15)
if now <= w3_e:
    lcs_week = 'Week 3'
elif now <= w4_e:
    lcs_week = 'Week 4'
elif now <= w5_e:
    lcs_week = 'Week 5'
elif now <= w6_e:
    lcs_week = 'Week 6'


class LoLSeries:
    SEASON = 'spring-2021'

    def __init__(self, region: str):
        self.region = region
        self.slug = main_slugs[region]

    def load_running_series(self):
        """for getting local data about a current LoL series (id, slug, etc...)
        :returns dict"""
        # OPEN THE LOCAL FILE
        with open('./assets/runningseries.json', 'r') as f:
            all_series = json.load(f)

        # RETURN CORRESPONDING ENTRY
        for series in all_series:
            if series['slug'] == self.slug + '-' + LoLSeries.SEASON:
                return series

    def load_team_by(self, key, value):
        """for loading local data about a regional team
        :returns dict"""
        # OPEN THE LOCAL FILE
        with open(f'./assets/teams_{self.region}.json', 'r') as f:
            all_teams = json.load(f)

        # RETURN CORRESPONDING ENTRY
        for c_team in all_teams:
            if c_team[key] == value:
                return c_team

    def get_matches(self, direction: str, w=lcs_week):
        """ get next week's matches, returns a list of 15 strings formatted ' T1 vs T2'
         :returns list"""
        # OPEN THE LOCAL FILE
        with open(f"./assets/{direction}_{self.region}.json", 'r') as f:
            all_matches = json.load(f)

        # RETURN CORRESPONDING ENTRIES
        this_week = []
        for match in all_matches:
            week, name = match['name'].split(':')
            if week == w:
                name = name[1:]
                this_week.append(name)
        return this_week

    def get_winner_of_match(self, week: str, match_name: str):
        # OPEN THE LOCAL FILE
        with open(f"./assets/past_{self.region}.json", 'r') as f:
            all_matches = json.load(f)

        # MAKE THE INDEXING STRING
        s = week + ': ' + match_name
        winner = None

        # GET THE CORRESPONDING WINNER
        for match in all_matches:
            if match['name'] == s:
                results1, results2 = match['results'][0], match['results'][1]
                if results1['score']:
                    winner = self.load_team_by('id', results1['team_id'])
                elif results2['score']:
                    winner = self.load_team_by('id', results2['team_id'])

        return winner['acronym']


class LCS(LoLSeries):
    """The North American League Championship Series"""
    ID = 4198

    def __init__(self):
        super().__init__('LCS')

    @staticmethod
    def download_past_lcs():
        resp = get(f'https://api.pandascore.co/lol/matches/past?token={PANDASCORE_TOKEN}'
                   f'&filter[league_id]={LCS.ID}').json()
        with open(f'./assets/past_LCS.json', 'w') as f1:
            json.dump(resp, f1, indent=4)

    def predict(self, predictions: list or tuple, author_id: str):
        """takes in list of strings as 2 or 3 letter team abbreviations & a discord author id as a str
        then saves the predictions as json in ./assets
        :returns error msg or dict"""
        # DATA VALIDATION
        if len(predictions) != 15:  # 15 GPW
            return '`ERROR:` `Invalid prediction size`'
        else:
            for i, match in enumerate(self.get_matches('upcoming')):
                t1, t2 = match.split(' vs ')
                if predictions[i].upper() not in [t1, t2]:
                    return f'`ERROR` `Bad prediction` {lcs_week} game {i+1}:{match}'

        # SAVE PREDICTIONS
        with open('./assets/predictions.json', 'r') as f:
            all_predictions = json.load(f)
        if author_id not in all_predictions.keys():
            all_predictions[author_id] = {lcs_week: predictions}
        else:
            all_predictions[author_id][lcs_week] = predictions
        with open('./assets/predictions.json', 'w') as f:
            json.dump(all_predictions, f, indent=4)
        return all_predictions

    @staticmethod
    def get_predictions(author_id: str):
        """return a user's predictions... this is static :>
        :returns dict"""
        with open('./assets/predictions.json', 'r') as f:
            raw = json.load(f)

        # LOOK FOR THE PREDICTIONS
        if author_id in raw:
            player_predictions = raw[author_id]
            return player_predictions
        else:
            return '`ERROR:` `NO USER`'

    def get_record(self, author_id: str):
        """ returns a dict of user predictions and stats
        :returns [{'Week n': {'game': 't1 vs t2', 'winner': 'tn', 'correct': bool}}, {'Week n+1...}, ...]"""

        # RETRIEVE PREDICTIONS
        user_predictions = LCS.get_predictions(author_id)
        ret = {}  # dict of arrays of 1's & 0's to return. 1's meaning a correct prediction. idx by week.

        # CHECK AGAINST THE DUBS
        for week in user_predictions:
            ret_inner = []
            if int(week[-1]) < int(lcs_week[-1]):

                # GET USER PREDICTIONS AND ACTUAL RECORD
                game_preds = user_predictions[week]
                fri, sat, sun = game_preds[0:5], game_preds[5:10], game_preds[10:15]
                outcomes = self.get_matches('past', week)
                outcomes_fi, outcomes_sat, outcomes_sun = outcomes[0:5], outcomes[5:10], outcomes[10:15]

                # COUNT WINS PER DAY AND ADD THE LIST TO THE RET DICT
                for day, matches in zip([fri, sat, sun], [outcomes_fi, outcomes_sat, outcomes_sun]):
                    for game in matches:
                        winner = self.get_winner_of_match(week, game)
                        oc = 1 if (winner.lower() in day) or (winner.upper() in day) else 0
                        ret_inner.append((game, winner, oc))
                ret[week] = ret_inner
        return ret


if __name__ == "__main__":
    lee = LCS()
    print(lee.get_record("809520615089635389"))

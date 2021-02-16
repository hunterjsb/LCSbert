from requests import get
import json
from datetime import datetime

# constants
with open('./secrets.json') as s:
    PANDASCORE_TOKEN = json.load(s)['PANDASCORE_TOKEN']
main_slugs = {'LCS': 'league-of-legends-lcs', 'LEC': 'league-of-legends-lec'}
LCS_ID = 4198
LEC_ID = 4197

# GET NA WEEK - DECLARE END OF WEEKS AS wX_e
now = datetime.now()
w3_e = datetime(2021, 2, 21)
w4_e = datetime(2021, 2, 28)
w5_e = datetime(2021, 3, 7)
w6_e = datetime(2021, 3, 14)
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
        """for getting local data about a current LoL series (id, slug, etc...)"""
        # OPEN THE LOCAL FILE
        with open('./assets/runningseries.json', 'r') as f:
            all_series = json.load(f)

        # RETURN CORRESPONDING ENTRY
        for series in all_series:
            if series['slug'] == self.slug + '-' + LoLSeries.SEASON:
                return series

    def load_team(self, team: str):
        """for loading local data about a regional team"""
        # OPEN THE LOCAL FILE
        with open(f'./assets/teams_{self.region}.json', 'r') as f:
            all_teams = json.load(f)

        # RETURN CORRESPONDING ENTRY
        for c_team in all_teams:
            if c_team['acronym'] == team:
                return c_team

    def next_week_matches(self):
        """ get next week's matches, returns a list of 15 strings formatted ' T1 vs T2' """
        # OPEN THE LOCAL FILE
        with open(f"./assets/upcoming_{self.region}.json", 'r') as f:
            all_matches = json.load(f)

        # RETURN CORRESPONDING ENTRIES
        this_week = []
        for match in all_matches:
            week, name = match['name'].split(':')
            if week == lcs_week:
                this_week.append(name)
        return this_week


class LCS(LoLSeries):
    """The North American League Championship Series"""
    def __init__(self):
        super().__init__('LCS')
        self.t = 0  # to call in static method and remove a PEP8 lol

    def predict(self, predictions: list or tuple, author_id: str):
        """takes in list of strings as 2 or 3 letter team abbreviations & a discord author id as a str
        then saves the predictions as json in ./assets"""
        # DATA VALIDATION
        if len(predictions) != 15:  # 15 GPW
            return '`ERROR:` `Invalid prediction size`'
        else:
            for i, match in enumerate(self.next_week_matches()):
                t1, t2 = match.split(' vs ')
                t1 = t1[1:]  # remove leading zero
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

    def get_predictions(self, author_id: str):
        """return a user's predictions... this is static :>"""
        try:
            with open('./assets/predictions.json', 'r') as f:
                player_predictions = json.load(f)[author_id]
            return player_predictions
        except KeyError:
            self.t += 1  # PEP8 staticmethod
            return '`ERROR:` `NO PREDICTIONS`'


if __name__ == "__main__":
    w3_LCS = LCS()
    print(w3_LCS.predict(['C9', 'DIG', 'GG', 'TSM', '100', 'C9', 'IMT', '100', 'TL', 'GG', 'TSM', 'IMT', 'GG', 'C9',
                          'EG'], 'admin'))

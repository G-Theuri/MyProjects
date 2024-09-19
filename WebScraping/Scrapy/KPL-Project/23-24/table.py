from curl_cffi import requests as cureq
import pandas as pd
import time
import json
import os

seasonIDs = {7752:"2014", 9841:"2015", 11265:"2016", 12921:"2017", 15858:"2018", 19876:"2018/2019", 24023:"2019/2020",
             34876:"2020/2021", 38844:"2021/2022", 45686:"2022/2023", 53922:"2023/2024", 65071:"2024/2025"}
#response = cureq.get("https://www.sofascore.com/api/v1/unique-tournament/1644/season/19876/rounds", impersonate="chrome")
for key in seasonIDs:
    print("Season", seasonIDs[key])

class matches:
    def __init__(self, seasonIDs, round):
        self.seasonIDs=seasonIDs
        self.rounds = round
        self.by_rounds()
        self.by_date()

    def by_rounds(self, seasonID, seasonIDs):
        os.makedirs(f'Season-{seasonIDs[seasonID]}', exist_ok=True)
        def extract():
            response = cureq.get("f'https://www.sofascore.com/api/v1/unique-tournament/1644/season/{seasonID}/events/round/{round}'",
                                  impersonate="chrome")
            return response
        def transform(response):
            round_data = []
            games = json.loads(response.text)
            for game in games["events"]:
                matchdata = {
                "tournament" : game["tournament"]["uniqueTournament"]["name"],
                "season" : game["season"]["year"],
                "round" : game["roundInfo"]["round"],
                "matchID" : game["id"],
                "matchCustomID" : game["customId"],
                "matchStatus" : game["status"]["description"], # Ended, Postponed, Not started
                "homeTeamnName" :game["homeTeam"]["name"],
                "homeTeamnNameCode":game["homeTeam"]["nameCode"],
                'homeTeamID' : game["homeTeam"]["id"],
                "awayTeamName": game["awayTeam"]["name"],
                'awayTeamNameCode': game["awayTeam"]["nameCode"],
                'awayTeamID' : game["awayTeam"]["id"],
                }
    
            if matchdata["matchStatus"]== "Ended":
                matchScores = {
                    'homeScoreHT' : game["homeScore"]["period1"],
                    'awayScoreHT' : game["awayScore"]["period1"],
                    'homeScoreFT' : game["homeScore"]["normaltime"],
                    'awayScoreFT' : game["awayScore"]["normaltime"]
                },
            else:
                matchScores = {
                    'homeScoreHT' : "-",
                    'awayScoreHT' : "-",
                    'homeScoreFT' : "-",
                    'awayScoreFT' : "-"
                }
            round_data.append(matchdata)
            return round_data       

        def load(round_data, seasonID, seasonIDs):
            df = pd.DataFrame(round_data)
            df.to_csv(f'Season-{seasonIDs[seasonID]}/round-{df["round"][1]}.csv')

    def by_date(self):
        pass
    
class standings:
    def table(self):
        pass
#use a for loop on these classes to link extracted data from both classes into a single folder
#try and use extract>>transform>>load in the functions

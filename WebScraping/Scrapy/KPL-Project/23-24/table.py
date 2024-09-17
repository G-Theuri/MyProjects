from curl_cffi import requests as cureq
import pandas as pd
import time
import json

seasonIDs = {7752:"2014", 9841:"2015", 11265:"2016", 12921:"2017", 15858:"2018", 19876:"2018/2019", 24023:"2019/2020",
             34876:"2020/2021", 38844:"2021/2022", 45686:"2022/2023", 53922:"2023/2024", 65071:"2024/2025"}
#response = cureq.get("https://www.sofascore.com/api/v1/unique-tournament/1644/season/19876/rounds", impersonate="chrome")
for key in seasonIDs:
    print("Season", seasonIDs[key])

class matches:
    def __init__(self, seasonID, round):
        self.seasonID=seasonID
        self.rounds = round
        self.by_rounds()
        self.by_date()

    def by_rounds(self):
        def extract():
            response = cureq.get("f'https://www.sofascore.com/api/v1/unique-tournament/1644/season/{seasonID}/events/round/{round}'",
                                  impersonate="chrome")
            return response
        def transform(response):
            games = json.loads(response.text)
            for game in games["events"]:
                tournament = game["tournament"]["uniqueTournament"]["name"]
                season = game["season"]["year"]
                round = game["roundInfo"]["round"]
                matchID = game["id"]
                matchCustomID = game["customId"]
                matchStatus = game["status"]["description"]
                homeTeam = {game["homeTeam"]["name"]: game["homeTeam"]["nameCode"]}
                homeScoreHT = game["homeScore"]
                awayScoreHT = game["homeTeam"]
                homeScoreFT = game["homeTeam"]
                awayScoreFT = game["homeTeam"]


            
        def load():
            pass
        pass
    def by_date(self):
        pass
    
class standings:
    def table(self):
        pass
#use a for loop on these classes to link extracted data from both classes into a single folder
#try and use extract>>transform>>load in the functions

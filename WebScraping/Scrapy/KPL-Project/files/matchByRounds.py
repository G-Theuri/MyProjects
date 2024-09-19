from curl_cffi import requests as cureq
import pandas as pd
import time
import json
import os


print(os.listdir('C:/MyProjects/WebScraping/Scrapy/KPL-Project/data/bySeasons'))
seasonIDs = [7752]

class rounds:

    def __init__(self, seasonID):
        self.seasonID=seasonID        
        response= self.extract()
        data = self.transform(response)
        self.load(data)

    def extract(self):
        response = cureq.get(f"https://www.sofascore.com/api/v1/unique-tournament/1644/season/{seasonID}/events/round/1",
                                 impersonate="chrome")
        return response
    def transform(self, response):
        alldata = []
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
                    'homeScoreFT' : game["homeScore"]["normaltime"],
                    'awayScoreFT' : game["awayScore"]["normaltime"]
                }
            else:
                matchScores = {
                    'homeScoreFT' : "-",
                    'awayScoreFT' : "-"
                }
            alldata.append(matchdata | matchScores)
        return alldata
    
    def load(self, alldata):
        df = pd.DataFrame(alldata)
        df.to_csv("ssn2014round1.csv", index=False)

for seasonID in seasonIDs:
    roundsData = rounds(seasonID)


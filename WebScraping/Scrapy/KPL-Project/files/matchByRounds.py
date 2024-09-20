from curl_cffi import requests as cureq
import pandas as pd
import time
import json
import os


directories = os.listdir('C:/MyProjects/WebScraping/Scrapy/KPL-Project/data/bySeasons')
seasonIDs = {7752:"2014",9841:"2015",11265:"2016", 12921:"2017",}

class rounds:

    def __init__(self, seasonID, directory):
        self.seasonID=seasonID
        self.directory = directory        
        response= self.extract()
        data = self.transform(response)
        self.load(data, directory)

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
    
    def load(self, alldata, directory):
        folders = os.listdir('C:/MyProjects/WebScraping/Scrapy/KPL-Project/data/bySeasons')
        path = 'C:/MyProjects/WebScraping/Scrapy/KPL-Project/data/bySeasons'
        df = pd.DataFrame(alldata)
        number = df['round'][1]

        filepath = f"{path}/{directory}/round{number}.csv"
        file_exists = True if os.path.isfile(filepath) else False

        if directory in folders:
            if file_exists is False:
                df.to_csv(f"{filepath}", index=False)
                print(f"Filename: ({directory}/round{number}) added!")
            else:
                print(f"Filename: ({directory}/round{number}) already exists!")
        else:
            print(f"Error: directory not found")

for seasonID in seasonIDs:
    directory = seasonIDs[seasonID]
    roundsData = rounds(seasonID, directory)


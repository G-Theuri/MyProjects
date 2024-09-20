from curl_cffi import requests as cureq
import pandas as pd
import time
import json
import os


directories = os.listdir('C:/MyProjects/WebScraping/Scrapy/KPL-Project/data/bySeasons')
seasonIDs = {7752:"2014",}

class rounds:

    def __init__(self, seasonID, directory, round):
        self.seasonID=seasonID
        self.directory = directory
        self.round = round        
        response= self.extract(round)
        data = self.transform(response)
        self.load(data, directory)

    def extract(self, round):
        response = cureq.get(f"https://www.sofascore.com/api/v1/unique-tournament/1644/season/{seasonID}/events/round/{round}",
                                 impersonate="chrome")
        return response
    def transform(self, response):
        alldata = []
        games = json.loads(response.text)

        if len(games) >= 2:
            for game in games["events"]:
                matchstatus = game["status"]["type"]
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
                    #'homeScoreFT' : game["homeScore"]["normaltime"] if matchstatus == ("finished") else '-',
                    #'awayScoreFT' : game["awayScore"]["normaltime"] if matchstatus == ("finished") else '-',
                    }
                alldata.append(matchdata)
        return alldata
    
    def load(self, alldata, directory):
        df = pd.DataFrame(alldata)
        round_number = df['round'][1]

        folders = os.listdir('C:/MyProjects/WebScraping/Scrapy/KPL-Project/data/bySeasons')
        path = 'C:/MyProjects/WebScraping/Scrapy/KPL-Project/data/bySeasons'     

        filepath = f"{path}/{directory}/round{round_number}.csv"
        file_exists = True if os.path.isfile(filepath) else False

        if directory in folders:
            if file_exists is False:
                df.to_csv(f"{filepath}", index=False)
                print(f"Filename: ({directory}/round{round_number}) added!")
            else:
                print(f"Filename: ({directory}/round{round_number}) already exists!")
        else:
            print(f"Error: directory not found")

for seasonID in seasonIDs:
    directory = seasonIDs[seasonID]
    for round in range(1,33):
        roundsData = rounds(seasonID, directory,round)


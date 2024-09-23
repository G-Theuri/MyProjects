from curl_cffi import requests as cureq
import pandas as pd
import time, os, json

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
        data = []
        games = json.loads(response.text)

        if len(games) >= 2:
            for game in games["events"]:
                try:
                    homeScoreFT= game["homeScore"]["normaltime"]
                    awayScoreFT= game["homeScore"]["normaltime"]
                except KeyError:
                    homeScoreFT="-"
                    awayScoreFT="-"
                matchdata = {
                    "tournament" : game["tournament"]["uniqueTournament"]["name"],
                    "season" : game["season"]["year"],
                    "round" : game["roundInfo"]["round"],
                    "matchID" : game["id"],
                    "matchCustomID" : game["customId"],
                    "matchStatus" : game["status"]["type"].capitalize(), # finished, notstarted, postponed
                    "homeTeamnName" :game["homeTeam"]["name"],
                    "homeTeamnNameCode":game["homeTeam"]["nameCode"],
                    'homeTeamID' : game["homeTeam"]["id"],
                    "awayTeamName": game["awayTeam"]["name"],
                    'awayTeamNameCode': game["awayTeam"]["nameCode"],
                    'awayTeamID' : game["awayTeam"]["id"],
                    'homeScoreFT' : homeScoreFT,
                    'awayScoreFT' : awayScoreFT,
                    }
                data.append(matchdata)
        return data    
    
    def load(self, data, directory):
        df = pd.DataFrame(data)

        folders = os.listdir('C:/MyProjects/WebScraping/Scrapy/KPL-Project/data/bySeasons')
        filepath = f'C:/MyProjects/WebScraping/Scrapy/KPL-Project/data/bySeasons/{directory}/rounds.csv'   

        if directory in folders:
            with open(filepath, 'r+') as file:
                contents = file.read()
            if contents=='':
                df.to_csv(filepath, mode='a', index=False)
                print(f"Year {directory} Round {df['round'][1]} added!")
            else:
                if str(df['matchID'][1]) not in contents:
                    df.to_csv(filepath, mode='a', index=False, header=False)
                    print(f"Year {directory} Round {df['round'][1]} added!")
                else:
                    print(f"Year {directory} Round {df['round'][1]} already exist!")
        else:
            print(f"Error: directory not found") 

for seasonID in seasonIDs:
    directory = seasonIDs[seasonID]
    for round in range(1,3):
        roundsData = rounds(seasonID, directory,round)
        time.sleep(2)


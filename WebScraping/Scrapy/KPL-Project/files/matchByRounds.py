from curl_cffi import requests as cureq
import pandas as pd
import time, os, json
from time import strftime, localtime
import logging

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
                    starttime = game["startTimestamp"]
                except KeyError:
                    homeScoreFT="-"
                    awayScoreFT="-"
                    starttime =None

                matchdata = {
                    "Tournament" : game["tournament"]["uniqueTournament"]["name"],
                    "Season" : game["season"]["year"],
                    "Round" : game["roundInfo"]["round"],
                    "Date": strftime('%Y-%m-%d', localtime(starttime)), 
                    "StartTime": strftime('%H:%M:%S', localtime(starttime)),
                    "MatchID" : game["id"],
                    "MatchCustomID" : game["customId"],
                    "MatchStatus" : game["status"]["type"].capitalize(), # finished, notstarted, postponed
                    "HomeTeamnName" :game["homeTeam"]["name"],
                    "HomeTeamnNameCode":game["homeTeam"]["nameCode"],
                    "HomeTeamID" : game["homeTeam"]["id"],
                    "AwayTeamName": game["awayTeam"]["name"],
                    "AwayTeamNameCode": game["awayTeam"]["nameCode"],
                    "AwayTeamID" : game["awayTeam"]["id"],
                    "HomeScoreFT" : homeScoreFT,
                    "AwayScoreFT" : awayScoreFT,
                    }
                data.append(matchdata)

        return data
    
    def load(self, data, directory):
        df = pd.DataFrame(data)

        folders = os.listdir('C:/MyProjects/WebScraping/Scrapy/KPL-Project/data/bySeasons')
        filepath = f'C:/MyProjects/WebScraping/Scrapy/KPL-Project/data/bySeasons/{directory}/rounds.csv'   

        try:
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

        except:
            print(f"Year {directory} Round {self.round} Not Available!")
            pass

for seasonID in seasonIDs:
    directory = seasonIDs[seasonID]
    for round in range(1,3):
        roundsData = rounds(seasonID, directory,round)
        time.sleep(1)
    time.sleep(3)


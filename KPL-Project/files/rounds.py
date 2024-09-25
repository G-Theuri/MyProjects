from curl_cffi import requests as cureq
import pandas as pd
import time, os, json
from time import strftime, localtime
import logging

directories = os.listdir('C:/MyProjects/KPL-Project/data/Seasons')

seasonIDs = {7752:"2014", 9841:"2015", 11265:"2016", 12921:"2017", 15858:"2018", 19876:"2018-2019", 24023:"2019-2020",
             34876:"2020-2021", 38844:"2021-2022", 45686:"2022-2023", 53922:"2023-2024", 65071:"2024-2025"}
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
                    "StartTime": strftime('%H:%M', localtime(starttime)),
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

        folders = os.listdir('C:/MyProjects/KPL-Project/data/Seasons')
        filepath = f'C:/MyProjects/KPL-Project/data/Seasons/{directory}/rounds.csv'   

        try:
            if directory in folders:
                with open(filepath, 'r+') as file:
                    contents = file.read()
                if contents=='':
                    df.to_csv(filepath, mode='a', index=False)
                    print(f"Season {directory} Round {df['Round'][1]} added!")
                else:
                    if str(df['MatchID'][1]) not in contents:
                        df.to_csv(filepath, mode='a', index=False, header=False)
                        print(f"Season {directory} Round {df['Round'][1]} added!")
                    else:
                        print(f"Season {directory} Round {df['Round'][1]} already exist!")
            else:
                print(f"Error: directory not found")

        except:
            print(f"Season {directory} Round {self.round} Not Available!")
            pass

for seasonID in seasonIDs:
    directory = seasonIDs[seasonID]
    for round in range(1,2):
        roundsData = rounds(seasonID, directory,round)
        time.sleep(1)
    time.sleep(3)


from curl_cffi import requests as cureq
import pandas as pd
import time
import json
import os


seasonIDs = {7752:"2014", 9841:"2015", 11265:"2016", 12921:"2017", 15858:"2018", 19876:"2018-2019", 24023:"2019-2020",
             34876:"2020-2021", 38844:"2021-2022", 45686:"2022-2023", 53922:"2023-2024", 65071:"2024-2025"}


class table:

    def __init__(self, seasonID, directory):
        self.seasonID = seasonID
        self.directory = directory
        response = self.extract()
        data = self.transform(response)
        self.load(data, directory)

    def extract(self):
        response =  cureq.get(f"https://www.sofascore.com/api/v1/unique-tournament/1644/season/{seasonID}/standings/total",
                             impersonate="chrome")
        return response
    
    def transform(self, response):
        rows = json.loads(response.text)
        alldata = []

        for row in rows['standings'][0]['rows']:
            data= {
                "teamName": row['team']['name'],
                "nameCode": row['team']['nameCode'],
                "shortName": row['team']['shortName'],
                "teamID": row['team']['id'],
                "teamcolor": row['team']['teamColors']['primary'],
                "position": row['position'],
                "Played": row['matches'],
                "Won": row['wins'],
                "Drawn": row['draws'],
                "Lost": row['losses'],
                "GF": row['scoresFor'],
                "GA": row['scoresAgainst'],
                "Points": row['points'],

            }
            alldata.append(data)
        return alldata
    
    def load(self, alldata, directory):
        df = pd.DataFrame(alldata)

        folders = os.listdir('C:/MyProjects/WebScraping/Scrapy/KPL-Project/data/bySeasons')
        filepath = f'C:/MyProjects/WebScraping/Scrapy/KPL-Project/data/bySeasons/{directory}/table.csv'

        try:
            if directory in folders:
                df.to_csv(filepath, mode='w+', index=False)
                print(f"Season {directory} Standings Table added!")
            else:
                print(f"Error: directory not found")

        except:
            print(f"Season {directory} Standings Table Not Found!")
            pass
    

for seasonID in seasonIDs:
    directory = seasonIDs[seasonID]
    tabledata = table(seasonID, directory)
    time.sleep(2)

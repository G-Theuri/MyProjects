from curl_cffi import requests as cureq
import pandas as pd
import time
import json
import os

seasonIDs = {7752:"2014",}


class table:
    def __init__(self, seasonID, directory):
        self.seasonID = seasonID
        self.directory = directory
    def extract(self):
        response =  cureq.get(f"https://www.sofascore.com/api/v1/unique-tournament/1644/season/{seasonID}/standings/total",
                             impersonate="chrome")
        return response
    def transform(self, response):
        rows = json.loads(response.text)
        alldata = []

        for row in rows['rows']:
            data= {
                "teamName": row['team']['name'],
                "nameCode": row['team']['nameCode'],
                "shortName": row['team']['shortName'],
                "teamName": row['team']['id'],
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
            if direc

for seasonID in seasonIDs:
    pass

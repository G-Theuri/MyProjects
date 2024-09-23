from curl_cffi import requests as cureq
import pandas as pd
import time
import json
import os

seasonIDs = {7752:"2014", 9841:"2015", 11265:"2016", 12921:"2017", 15858:"2018", 19876:"2018-2019", 24023:"2019-2020",
             34876:"2020-2021", 38844:"2021-2022", 45686:"2022-2023", 53922:"2023-2024", 65071:"2024-2025"}


class table:
    def __init__(self, seasonID):
        self.seasonID = seasonID
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
    def load(self, alldata):
        pass

for seasonID in seasonIDs:
    pass

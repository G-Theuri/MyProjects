from curl_cffi import requests as cureq
import pandas as pd
import time
import json
import os


print(os.listdir('C:/MyProjects/WebScraping/Scrapy/KPL-Project/data/bySeasons'))
seasonIDs = {7752:"2014", 9841:"2015", 11265:"2016", 12921:"2017", 15858:"2018", 19876:"2018-2019", 24023:"2019-2020",
             34876:"2020-2021", 38844:"2021-2022", 45686:"2022-2023", 53922:"2023-2024", 65071:"2024-2025"}

class rounds:

    def __init__(self, seasonID):
        self.seasonID=seasonID
        round = [round for round in range (1,32)]
        response = self.extract(round)
        data = self.transform(response)
        self.load(data)

    def extract(self, round):
        response = cureq.get("f'https://www.sofascore.com/api/v1/unique-tournament/1644/season/{seasonID}/events/round/{round}'",
                                  impersonate="chrome")
        return response
    def transform(self):
        pass
    def load(self):
        pass

for seasonID in seasonIDs:
    roundsData = rounds(seasonID)


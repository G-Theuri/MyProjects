from curl_cffi import requests as cureq
import pandas as pd
import time

seasonIDs = {7752:"2014", 9841:"2015", 11265:"2016", 12921:"2017", 15858:"2018", 19876:"2018/2019", 24023:"2019/2020",
             34876:"2020/2021", 38844:"2021/2022", 45686:"2022/2023", 53922:"2023/2024", 65071:"2024/2025"}
#response = cureq.get("https://www.sofascore.com/api/v1/unique-tournament/1644/season/19876/rounds", impersonate="chrome")
for key in seasonIDs:
    print("Season", seasonIDs[key])

class matches:
    def by_rounds(self):
        pass
    def by_date(self):
        pass
    
class standings:
    def table(self):
        pass
#use a for loop on these classes to link extracted data from both classes into a single folder
#try and use extract>>transform>>load in the functions

from curl_cffi import requests as cureq
import json
import pandas as pd

response = cureq.get('https://www.sofascore.com/api/v1/unique-tournament/1644/season/19876/rounds')
data = json.loads(response.text)
count =0
for round in data['rounds']:
    if len(round) == 1:
        count += 1
print(count)
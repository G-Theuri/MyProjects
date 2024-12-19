import requests
from bs4 import BeautifulSoup
import pandas as pd

header = {
    #"cookie":'',
    "authority": 'site.web.api.espn.com',
    "sec-ch-ua":'"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "user-agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',    
}

url = 'https://www.espn.com/soccer/table/_/league/ken.1'
data = requests.get(url, headers=header).text


soup = BeautifulSoup(data, 'html.parser')
